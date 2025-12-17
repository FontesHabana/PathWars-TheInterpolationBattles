"""
Combat Manager module for PathWars - The Interpolation Battles.

Handles the combat loop where towers attack enemies, enemies take damage,
and reaching the base deducts player lives. Uses Observer pattern for events.
"""

from typing import Callable, Dict, List, Optional, Tuple

from core.game_state import GameState
from entities.base import EntityState
from entities.enemy import Enemy, EnemyType
from entities.tower import Tower


# Money rewards per enemy type
ENEMY_REWARDS: Dict[EnemyType, int] = {
    EnemyType.STUDENT: 10,
    EnemyType.VARIABLE_X: 15,
}


class CombatManager:
    """
    Manages the combat loop for the tower defense game.

    Coordinates tower attacks on enemies, processes enemy deaths,
    and handles base damage when enemies reach the end of their path.
    Uses the Observer pattern to notify listeners of important events.

    Attributes:
        active_attacks: List of (tower, enemy) pairs representing current attacks
                       for visualization purposes.
    """

    def __init__(self) -> None:
        """Initialize the CombatManager."""
        self._enemy_killed_callbacks: List[Callable[[Enemy, int], None]] = []
        self._base_damaged_callbacks: List[Callable[[Enemy], None]] = []
        self._active_attacks: List[Tuple[Tower, Enemy]] = []

    @property
    def active_attacks(self) -> List[Tuple[Tower, Enemy]]:
        """
        Get the list of active attacks for visualization.

        Returns:
            List of (tower, enemy) tuples representing attacks this frame.
        """
        return self._active_attacks

    def on_enemy_killed(self, callback: Callable[[Enemy, int], None]) -> None:
        """
        Register a callback for when an enemy is killed.

        Args:
            callback: Function to call with (enemy, reward) when enemy dies.
        """
        self._enemy_killed_callbacks.append(callback)

    def on_base_damaged(self, callback: Callable[[Enemy], None]) -> None:
        """
        Register a callback for when the base is damaged.

        Args:
            callback: Function to call with (enemy) when an enemy reaches the base.
        """
        self._base_damaged_callbacks.append(callback)

    def _notify_enemy_killed(self, enemy: Enemy, reward: int) -> None:
        """
        Notify all registered observers of an enemy death.

        Args:
            enemy: The enemy that was killed.
            reward: Money reward for the kill.
        """
        for callback in self._enemy_killed_callbacks:
            callback(enemy, reward)

    def _notify_base_damaged(self, enemy: Enemy) -> None:
        """
        Notify all registered observers of base damage.

        Args:
            enemy: The enemy that reached the base.
        """
        for callback in self._base_damaged_callbacks:
            callback(enemy)

    def _get_reward(self, enemy: Enemy) -> int:
        """
        Get the money reward for killing an enemy.

        Args:
            enemy: The enemy to get reward for.

        Returns:
            Money reward amount.
        """
        return ENEMY_REWARDS.get(enemy.enemy_type, 10)

    def update(self, dt: float, game_state: GameState) -> None:
        """
        Update the combat state for one frame.

        Processes tower attacks, enemy deaths, and base damage.

        Args:
            dt: Delta time since last update in seconds.
            game_state: The current game state.
        """
        # Clear active attacks from previous frame
        self._active_attacks = []

        # Get entities from game state
        entities = game_state.entities_collection
        towers = entities.get('towers', [])
        enemies = entities.get('enemies', [])

        # Process tower attacks
        for tower in towers:
            if not isinstance(tower, Tower):
                continue

            # Update tower cooldown
            tower.cooldown_check(dt)

            # Skip if tower cannot attack
            if not tower.can_attack:
                continue

            # Find target
            target = tower.find_target(enemies)
            if target is None:
                continue

            # Attack target
            tower.attack(target)

            # Record attack for visualization
            self._active_attacks.append((tower, target))

        # Process enemies that have reached the end or died
        enemies_to_remove: List[Enemy] = []
        for enemy in enemies:
            if not isinstance(enemy, Enemy):
                continue

            # Check if enemy reached end of path
            if enemy.has_reached_end and enemy.state != EntityState.DEAD:
                # Mark as dead so wave completion logic works
                enemy.state = EntityState.DEAD
                self._notify_base_damaged(enemy)
                enemies_to_remove.append(enemy)
                continue

            # Check if enemy died from damage
            if enemy.state == EntityState.DEAD:
                reward = self._get_reward(enemy)
                self._notify_enemy_killed(enemy, reward)
                enemies_to_remove.append(enemy)

        # Remove dead/reached enemies from game state
        for enemy in enemies_to_remove:
            game_state.remove_entity('enemies', enemy)
