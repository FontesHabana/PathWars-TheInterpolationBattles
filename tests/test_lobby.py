"""
Unit tests for LobbyScreen UI.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ui.lobby import LobbyScreen
from core.match_config import MatchConfig, Difficulty, GameSpeed, MapSize


class TestLobbyScreen:
    """Tests for LobbyScreen UI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.screen_width = 1280
        self.screen_height = 720
        self.lobby = LobbyScreen(self.screen_width, self.screen_height)
    
    def test_initial_state(self):
        """Test initial state of LobbyScreen."""
        assert self.lobby._is_host is False
        assert self.lobby._local_ready is False
        assert self.lobby._remote_ready is False
        assert self.lobby._remote_connected is True
        assert self.lobby._active_dropdown is None
        
        # Check default config
        config = self.lobby.get_config()
        assert config.wave_count == 5
        assert config.difficulty == Difficulty.NORMAL
    
    def test_set_host_mode(self):
        """Test setting host mode."""
        self.lobby.set_host_mode(True)
        assert self.lobby._is_host is True
        
        self.lobby.set_host_mode(False)
        assert self.lobby._is_host is False
    
    def test_set_config(self):
        """Test setting match configuration."""
        new_config = MatchConfig(
            wave_count=10,
            difficulty=Difficulty.HARD,
            game_speed=GameSpeed.VERY_FAST,
            map_size=MapSize.LARGE,
            starting_money=1000,
        )
        
        self.lobby.set_config(new_config)
        
        config = self.lobby.get_config()
        assert config.wave_count == 10
        assert config.difficulty == Difficulty.HARD
        assert config.game_speed == GameSpeed.VERY_FAST
        assert config.map_size == MapSize.LARGE
        assert config.starting_money == 1000
    
    def test_set_local_ready(self):
        """Test setting local ready status."""
        self.lobby.set_local_ready(True)
        assert self.lobby._local_ready is True
        
        self.lobby.set_local_ready(False)
        assert self.lobby._local_ready is False
    
    def test_set_remote_ready(self):
        """Test setting remote ready status."""
        self.lobby.set_remote_ready(True)
        assert self.lobby._remote_ready is True
        
        self.lobby.set_remote_ready(False)
        assert self.lobby._remote_ready is False
    
    def test_set_remote_connected(self):
        """Test setting remote connection status."""
        self.lobby.set_remote_connected(False)
        assert self.lobby._remote_connected is False
        
        self.lobby.set_remote_connected(True)
        assert self.lobby._remote_connected is True
    
    def test_escape_returns_back(self):
        """Test that ESC key returns 'back'."""
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE, 'unicode': ''})
        result = self.lobby.handle_event(event)
        
        assert result == 'back'
    
    def test_back_button_returns_back(self):
        """Test that back button returns 'back'."""
        back_button = self.lobby._buttons['back']
        center = back_button.center
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert result == 'back'
    
    def test_ready_button_toggles_ready(self):
        """Test that ready button toggles local ready status."""
        ready_button = self.lobby._buttons['ready']
        center = ready_button.center
        
        # Initially not ready
        assert self.lobby._local_ready is False
        
        # Click ready button
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert self.lobby._local_ready is True
        assert result is None
        
        # Click again to unready
        result = self.lobby.handle_event(event)
        assert self.lobby._local_ready is False
    
    def test_start_button_disabled_when_not_host(self):
        """Test that start button doesn't work when not host."""
        self.lobby.set_host_mode(False)
        self.lobby.set_local_ready(True)
        self.lobby.set_remote_ready(True)
        
        start_button = self.lobby._buttons['start']
        center = start_button.center
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert result is None  # Should not start
    
    def test_start_button_disabled_when_not_ready(self):
        """Test that start button doesn't work when players not ready."""
        self.lobby.set_host_mode(True)
        
        start_button = self.lobby._buttons['start']
        center = start_button.center
        
        # Neither ready
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        assert result is None
        
        # Only local ready
        self.lobby.set_local_ready(True)
        result = self.lobby.handle_event(event)
        assert result is None
        
        # Only remote ready
        self.lobby.set_local_ready(False)
        self.lobby.set_remote_ready(True)
        result = self.lobby.handle_event(event)
        assert result is None
    
    def test_start_button_works_when_host_and_both_ready(self):
        """Test that start button works when host and both players ready."""
        self.lobby.set_host_mode(True)
        self.lobby.set_local_ready(True)
        self.lobby.set_remote_ready(True)
        
        start_button = self.lobby._buttons['start']
        center = start_button.center
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert result == 'start'
    
    def test_dropdown_opens_when_host_clicks(self):
        """Test that clicking dropdown opens it when host."""
        self.lobby.set_host_mode(True)
        
        wave_dropdown = self.lobby._dropdowns['wave_count']
        center = wave_dropdown.center
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert self.lobby._active_dropdown == 'wave_count'
        assert result is None
    
    def test_dropdown_does_not_open_when_not_host(self):
        """Test that clicking dropdown doesn't open when not host."""
        self.lobby.set_host_mode(False)
        
        wave_dropdown = self.lobby._dropdowns['wave_count']
        center = wave_dropdown.center
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.lobby.handle_event(event)
        
        assert self.lobby._active_dropdown is None
    
    def test_wave_count_dropdown_selection(self):
        """Test selecting wave count from dropdown."""
        self.lobby.set_host_mode(True)
        
        # Open dropdown
        self.lobby._active_dropdown = 'wave_count'
        
        # Calculate position of second option (5 waves, index 1)
        dropdown_rect = self.lobby._dropdowns['wave_count']
        option_height = 35
        option_pos = (dropdown_rect.centerx, dropdown_rect.bottom + option_height * 1 + option_height // 2)
        
        # Click the option
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': option_pos})
        result = self.lobby.handle_event(event)
        
        # Dropdown should be closed now
        assert self.lobby._active_dropdown is None
        
        # Check that wave count was set (option at index 1 is 5)
        assert self.lobby._config.wave_count == 5
    
    def test_difficulty_dropdown_selection(self):
        """Test selecting difficulty from dropdown."""
        self.lobby.set_host_mode(True)
        
        # Open dropdown
        self.lobby._active_dropdown = 'difficulty'
        
        # Calculate position of first option (EASY, index 0)
        dropdown_rect = self.lobby._dropdowns['difficulty']
        option_height = 35
        option_pos = (dropdown_rect.centerx, dropdown_rect.bottom + option_height // 2)
        
        # Click the option
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': option_pos})
        result = self.lobby.handle_event(event)
        
        # Check that difficulty was set
        assert self.lobby._config.difficulty == Difficulty.EASY
    
    def test_game_speed_dropdown_selection(self):
        """Test selecting game speed from dropdown."""
        self.lobby.set_host_mode(True)
        
        # Open dropdown
        self.lobby._active_dropdown = 'game_speed'
        
        # Calculate position of third option (VERY_FAST, index 2)
        dropdown_rect = self.lobby._dropdowns['game_speed']
        option_height = 35
        option_pos = (dropdown_rect.centerx, dropdown_rect.bottom + option_height * 2 + option_height // 2)
        
        # Click the option
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': option_pos})
        result = self.lobby.handle_event(event)
        
        # Check that speed was set
        assert self.lobby._config.game_speed == GameSpeed.VERY_FAST
    
    def test_map_size_dropdown_selection(self):
        """Test selecting map size from dropdown."""
        self.lobby.set_host_mode(True)
        
        # Open dropdown
        self.lobby._active_dropdown = 'map_size'
        
        # Calculate position of third option (LARGE, index 2)
        dropdown_rect = self.lobby._dropdowns['map_size']
        option_height = 35
        option_pos = (dropdown_rect.centerx, dropdown_rect.bottom + option_height * 2 + option_height // 2)
        
        # Click the option
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': option_pos})
        result = self.lobby.handle_event(event)
        
        # Check that size was set
        assert self.lobby._config.map_size == MapSize.LARGE
    
    def test_starting_money_dropdown_selection(self):
        """Test selecting starting money from dropdown."""
        self.lobby.set_host_mode(True)
        
        # Open dropdown
        self.lobby._active_dropdown = 'starting_money'
        
        # Calculate position of last option (1500, index 4)
        dropdown_rect = self.lobby._dropdowns['starting_money']
        option_height = 35
        option_pos = (dropdown_rect.centerx, dropdown_rect.bottom + option_height * 4 + option_height // 2)
        
        # Click the option
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': option_pos})
        result = self.lobby.handle_event(event)
        
        # Check that money was set
        assert self.lobby._config.starting_money == 1500
    
    def test_mouse_motion_updates_hover(self):
        """Test that mouse motion updates hover state."""
        ready_button = self.lobby._buttons['ready']
        center = ready_button.center
        
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': center})
        self.lobby.handle_event(event)
        
        assert self.lobby._hovered_button == 'ready'
    
    def test_start_button_hover_only_when_enabled(self):
        """Test that start button only highlights when enabled."""
        start_button = self.lobby._buttons['start']
        center = start_button.center
        
        # Not host - should not highlight
        self.lobby.set_host_mode(False)
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': center})
        self.lobby.handle_event(event)
        assert self.lobby._hovered_button != 'start'
        
        # Host but not ready - should not highlight
        self.lobby.set_host_mode(True)
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': center})
        self.lobby.handle_event(event)
        assert self.lobby._hovered_button != 'start'
        
        # Host and both ready - should highlight
        self.lobby.set_local_ready(True)
        self.lobby.set_remote_ready(True)
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': center})
        self.lobby.handle_event(event)
        assert self.lobby._hovered_button == 'start'
    
    def test_draw_does_not_crash(self):
        """Test that draw method doesn't crash."""
        # Create a surface to draw on
        surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Should not raise any exceptions
        self.lobby.draw(surface)
    
    def test_draw_with_various_states(self):
        """Test drawing in various states."""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Test as host
        self.lobby.set_host_mode(True)
        self.lobby.draw(surface)
        
        # Test with ready status
        self.lobby.set_local_ready(True)
        self.lobby.set_remote_ready(True)
        self.lobby.draw(surface)
        
        # Test with dropdown open
        self.lobby._active_dropdown = 'wave_count'
        self.lobby.draw(surface)
        
        # Test with remote disconnected
        self.lobby.set_remote_connected(False)
        self.lobby.draw(surface)
    
    def test_dropdown_closes_on_outside_click(self):
        """Test that clicking outside dropdown closes it."""
        self.lobby.set_host_mode(True)
        self.lobby._active_dropdown = 'wave_count'
        
        # Click somewhere outside dropdown menu
        outside_pos = (100, 100)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': outside_pos})
        result = self.lobby.handle_event(event)
        
        # Dropdown should be closed
        assert self.lobby._active_dropdown is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
