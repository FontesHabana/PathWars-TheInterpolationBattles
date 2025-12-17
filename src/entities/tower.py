"""
Tower entity implementation.

Towers are stationary defensive structures that attack enemies within range.
"""

from typing import List, Optional
from enum import Enum
from .base import Entity, Vector2
from .enemy import Enemy


class TowerType(Enum):
    """Types of towers in the game."""
    DECANO = "decano"  # Tank/Blocking tower
    CALCULO = "calculo"  # Ranged attack tower
    FISICA = "fisica"  # AoE/Cannon tower
    ESTADISTICA = "estadistica"  # Support/Slow tower


class Tower(Entity):
    """
    Tower entity that attacks enemies within range.
    
    Towers are stationary defensive structures placed by the player.
    They automatically target and attack enemies that come within range.
    
    Attributes:
        tower_type: The type of tower (affects stats and behavior).
        range: Attack range in units.
        damage: Damage dealt per attack.
        attack_speed: Attacks per second.
        cooldown: Time until next attack is ready.
        target: Currently targeted enemy (if any).
        level: Tower upgrade level.
        cost: Gold cost to build this tower.
    """
    
    # Level scaling constants
    DAMAGE_SCALE_FACTOR = 0.3  # +30% damage per level
    RANGE_SCALE_FACTOR = 0.1   # +10% range per level
    
    def __init__(
        self,
        position: Vector2,
        tower_type: TowerType = TowerType.CALCULO,
        level: int = 1
    ):
        """
        Initialize a Tower.
        
        Args:
            position: Position where the tower is placed.
            tower_type: Type of tower determining its characteristics.
            level: Initial level (1 = basic, higher = upgraded).
        """
        super().__init__(position)
        self.tower_type = tower_type
        self.level = level
        self.cooldown = 0.0
        self.target: Optional[Enemy] = None
        
        # Base stats - will be modified by type and level
        self.range = 100.0
        self.damage = 20.0
        self.attack_speed = 1.0  # Attacks per second
        self.cost = 100
        
        # Apply type-specific stats
        self._apply_type_stats()
        
        # Store base stats for upgrade calculations
        self._base_damage = self.damage
        self._base_range = self.range
        
        # Apply level scaling
        self._apply_level_scaling()
    
    def _apply_type_stats(self) -> None:
        """Apply type-specific statistics."""
        if self.tower_type == TowerType.DECANO:
            # Tank/Blocking - High HP, low damage, short range
            self.range = 80.0
            self.damage = 10.0
            self.attack_speed = 0.5
            self.cost = 150
            
        elif self.tower_type == TowerType.CALCULO:
            # Ranged - Medium everything, good general purpose
            self.range = 120.0
            self.damage = 20.0
            self.attack_speed = 1.0
            self.cost = 100
            
        elif self.tower_type == TowerType.FISICA:
            # AoE/Cannon - High damage, slow attack, long range
            self.range = 140.0
            self.damage = 50.0
            self.attack_speed = 0.4
            self.cost = 200
            
        elif self.tower_type == TowerType.ESTADISTICA:
            # Support/Slow - Low damage, affects multiple enemies
            self.range = 100.0
            self.damage = 5.0
            self.attack_speed = 0.8
            self.cost = 120
    
    def _apply_level_scaling(self) -> None:
        """Apply level-based stat increases to base stats."""
        if self.level > 1:
            damage_scale = 1.0 + (self.level - 1) * self.DAMAGE_SCALE_FACTOR
            range_scale = 1.0 + (self.level - 1) * self.RANGE_SCALE_FACTOR
            self.damage = self._base_damage * damage_scale
            self.range = self._base_range * range_scale
    
    def update(self, dt: float) -> None:
        """
        Update tower state and cooldown.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
            if self.cooldown < 0:
                self.cooldown = 0
    
    def find_target(self, enemies: List[Enemy]) -> Optional[Enemy]:
        """
        Find the best enemy to target.
        
        Prioritizes enemies that are:
        1. Alive
        2. Within range
        3. Furthest along the path (closest to end)
        
        Args:
            enemies: List of all enemies to consider.
            
        Returns:
            The enemy to target, or None if no valid target.
        """
        valid_targets = []
        
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            
            distance = self.position.distance_to(enemy.position)
            if distance <= self.range:
                valid_targets.append(enemy)
        
        if not valid_targets:
            return None
        
        # Target the enemy furthest along the path
        self.target = max(valid_targets, key=lambda e: e.get_progress())
        return self.target
    
    def can_attack(self) -> bool:
        """
        Check if the tower is ready to attack.
        
        Returns:
            True if cooldown has finished, False otherwise.
        """
        return self.cooldown <= 0
    
    def attack(self, target: Optional[Enemy] = None) -> bool:
        """
        Attempt to attack a target.
        
        Args:
            target: The enemy to attack. If None, uses current target.
            
        Returns:
            True if attack was performed, False otherwise.
        """
        if not self.can_attack():
            return False
        
        if target is None:
            target = self.target
        
        if target is None or not target.is_alive():
            return False
        
        # Check if target is still in range
        distance = self.position.distance_to(target.position)
        if distance > self.range:
            self.target = None
            return False
        
        # Perform attack
        target.take_damage(self.damage)
        
        # Set cooldown
        self.cooldown = 1.0 / self.attack_speed
        
        return True
    
    def upgrade(self) -> None:
        """Upgrade the tower to the next level."""
        self.level += 1
        self._apply_level_scaling()
    
    def get_upgrade_cost(self) -> int:
        """
        Get the cost to upgrade to the next level.
        
        Returns:
            Gold cost for the next upgrade.
        """
        return int(self.cost * 0.6 * self.level)
