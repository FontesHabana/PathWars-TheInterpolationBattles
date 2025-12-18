"""
Base mercenary classes for PathWars - The Interpolation Battles.

This module defines the abstract base class for mercenary units and their stats.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MercenaryStats:
    """Stats for a mercenary unit."""
    base_hp: int
    base_speed: float
    cost: int
    display_name: str
    
    def get_modified_hp(self, hp_modifier: float = 1.0) -> int:
        """Calculate HP with modifier."""
        return int(self.base_hp * hp_modifier)
    
    def get_modified_speed(self, speed_modifier: float = 1.0) -> float:
        """Calculate speed with modifier."""
        return self.base_speed * speed_modifier


class BaseMercenary(ABC):
    """Abstract base class for mercenary units."""
    
    def __init__(self, owner_player_id: str, target_player_id: str) -> None:
        self._owner_id = owner_player_id
        self._target_id = target_player_id
        self._position: Tuple[float, float] = (0.0, 0.0)
        self._hp: int = self.stats.get_modified_hp(self.hp_modifier)
        self._speed: float = self.stats.get_modified_speed(self.speed_modifier)
        self._is_alive: bool = True
    
    @property
    @abstractmethod
    def stats(self) -> MercenaryStats:
        """Return base stats for this mercenary type."""
        ...
    
    @property
    @abstractmethod
    def hp_modifier(self) -> float:
        """Return HP modifier for this mercenary type."""
        ...
    
    @property
    @abstractmethod
    def speed_modifier(self) -> float:
        """Return speed modifier for this mercenary type."""
        ...
    
    @property
    def owner_player_id(self) -> str:
        return self._owner_id
    
    @property
    def target_player_id(self) -> str:
        return self._target_id
    
    @property
    def hp(self) -> int:
        return self._hp
    
    @property
    def speed(self) -> float:
        return self._speed
    
    @property
    def is_alive(self) -> bool:
        return self._is_alive
    
    @property
    def position(self) -> Tuple[float, float]:
        return self._position
    
    def take_damage(self, amount: int) -> None:
        """Receive damage."""
        self._hp = max(0, self._hp - amount)
        if self._hp <= 0:
            self._is_alive = False
    
    def move(self, dx: float, dy: float) -> None:
        """Move by delta."""
        x, y = self._position
        self._position = (x + dx, y + dy)
    
    def set_position(self, x: float, y: float) -> None:
        """Set absolute position."""
        self._position = (x, y)
