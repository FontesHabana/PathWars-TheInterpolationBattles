"""
Unit tests for WaveBanner in PathWars - The Interpolation Battles.

Tests cover show/hide logic, timer countdown, and visibility states.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Initialize pygame for font/surface operations
import pygame
pygame.init()

from ui.wave_banner import WaveBanner


class TestWaveBannerInit:
    """Tests for WaveBanner initialization."""

    def test_wave_banner_creation(self):
        """Test basic WaveBanner creation."""
        banner = WaveBanner(800, 600)
        assert banner.screen_width == 800
        assert banner.screen_height == 600
        assert banner.visible is False

    def test_wave_banner_custom_colors(self):
        """Test WaveBanner with custom colors."""
        banner = WaveBanner(
            800,
            600,
            font_size=36,
            bg_color=(10, 20, 30, 200),
            text_color=(100, 150, 200),
        )
        assert banner.font_size == 36
        assert banner.bg_color == (10, 20, 30, 200)
        assert banner.text_color == (100, 150, 200)


class TestWaveBannerShowHide:
    """Tests for WaveBanner show/hide logic."""

    @pytest.fixture
    def banner(self):
        """Create a fresh WaveBanner for each test."""
        return WaveBanner(800, 600)

    def test_show_sets_visible(self, banner):
        """Test that show() makes the banner visible."""
        assert banner.visible is False
        banner.show("Wave 1")
        assert banner.visible is True

    def test_show_sets_message(self, banner):
        """Test that show() sets the message."""
        banner.show("Wave 2 Complete!")
        assert banner.message == "Wave 2 Complete!"

    def test_show_sets_duration(self, banner):
        """Test that show() uses the duration parameter."""
        banner.show("Test", duration=5.0)
        assert banner.remaining_time == pytest.approx(5.0, abs=0.001)

    def test_show_default_duration(self, banner):
        """Test that show() uses default duration of 2.0."""
        banner.show("Test")
        assert banner.remaining_time == pytest.approx(2.0, abs=0.001)

    def test_hide_sets_invisible(self, banner):
        """Test that hide() makes the banner invisible."""
        banner.show("Test")
        assert banner.visible is True
        banner.hide()
        assert banner.visible is False

    def test_hide_clears_message(self, banner):
        """Test that hide() clears the message."""
        banner.show("Test")
        banner.hide()
        assert banner.message == ""

    def test_hide_resets_timer(self, banner):
        """Test that hide() resets the timer."""
        banner.show("Test")
        banner.update(1.0)
        banner.hide()
        assert banner.remaining_time == 0.0


class TestWaveBannerTimer:
    """Tests for WaveBanner timer countdown."""

    @pytest.fixture
    def banner(self):
        """Create a fresh WaveBanner for each test."""
        return WaveBanner(800, 600)

    def test_update_decrements_remaining_time(self, banner):
        """Test that update() reduces remaining time."""
        banner.show("Test", duration=5.0)
        banner.update(1.0)
        assert banner.remaining_time == pytest.approx(4.0, abs=0.001)

    def test_update_multiple_times(self, banner):
        """Test multiple update calls accumulate correctly."""
        banner.show("Test", duration=5.0)
        banner.update(0.5)
        banner.update(0.5)
        banner.update(0.5)
        assert banner.remaining_time == pytest.approx(3.5, abs=0.001)

    def test_update_hides_after_duration(self, banner):
        """Test that banner hides when timer expires."""
        banner.show("Test", duration=2.0)
        assert banner.visible is True
        banner.update(2.0)
        assert banner.visible is False

    def test_update_hides_after_exceeding_duration(self, banner):
        """Test that banner hides when timer exceeds duration."""
        banner.show("Test", duration=2.0)
        banner.update(3.0)
        assert banner.visible is False

    def test_update_does_nothing_when_hidden(self, banner):
        """Test that update() is a no-op when banner is hidden."""
        banner.update(1.0)
        assert banner.visible is False
        assert banner.remaining_time == 0.0

    def test_remaining_time_never_negative(self, banner):
        """Test that remaining_time is clamped to 0."""
        banner.show("Test", duration=1.0)
        banner.update(5.0)
        assert banner.remaining_time == 0.0


class TestWaveBannerDraw:
    """Tests for WaveBanner draw functionality."""

    @pytest.fixture
    def banner(self):
        """Create a fresh WaveBanner for each test."""
        return WaveBanner(800, 600)

    @pytest.fixture
    def screen(self):
        """Create a test screen surface."""
        return pygame.Surface((800, 600))

    def test_draw_when_hidden_does_nothing(self, banner, screen):
        """Test that draw() does nothing when banner is hidden."""
        # Fill screen with a known color
        screen.fill((0, 0, 0))
        original = screen.copy()
        
        banner.draw(screen)
        
        # Screen should be unchanged
        assert pygame.image.tostring(screen, 'RGB') == pygame.image.tostring(original, 'RGB')

    def test_draw_when_visible_modifies_screen(self, banner, screen):
        """Test that draw() modifies the screen when visible."""
        screen.fill((0, 0, 0))
        original = pygame.image.tostring(screen, 'RGB')
        
        banner.show("Test Message")
        banner.draw(screen)
        
        # Screen should be different
        assert pygame.image.tostring(screen, 'RGB') != original


class TestWaveBannerReshowing:
    """Tests for WaveBanner re-showing behavior."""

    @pytest.fixture
    def banner(self):
        """Create a fresh WaveBanner for each test."""
        return WaveBanner(800, 600)

    def test_show_replaces_existing_message(self, banner):
        """Test that showing a new message replaces the old one."""
        banner.show("First Message", duration=5.0)
        banner.update(2.0)
        banner.show("Second Message", duration=3.0)
        
        assert banner.message == "Second Message"
        assert banner.remaining_time == pytest.approx(3.0, abs=0.001)

    def test_show_resets_timer(self, banner):
        """Test that showing resets the timer."""
        banner.show("First", duration=5.0)
        banner.update(4.0)  # Almost expired
        banner.show("Second", duration=2.0)
        
        # Timer should be reset, not expired
        assert banner.visible is True
        assert banner.remaining_time == pytest.approx(2.0, abs=0.001)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
