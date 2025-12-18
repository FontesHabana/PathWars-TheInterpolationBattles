"""
Tower entity classes for PathWars - The Interpolation Battles.

This module defines the Tower class and tower types that defend against
enemies by attacking them as they pass.
"""

import uuid
from enum import Enum, auto
from typing import Dict, List, Optional

from entities.base import Entity, EntityState, EntityType, Vector2


class TowerType(Enum):
    """Enumeration of tower types in the game."""
    DEAN = auto()        # Tank/Blocker - high HP, low damage
    CALCULUS = auto()    # Ranged - fast attack, medium damage
    PHYSICS = auto()     # Cannon/AoE - slow attack, high damage
    STATISTICS = auto()  # Support/Slow - debuff, no damage


class TowerLevel(Enum):
    """Enumeration of tower upgrade levels."""
    MASTERY = 1      # Base level (Grado de Maestría)
    DOCTORATE = 2    # Upgraded level (Doctorado)


class TowerUpgradeError(Exception):
    """Raised when a tower upgrade fails."""
    pass


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
        level: Current upgrade level (MASTERY or DOCTORATE).
        id: Unique identifier for this tower.
    """

    # Default stats by tower type
    _TOWER_STATS = {
        TowerType.DEAN: {
            "damage": 10,
            "attack_range": 2.0,
            "cooldown": 1.5,
            "stun_duration": 1.0,
            "splash_radius": 0.0,
            "slow_amount": 0.0,
        },
        TowerType.CALCULUS: {
            "damage": 25,
            "attack_range": 5.0,
            "cooldown": 0.5,
            "stun_duration": 0.0,
            "splash_radius": 0.0,
            "slow_amount": 0.0,
        },
        TowerType.PHYSICS: {
            "damage": 50,
            "attack_range": 4.0,
            "cooldown": 2.0,
            "stun_duration": 0.0,
            "splash_radius": 2.0,
            "slow_amount": 0.0,
        },
        TowerType.STATISTICS: {
            "damage": 0,
            "attack_range": 3.5,
            "cooldown": 1.0,
            "stun_duration": 0.0,
            "splash_radius": 0.0,
            "slow_amount": 0.5,
            "slow_duration": 2.0,
        },
    }

    # Upgrade multipliers for each stat
    _UPGRADE_MULTIPLIERS = {
        "damage": 1.5,           # +50% damage
        "attack_range": 1.25,    # +25% range
        "cooldown": 0.8,         # -20% cooldown (faster attacks)
        "stun_duration": 1.5,    # +50% stun duration
        "splash_radius": 1.3,    # +30% splash radius
        "slow_amount": 1.25,     # +25% slow effect
        "slow_duration": 1.5,    # +50% slow duration
    }

    # Upgrade costs by tower type
    _UPGRADE_COSTS = {
        TowerType.DEAN: 75,       # Base cost $50, upgrade $75
        TowerType.CALCULUS: 100,  # Base cost $75, upgrade $100
        TowerType.PHYSICS: 150,   # Base cost $100, upgrade $150
        TowerType.STATISTICS: 90, # Base cost $60, upgrade $90
    }

    def __init__(
        self,
        position: Vector2,
        tower_type: TowerType,
        damage: Optional[int] = None,
        attack_range: Optional[float] = None,
        cooldown: Optional[float] = None,
        level: TowerLevel = TowerLevel.MASTERY,
    ) -> None:
        """
        Initialize a new Tower.

        Args:
            position: Position of the tower.
            tower_type: The type of tower to create.
            damage: Override default damage for this tower type.
            attack_range: Override default range for this tower type.
            cooldown: Override default cooldown for this tower type.
            level: Initial tower level (default: MASTERY).
        """
        super().__init__(position, EntityType.TOWER)

        self._id: str = str(uuid.uuid4())
        self._tower_type = tower_type
        self._level: TowerLevel = TowerLevel.MASTERY
        stats = self._TOWER_STATS[tower_type]

        # Store base stats (before any upgrades)
        self._base_damage: int = damage if damage is not None else stats["damage"]
        self._base_attack_range: float = (
            attack_range if attack_range is not None else stats["attack_range"]
        )
        self._base_cooldown: float = cooldown if cooldown is not None else stats["cooldown"]
        self._base_stun_duration: float = stats.get("stun_duration", 0.0)
        self._base_splash_radius: float = stats.get("splash_radius", 0.0)
        self._base_slow_amount: float = stats.get("slow_amount", 0.0)
        self._base_slow_duration: float = stats.get("slow_duration", 0.0)

        # Set current stats to base stats
        self._damage: int = self._base_damage
        self._attack_range: float = self._base_attack_range
        self._cooldown: float = self._base_cooldown
        self._cooldown_remaining: float = 0.0
        self._current_target: Optional["Enemy"] = None

        # Special effect stats
        self._stun_duration: float = self._base_stun_duration
        self._splash_radius: float = self._base_splash_radius
        self._slow_amount: float = self._base_slow_amount
        self._slow_duration: float = self._base_slow_duration

        self.state = EntityState.ACTIVE

        # If initialized at DOCTORATE level, apply upgrade multipliers
        if level == TowerLevel.DOCTORATE:
            self._level = TowerLevel.DOCTORATE
            self._apply_upgrade_multipliers()

    @property
    def tower_type(self) -> TowerType:
        """Get the type of tower."""
        return self._tower_type

    @property
    def level(self) -> TowerLevel:
        """Get the current upgrade level."""
        return self._level

    @property
    def id(self) -> str:
        """Get the unique identifier of this tower."""
        return self._id

    @property
    def upgrade_cost(self) -> int:
        """
        Get the cost to upgrade this tower.
        
        Returns:
            Cost in money to upgrade, or 0 if already at max level.
        """
        if self._level == TowerLevel.DOCTORATE:
            return 0
        return self._UPGRADE_COSTS[self._tower_type]

    @property
    def can_upgrade(self) -> bool:
        """
        Check if this tower can be upgraded.
        
        Returns:
            True if tower is at MASTERY level, False if at DOCTORATE.
        """
        return self._level == TowerLevel.MASTERY

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
    def stun_duration(self) -> float:
        """Get stun duration in seconds."""
        return self._stun_duration

    @property
    def splash_radius(self) -> float:
        """Get splash/AoE radius."""
        return self._splash_radius

    @property
    def slow_amount(self) -> float:
        """Get slow effect amount (0.0 to 1.0)."""
        return self._slow_amount

    @property
    def slow_duration(self) -> float:
        """Get slow effect duration in seconds."""
        return self._slow_duration

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

    def _apply_upgrade_multipliers(self) -> None:
        """
        Apply upgrade multipliers to tower stats.
        
        This is called internally when upgrading a tower to DOCTORATE level.
        """
        self._damage = int(self._base_damage * self._UPGRADE_MULTIPLIERS["damage"])
        self._attack_range = self._base_attack_range * self._UPGRADE_MULTIPLIERS["attack_range"]
        self._cooldown = self._base_cooldown * self._UPGRADE_MULTIPLIERS["cooldown"]
        self._stun_duration = self._base_stun_duration * self._UPGRADE_MULTIPLIERS["stun_duration"]
        self._splash_radius = self._base_splash_radius * self._UPGRADE_MULTIPLIERS["splash_radius"]
        
        # Slow amount is capped at 1.0 (100% slow = complete stop)
        self._slow_amount = min(
            1.0, 
            self._base_slow_amount * self._UPGRADE_MULTIPLIERS["slow_amount"]
        )
        self._slow_duration = self._base_slow_duration * self._UPGRADE_MULTIPLIERS["slow_duration"]

    def upgrade(self) -> bool:
        """
        Upgrade this tower to DOCTORATE level.
        
        Returns:
            True if upgrade was successful, False if already at max level.
        """
        if not self.can_upgrade:
            return False
        
        self._level = TowerLevel.DOCTORATE
        self._apply_upgrade_multipliers()
        return True

    def get_upgrade_preview(self) -> Dict[str, Dict[str, float]]:
        """
        Get a preview of stats after upgrading.
        
        Returns:
            Dictionary with 'current' and 'upgraded' stat dictionaries.
            Empty if already at max level.
        """
        if not self.can_upgrade:
            return {}
        
        current_stats = {
            "damage": self._damage,
            "attack_range": self._attack_range,
            "cooldown": self._cooldown,
            "stun_duration": self._stun_duration,
            "splash_radius": self._splash_radius,
            "slow_amount": self._slow_amount,
            "slow_duration": self._slow_duration,
        }
        
        upgraded_stats = {
            "damage": int(self._base_damage * self._UPGRADE_MULTIPLIERS["damage"]),
            "attack_range": self._base_attack_range * self._UPGRADE_MULTIPLIERS["attack_range"],
            "cooldown": self._base_cooldown * self._UPGRADE_MULTIPLIERS["cooldown"],
            "stun_duration": self._base_stun_duration * self._UPGRADE_MULTIPLIERS["stun_duration"],
            "splash_radius": self._base_splash_radius * self._UPGRADE_MULTIPLIERS["splash_radius"],
            "slow_amount": min(1.0, self._base_slow_amount * self._UPGRADE_MULTIPLIERS["slow_amount"]),
            "slow_duration": self._base_slow_duration * self._UPGRADE_MULTIPLIERS["slow_duration"],
        }
        
        return {
            "current": current_stats,
            "upgraded": upgraded_stats,
        }

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

    def attack(self, target, all_enemies: Optional[List] = None) -> int:
        """
        Attack a target enemy, applying tower-specific effects.

        Args:
            target: The Enemy to attack.
            all_enemies: Optional list of all enemies for AoE attacks.

        Returns:
            The damage dealt to the primary target.
        """
        from core.effects import EffectType, StatusEffect

        if not self.can_attack:
            return 0

        # Reset cooldown
        self._cooldown_remaining = self._cooldown

        # Deal damage to primary target
        target.take_damage(self._damage)

        # Apply tower-specific effects
        if self._tower_type == TowerType.DEAN and self._stun_duration > 0:
            # DEAN: Apply stun effect
            stun_effect = StatusEffect(EffectType.STUN, self._stun_duration)
            target.apply_effect(stun_effect)

        elif self._tower_type == TowerType.PHYSICS and self._splash_radius > 0:
            # PHYSICS: AoE damage to nearby enemies
            if all_enemies:
                for enemy in all_enemies:
                    if enemy is target:
                        continue
                    if enemy.state == EntityState.DEAD:
                        continue
                    distance = target.position.distance_to(enemy.position)
                    if distance <= self._splash_radius:
                        enemy.take_damage(self._damage)

        elif self._tower_type == TowerType.STATISTICS and self._slow_amount > 0:
            # STATISTICS: Apply slow effect
            slow_effect = StatusEffect(
                EffectType.SLOW, self._slow_duration, self._slow_amount
            )
            target.apply_effect(slow_effect)

        return self._damage

    def update(self, dt: float) -> None:
        """
        Update tower state and cooldown.

        Args:
            dt: Delta time since last update in seconds.
        """
        self.cooldown_check(dt)
