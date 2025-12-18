"""
Unit tests for ResultScreen in PathWars - The Interpolation Battles.

Tests cover victory/game over display, button interactions, and visibility states.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pygame

from ui.result_screen import ResultScreen


class TestResultScreenInit:
    """Tests for ResultScreen initialization."""

    def test_result_screen_creation(self):
        """Test basic ResultScreen creation."""
        screen = ResultScreen(800, 600)
        assert screen.screen_width == 800
        assert screen.screen_height == 600
        assert screen.visible is False

    def test_result_screen_custom_bg_color(self):
        """Test ResultScreen with custom background color."""
        screen = ResultScreen(800, 600, bg_color=(10, 20, 30, 200))
        assert screen.bg_color == (10, 20, 30, 200)


class TestResultScreenVictory:
    """Tests for ResultScreen victory display."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_show_victory_sets_visible(self, result_screen):
        """Test that show_victory() makes the screen visible."""
        assert result_screen.visible is False
        result_screen.show_victory()
        assert result_screen.visible is True

    def test_show_victory_sets_result_type(self, result_screen):
        """Test that show_victory() sets result type to victory."""
        result_screen.show_victory()
        assert result_screen.result_type == ResultScreen.VICTORY

    def test_show_victory_with_stats(self, result_screen):
        """Test that show_victory() accepts and stores stats."""
        stats = {"Score": 1000, "Waves Completed": 5}
        result_screen.show_victory(stats)
        assert result_screen.stats == stats

    def test_show_victory_without_stats(self, result_screen):
        """Test that show_victory() works without stats."""
        result_screen.show_victory()
        assert result_screen.stats == {}


class TestResultScreenGameOver:
    """Tests for ResultScreen game over display."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_show_game_over_sets_visible(self, result_screen):
        """Test that show_game_over() makes the screen visible."""
        assert result_screen.visible is False
        result_screen.show_game_over()
        assert result_screen.visible is True

    def test_show_game_over_sets_result_type(self, result_screen):
        """Test that show_game_over() sets result type to game_over."""
        result_screen.show_game_over()
        assert result_screen.result_type == ResultScreen.GAME_OVER

    def test_show_game_over_with_stats(self, result_screen):
        """Test that show_game_over() accepts and stores stats."""
        stats = {"Score": 500, "Waves Completed": 2}
        result_screen.show_game_over(stats)
        assert result_screen.stats == stats


class TestResultScreenHide:
    """Tests for ResultScreen hide functionality."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_hide_sets_invisible(self, result_screen):
        """Test that hide() makes the screen invisible."""
        result_screen.show_victory()
        result_screen.hide()
        assert result_screen.visible is False

    def test_hide_clears_result_type(self, result_screen):
        """Test that hide() clears the result type."""
        result_screen.show_victory()
        result_screen.hide()
        assert result_screen.result_type is None

    def test_hide_clears_stats(self, result_screen):
        """Test that hide() clears the stats."""
        result_screen.show_victory({"Score": 100})
        result_screen.hide()
        assert result_screen.stats == {}


class TestResultScreenEventHandling:
    """Tests for ResultScreen event handling."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_handle_event_returns_none_when_hidden(self, result_screen):
        """Test that handle_event() returns None when hidden."""
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(400, 400))
        result = result_screen.handle_event(event)
        assert result is None

    def test_handle_event_returns_none_for_no_click(self, result_screen):
        """Test that handle_event() returns None when no button clicked."""
        result_screen.show_victory()
        event = pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0))
        result = result_screen.handle_event(event)
        assert result is None

    def test_handle_event_restart_button(self, result_screen):
        """Test that clicking restart button returns 'restart'."""
        result_screen.show_victory()
        
        # Get the restart button rect
        button_rect = result_screen._restart_button.rect
        click_pos = button_rect.center
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos
        )
        result = result_screen.handle_event(event)
        assert result == "restart"

    def test_handle_event_quit_button(self, result_screen):
        """Test that clicking quit button returns 'quit'."""
        result_screen.show_victory()
        
        # Get the quit button rect
        button_rect = result_screen._quit_button.rect
        click_pos = button_rect.center
        
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos
        )
        result = result_screen.handle_event(event)
        assert result == "quit"


class TestResultScreenDraw:
    """Tests for ResultScreen draw functionality."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    @pytest.fixture
    def screen(self):
        """Create a test screen surface."""
        return pygame.Surface((800, 600))

    def test_draw_when_hidden_does_nothing(self, result_screen, screen):
        """Test that draw() does nothing when screen is hidden."""
        screen.fill((0, 0, 0))
        original = screen.copy()
        
        result_screen.draw(screen)
        
        # Screen should be unchanged
        assert pygame.image.tostring(screen, 'RGB') == pygame.image.tostring(original, 'RGB')

    def test_draw_victory_modifies_screen(self, result_screen, screen):
        """Test that draw() modifies the screen for victory."""
        screen.fill((0, 0, 0))
        original = pygame.image.tostring(screen, 'RGB')
        
        result_screen.show_victory()
        result_screen.draw(screen)
        
        # Screen should be different
        assert pygame.image.tostring(screen, 'RGB') != original

    def test_draw_game_over_modifies_screen(self, result_screen, screen):
        """Test that draw() modifies the screen for game over."""
        screen.fill((0, 0, 0))
        original = pygame.image.tostring(screen, 'RGB')
        
        result_screen.show_game_over()
        result_screen.draw(screen)
        
        # Screen should be different
        assert pygame.image.tostring(screen, 'RGB') != original


class TestResultScreenSwitching:
    """Tests for switching between victory and game over states."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_switch_from_victory_to_game_over(self, result_screen):
        """Test switching from victory to game over."""
        result_screen.show_victory({"Score": 100})
        result_screen.show_game_over({"Score": 50})
        
        assert result_screen.result_type == ResultScreen.GAME_OVER
        assert result_screen.stats == {"Score": 50}

    def test_switch_from_game_over_to_victory(self, result_screen):
        """Test switching from game over to victory."""
        result_screen.show_game_over({"Score": 50})
        result_screen.show_victory({"Score": 100})
        
        assert result_screen.result_type == ResultScreen.VICTORY
        assert result_screen.stats == {"Score": 100}


class TestResultScreenStatsImmutability:
    """Tests for stats dictionary immutability."""

    @pytest.fixture
    def result_screen(self):
        """Create a fresh ResultScreen for each test."""
        return ResultScreen(800, 600)

    def test_stats_returns_copy(self, result_screen):
        """Test that stats property returns a copy."""
        original_stats = {"Score": 100}
        result_screen.show_victory(original_stats)
        
        returned_stats = result_screen.stats
        returned_stats["Score"] = 999
        
        # Original should be unchanged
        assert result_screen.stats["Score"] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
