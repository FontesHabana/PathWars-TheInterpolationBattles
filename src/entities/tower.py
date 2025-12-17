"""
Tower entity logic for the game.

This module defines tower behavior including targeting and attacking enemies.
"""

from enum import Enum
from typing import List, Optional
from .base import Entity, Vector2
from .enemy import Enemy


class TowerType(Enum):
    """Types of towers in the game."""
    DEAN = "dean"           # Tank/Blocker - high health, low damage
    CALCULUS = "calculus"   # Ranged - fast fire rate, medium damage
    PHYSICS = "physics"     # Cannon/AoE - slow fire rate, high damage, area effect
    STATISTICS = "statistics"  # Support - no damage, slows enemies


class TowerState(Enum):
    """Possible states for a tower."""
    IDLE = "idle"
    ATTACKING = "attacking"
    COOLDOWN = "cooldown"


class Tower(Entity):
    """
    Tower entity that attacks enemies within range.

    Attributes:
        tower_type: Type of the tower
        damage: Damage dealt per attack
        range: Attack range in units
        cooldown: Time between attacks in seconds
        cooldown_timer: Current cooldown timer
        state: Current state of the tower
        target: Current target enemy
    """

    def __init__(
        self,
        position: Vector2,
        tower_type: TowerType,
        damage: float = 20.0,
        attack_range: float = 100.0,
        cooldown: float = 1.0
    ):
        """
        Initialize a tower.

        Args:
            position: Tower position on the map
            tower_type: Type of the tower
            damage: Damage dealt per attack
            attack_range: Maximum attack range
            cooldown: Time between attacks in seconds
        """
        super().__init__(position)
        self.tower_type = tower_type
        self.damage = damage
        self.range = attack_range
        self.cooldown = cooldown
        self.cooldown_timer = 0.0
        self.state = TowerState.IDLE
        self.target: Optional[Enemy] = None

    def update(self, dt: float) -> None:
        """
        Update tower state and cooldown.

        Args:
            dt: Delta time since last update in seconds
        """
        # Update cooldown timer
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.cooldown_timer = 0
                self.state = TowerState.IDLE

    def find_target(self, enemies: List[Enemy]) -> Optional[Enemy]:
        """
        Find the best target among available enemies.

        Strategy: Target the enemy closest to the end of their path
        (highest path progress) that is within range.

        Args:
            enemies: List of enemy entities

        Returns:
            Best target enemy or None if no valid target
        """
        valid_targets = []

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            # Calculate distance to enemy
            distance = self.position.distance_to(enemy.position)

            if distance <= self.range:
                # Enemy is in range
                valid_targets.append((enemy, enemy.path_index))

        if not valid_targets:
            self.target = None
            return None

        # Sort by path progress (descending) and select the one closest to end
        valid_targets.sort(key=lambda x: x[1], reverse=True)
        self.target = valid_targets[0][0]
        return self.target

    def can_attack(self) -> bool:
        """
        Check if the tower can attack (cooldown is ready).

        Returns:
            True if can attack, False otherwise
        """
        return self.cooldown_timer <= 0

    def attack(self, target: Enemy) -> bool:
        """
        Attack a target enemy if cooldown allows.

        Args:
            target: Enemy to attack

        Returns:
            True if attack was successful, False if on cooldown or target invalid
        """
        if not self.can_attack():
            return False

        if not target.is_alive():
            return False

        # Check if target is still in range
        distance = self.position.distance_to(target.position)
        if distance > self.range:
            return False

        # Apply damage
        killed = target.take_damage(self.damage)

        # Start cooldown
        self.cooldown_timer = self.cooldown
        self.state = TowerState.ATTACKING if killed else TowerState.COOLDOWN

        return True

    def get_cooldown_progress(self) -> float:
        """
        Get the cooldown progress as a percentage.

        Returns:
            Value between 0.0 (ready) and 1.0 (just attacked)
        """
        if self.cooldown <= 0:
            return 0.0
        return min(1.0, self.cooldown_timer / self.cooldown)
