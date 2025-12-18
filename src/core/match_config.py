"""
Match Configuration Module.

Provides data structures for configuring multiplayer matches,
including difficulty, game speed, map size, and wave counts.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any


class Difficulty(Enum):
    """Difficulty levels for the game."""
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    
    def enemy_hp_multiplier(self) -> float:
        """
        Return HP multiplier for enemies based on difficulty.
        
        Returns:
            HP multiplier (0.75 for Easy, 1.0 for Normal, 1.5 for Hard).
        """
        return {
            self.EASY: 0.75,
            self.NORMAL: 1.0,
            self.HARD: 1.5
        }[self]
    
    def starting_money_bonus(self) -> int:
        """
        Return bonus starting money based on difficulty.
        
        Returns:
            Money bonus (200 for Easy, 0 for Normal, -100 for Hard).
        """
        return {
            self.EASY: 200,
            self.NORMAL: 0,
            self.HARD: -100
        }[self]


class GameSpeed(Enum):
    """Game speed multipliers."""
    NORMAL = 1.0
    FAST = 1.5
    VERY_FAST = 2.0


class MapSize(Enum):
    """Map size configurations."""
    SMALL = (15, 15)
    MEDIUM = (20, 20)
    LARGE = (25, 25)
    
    @property
    def width(self) -> int:
        """Get map width in cells."""
        return self.value[0]
    
    @property
    def height(self) -> int:
        """Get map height in cells."""
        return self.value[1]


@dataclass
class MatchConfig:
    """
    Configuration for a match.
    
    Attributes:
        wave_count: Number of waves (3, 5, 7, or 10).
        difficulty: Game difficulty level.
        game_speed: Game speed multiplier.
        map_size: Size of the game map.
        starting_money: Starting money for players.
        offense_phase_time: Time limit for offense phase in seconds.
        defense_phase_time: Time limit for defense phase in seconds.
    """
    wave_count: int = 5
    difficulty: Difficulty = Difficulty.NORMAL
    game_speed: GameSpeed = GameSpeed.NORMAL
    map_size: MapSize = MapSize.MEDIUM
    starting_money: int = 500
    
    # Phase time limits
    offense_phase_time: float = 60.0  # seconds
    defense_phase_time: float = 45.0  # seconds
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        if self.wave_count not in (3, 5, 7, 10):
            return False
        if self.starting_money < 100 or self.starting_money > 5000:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary for network transmission.
        
        Returns:
            Dictionary representation of the configuration.
        """
        return {
            'wave_count': self.wave_count,
            'difficulty': self.difficulty.name,
            'game_speed': self.game_speed.value,
            'map_size': self.map_size.name,
            'starting_money': self.starting_money,
            'offense_phase_time': self.offense_phase_time,
            'defense_phase_time': self.defense_phase_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatchConfig':
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary containing configuration data.
            
        Returns:
            MatchConfig instance created from the data.
        """
        # Convert string names back to enum instances
        difficulty = Difficulty[data['difficulty']]
        
        # Find GameSpeed by value
        game_speed = None
        for speed in GameSpeed:
            if speed.value == data['game_speed']:
                game_speed = speed
                break
        if game_speed is None:
            game_speed = GameSpeed.NORMAL
        
        # Convert map size name back to enum
        map_size = MapSize[data['map_size']]
        
        return cls(
            wave_count=data['wave_count'],
            difficulty=difficulty,
            game_speed=game_speed,
            map_size=map_size,
            starting_money=data['starting_money'],
            offense_phase_time=data.get('offense_phase_time', 60.0),
            defense_phase_time=data.get('defense_phase_time', 45.0),
        )
