"""
Tower entity classes for PathWars - The Interpolation Battles.

This module defines the Tower class and tower types that defend against
enemies by attacking them as they pass.
"""

from enum import Enum, auto
from typing import List, Optional

from entities.base import Entity, EntityState, EntityType, Vector2


class TowerType(Enum):
    """Enumeration of tower types in the game."""
    DEAN = auto()        # Tank/Blocker - high HP, low damage
    CALCULUS = auto()    # Ranged - fast attack, medium damage
    PHYSICS = auto()     # Cannon/AoE - slow attack, high damage
    STATISTICS = auto()  # Support/Slow - debuff, no damage


class Tower(Entity):
    """
    A tower entity that attacks enemies within range.

    Towers are stationary entities that target and attack enemies that come
    within their attack range.

    Attributes:
        tower_type: The specific type of tower.
        damage: Damage dealt per attack.
        attack_range: Maximum distance to attack enemies.
        cooldown: Time between attacks in seconds.
        cooldown_remaining: Time until next attack is ready.
    """

    # Default stats by tower type
    _TOWER_STATS = {
        TowerType.DEAN: {
            "damage": 10,
            "attack_range": 2.0,
            "cooldown": 1.5,
        },
        TowerType.CALCULUS: {
            "damage": 25,
            "attack_range": 5.0,
            "cooldown": 0.5,
        },
        TowerType.PHYSICS: {
            "damage": 50,
            "attack_range": 4.0,
            "cooldown": 2.0,
        },
        TowerType.STATISTICS: {
            "damage": 0,
            "attack_range": 3.5,
            "cooldown": 1.0,
        },
    }

    def __init__(
        self,
        position: Vector2,
        tower_type: TowerType,
        damage: Optional[int] = None,
        attack_range: Optional[float] = None,
        cooldown: Optional[float] = None,
    ) -> None:
        """
        Initialize a new Tower.

        Args:
            position: Position of the tower.
            tower_type: The type of tower to create.
            damage: Override default damage for this tower type.
            attack_range: Override default range for this tower type.
            cooldown: Override default cooldown for this tower type.
        """
        super().__init__(position, EntityType.TOWER)

        self._tower_type = tower_type
        stats = self._TOWER_STATS[tower_type]

        self._damage: int = damage if damage is not None else stats["damage"]
        self._attack_range: float = (
            attack_range if attack_range is not None else stats["attack_range"]
        )
        self._cooldown: float = cooldown if cooldown is not None else stats["cooldown"]
        self._cooldown_remaining: float = 0.0
        self._current_target: Optional["Enemy"] = None

        self.state = EntityState.ACTIVE

    @property
    def tower_type(self) -> TowerType:
        """Get the type of tower."""
        return self._tower_type

    @property
    def damage(self) -> int:
        """Get damage per attack."""
        return self._damage

    @property
    def attack_range(self) -> float:
        """Get attack range."""
        return self._attack_range

    @property
    def cooldown(self) -> float:
        """Get attack cooldown in seconds."""
        return self._cooldown

    @property
    def cooldown_remaining(self) -> float:
        """Get remaining cooldown time."""
        return self._cooldown_remaining

    @property
    def can_attack(self) -> bool:
        """Check if the tower is ready to attack."""
        return self._cooldown_remaining <= 0

    def cooldown_check(self, dt: float) -> bool:
        """
        Update the cooldown timer and check if ready to attack.

        Args:
            dt: Delta time since last update in seconds.

        Returns:
            True if the tower is ready to attack, False otherwise.
        """
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= dt
            self._cooldown_remaining = max(0, self._cooldown_remaining)
        return self.can_attack

    def is_in_range(self, target_position: Vector2) -> bool:
        """
        Check if a target position is within attack range.

        Args:
            target_position: Position to check.

        Returns:
            True if target is in range, False otherwise.
        """
        distance = self.position.distance_to(target_position)
        return distance <= self._attack_range

    def find_target(self, enemies: List) -> Optional["Enemy"]:
        """
        Find the best target from a list of enemies.

        Targeting priority: closest enemy that is in range and alive.

        Args:
            enemies: List of Enemy objects to consider.

        Returns:
            The best target Enemy, or None if no valid targets.
        """
        # Import here to avoid circular import
        from entities.enemy import Enemy

        valid_targets: List[tuple] = []

        for enemy in enemies:
            if not isinstance(enemy, Enemy):
                continue
            if enemy.state == EntityState.DEAD:
                continue
            if not self.is_in_range(enemy.position):
                continue

            distance = self.position.distance_to(enemy.position)
            valid_targets.append((distance, enemy))

        if not valid_targets:
            return None

        # Sort by distance and return the closest
        valid_targets.sort(key=lambda x: x[0])
        return valid_targets[0][1]

    def attack(self, target) -> int:
        """
        Attack a target enemy.

        Args:
            target: The Enemy to attack.

        Returns:
            The damage dealt.
        """
        if not self.can_attack:
            return 0

        # Reset cooldown
        self._cooldown_remaining = self._cooldown

        # Deal damage
        target.take_damage(self._damage)
        return self._damage

    def update(self, dt: float) -> None:
        """
        Update tower state and cooldown.

        Args:
            dt: Delta time since last update in seconds.
        """
        self.cooldown_check(dt)
