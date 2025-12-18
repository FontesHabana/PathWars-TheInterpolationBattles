"""
Unit tests for MatchConfig and related enums.
"""

import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.match_config import MatchConfig, Difficulty, GameSpeed, MapSize


class TestDifficulty:
    """Tests for Difficulty enum."""
    
    def test_enemy_hp_multiplier_easy(self):
        """Test that Easy difficulty has correct HP multiplier."""
        assert Difficulty.EASY.enemy_hp_multiplier() == 0.75
    
    def test_enemy_hp_multiplier_normal(self):
        """Test that Normal difficulty has correct HP multiplier."""
        assert Difficulty.NORMAL.enemy_hp_multiplier() == 1.0
    
    def test_enemy_hp_multiplier_hard(self):
        """Test that Hard difficulty has correct HP multiplier."""
        assert Difficulty.HARD.enemy_hp_multiplier() == 1.5
    
    def test_starting_money_bonus_easy(self):
        """Test that Easy difficulty has correct money bonus."""
        assert Difficulty.EASY.starting_money_bonus() == 200
    
    def test_starting_money_bonus_normal(self):
        """Test that Normal difficulty has correct money bonus."""
        assert Difficulty.NORMAL.starting_money_bonus() == 0
    
    def test_starting_money_bonus_hard(self):
        """Test that Hard difficulty has correct money bonus."""
        assert Difficulty.HARD.starting_money_bonus() == -100


class TestGameSpeed:
    """Tests for GameSpeed enum."""
    
    def test_normal_speed(self):
        """Test that Normal speed has value 1.0."""
        assert GameSpeed.NORMAL.value == 1.0
    
    def test_fast_speed(self):
        """Test that Fast speed has value 1.5."""
        assert GameSpeed.FAST.value == 1.5
    
    def test_very_fast_speed(self):
        """Test that Very Fast speed has value 2.0."""
        assert GameSpeed.VERY_FAST.value == 2.0


class TestMapSize:
    """Tests for MapSize enum."""
    
    def test_small_size(self):
        """Test that Small map has correct dimensions."""
        assert MapSize.SMALL.width == 15
        assert MapSize.SMALL.height == 15
    
    def test_medium_size(self):
        """Test that Medium map has correct dimensions."""
        assert MapSize.MEDIUM.width == 20
        assert MapSize.MEDIUM.height == 20
    
    def test_large_size(self):
        """Test that Large map has correct dimensions."""
        assert MapSize.LARGE.width == 25
        assert MapSize.LARGE.height == 25


class TestMatchConfig:
    """Tests for MatchConfig dataclass."""
    
    def test_default_values(self):
        """Test that MatchConfig has correct default values."""
        config = MatchConfig()
        
        assert config.wave_count == 5
        assert config.difficulty == Difficulty.NORMAL
        assert config.game_speed == GameSpeed.NORMAL
        assert config.map_size == MapSize.MEDIUM
        assert config.starting_money == 500
        assert config.offense_phase_time == 60.0
        assert config.defense_phase_time == 45.0
    
    def test_custom_values(self):
        """Test creating MatchConfig with custom values."""
        config = MatchConfig(
            wave_count=10,
            difficulty=Difficulty.HARD,
            game_speed=GameSpeed.VERY_FAST,
            map_size=MapSize.LARGE,
            starting_money=1000,
            offense_phase_time=90.0,
            defense_phase_time=60.0,
        )
        
        assert config.wave_count == 10
        assert config.difficulty == Difficulty.HARD
        assert config.game_speed == GameSpeed.VERY_FAST
        assert config.map_size == MapSize.LARGE
        assert config.starting_money == 1000
        assert config.offense_phase_time == 90.0
        assert config.defense_phase_time == 60.0
    
    def test_validate_valid_config(self):
        """Test that valid configurations pass validation."""
        for wave_count in (3, 5, 7, 10):
            config = MatchConfig(wave_count=wave_count, starting_money=500)
            assert config.validate() is True
    
    def test_validate_invalid_wave_count(self):
        """Test that invalid wave counts fail validation."""
        for wave_count in (1, 2, 4, 6, 8, 9, 11, 15):
            config = MatchConfig(wave_count=wave_count)
            assert config.validate() is False
    
    def test_validate_invalid_starting_money_too_low(self):
        """Test that starting money below minimum fails validation."""
        config = MatchConfig(starting_money=99)
        assert config.validate() is False
    
    def test_validate_invalid_starting_money_too_high(self):
        """Test that starting money above maximum fails validation."""
        config = MatchConfig(starting_money=5001)
        assert config.validate() is False
    
    def test_validate_boundary_starting_money(self):
        """Test boundary values for starting money."""
        config_min = MatchConfig(starting_money=100)
        assert config_min.validate() is True
        
        config_max = MatchConfig(starting_money=5000)
        assert config_max.validate() is True
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = MatchConfig(
            wave_count=7,
            difficulty=Difficulty.EASY,
            game_speed=GameSpeed.FAST,
            map_size=MapSize.SMALL,
            starting_money=800,
            offense_phase_time=75.0,
            defense_phase_time=50.0,
        )
        
        data = config.to_dict()
        
        assert data['wave_count'] == 7
        assert data['difficulty'] == 'EASY'
        assert data['game_speed'] == 1.5
        assert data['map_size'] == 'SMALL'
        assert data['starting_money'] == 800
        assert data['offense_phase_time'] == 75.0
        assert data['defense_phase_time'] == 50.0
    
    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            'wave_count': 10,
            'difficulty': 'HARD',
            'game_speed': 2.0,
            'map_size': 'LARGE',
            'starting_money': 1200,
            'offense_phase_time': 90.0,
            'defense_phase_time': 60.0,
        }
        
        config = MatchConfig.from_dict(data)
        
        assert config.wave_count == 10
        assert config.difficulty == Difficulty.HARD
        assert config.game_speed == GameSpeed.VERY_FAST
        assert config.map_size == MapSize.LARGE
        assert config.starting_money == 1200
        assert config.offense_phase_time == 90.0
        assert config.defense_phase_time == 60.0
    
    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are reversible."""
        original = MatchConfig(
            wave_count=5,
            difficulty=Difficulty.NORMAL,
            game_speed=GameSpeed.NORMAL,
            map_size=MapSize.MEDIUM,
            starting_money=500,
        )
        
        data = original.to_dict()
        restored = MatchConfig.from_dict(data)
        
        assert restored.wave_count == original.wave_count
        assert restored.difficulty == original.difficulty
        assert restored.game_speed == original.game_speed
        assert restored.map_size == original.map_size
        assert restored.starting_money == original.starting_money
        assert restored.offense_phase_time == original.offense_phase_time
        assert restored.defense_phase_time == original.defense_phase_time
    
    def test_from_dict_with_missing_phase_times(self):
        """Test deserialization with missing phase time fields uses defaults."""
        data = {
            'wave_count': 5,
            'difficulty': 'NORMAL',
            'game_speed': 1.0,
            'map_size': 'MEDIUM',
            'starting_money': 500,
        }
        
        config = MatchConfig.from_dict(data)
        
        # Should use default values
        assert config.offense_phase_time == 60.0
        assert config.defense_phase_time == 45.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
