"""
Mercenary type definitions for PathWars - The Interpolation Battles.

This module defines the concrete mercenary classes and their types.
"""

from enum import Enum, auto

from entities.mercenaries.base_mercenary import BaseMercenary, MercenaryStats


class MercenaryType(Enum):
    """Enumeration of available mercenary types."""
    REINFORCED_STUDENT = auto()
    SPEEDY_VARIABLE_X = auto()
    TANK_CONSTANT_PI = auto()


class ReinforcedStudent(BaseMercenary):
    """Reinforced Student: +50% HP, normal speed, cost 100$."""
    
    _stats = MercenaryStats(
        base_hp=100,
        base_speed=1.0,
        cost=100,
        display_name="Reinforced Student"
    )
    
    @property
    def stats(self) -> MercenaryStats:
        return self._stats
    
    @property
    def hp_modifier(self) -> float:
        return 1.5
    
    @property
    def speed_modifier(self) -> float:
        return 1.0


class SpeedyVariableX(BaseMercenary):
    """Speedy Variable X: -30% HP, +100% speed, cost 75$."""
    
    _stats = MercenaryStats(
        base_hp=100,
        base_speed=1.0,
        cost=75,
        display_name="Speedy Variable X"
    )
    
    @property
    def stats(self) -> MercenaryStats:
        return self._stats
    
    @property
    def hp_modifier(self) -> float:
        return 0.7
    
    @property
    def speed_modifier(self) -> float:
        return 2.0


class TankConstantPi(BaseMercenary):
    """Tank Constant Pi: +200% HP, -50% speed, cost 200$."""
    
    _stats = MercenaryStats(
        base_hp=100,
        base_speed=1.0,
        cost=200,
        display_name="Tank Constant Pi"
    )
    
    @property
    def stats(self) -> MercenaryStats:
        return self._stats
    
    @property
    def hp_modifier(self) -> float:
        return 3.0
    
    @property
    def speed_modifier(self) -> float:
        return 0.5
