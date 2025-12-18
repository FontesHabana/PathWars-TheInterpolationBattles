import pytest
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.pause_menu import PauseMenu


class TestPauseMenu:
    """Tests for PauseMenu UI component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_pause_menu_initial_state_hidden(self):
        """Test pause menu starts hidden."""
        assert self.pause_menu.visible is False
    
    def test_pause_menu_show(self):
        """Test showing pause menu."""
        self.pause_menu.show()
        assert self.pause_menu.visible is True
    
    def test_pause_menu_hide(self):
        """Test hiding pause menu."""
        self.pause_menu.show()
        self.pause_menu.hide()
        assert self.pause_menu.visible is False
    
    def test_pause_menu_toggle(self):
        """Test toggling pause menu visibility."""
        assert self.pause_menu.visible is False
        self.pause_menu.toggle()
        assert self.pause_menu.visible is True
        self.pause_menu.toggle()
        assert self.pause_menu.visible is False
    
    def test_resume_button_returns_resume_action(self):
        """Test resume button returns 'resume' action."""
        self.pause_menu.show()
        # Simulate click on resume button
        resume_btn = self.pause_menu._buttons.get('resume')
        if resume_btn:
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': resume_btn.rect.center})
            result = self.pause_menu.handle_event(event)
            assert result == 'resume'
    
    def test_restart_button_returns_restart_action(self):
        """Test restart button returns 'restart' action."""
        self.pause_menu.show()
        restart_btn = self.pause_menu._buttons.get('restart')
        if restart_btn:
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': restart_btn.rect.center})
            result = self.pause_menu.handle_event(event)
            assert result == 'restart'
    
    def test_main_menu_button_returns_main_menu_action(self):
        """Test main menu button returns 'main_menu' action."""
        self.pause_menu.show()
        main_menu_btn = self.pause_menu._buttons.get('main_menu')
        if main_menu_btn:
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': main_menu_btn.rect.center})
            result = self.pause_menu.handle_event(event)
            assert result == 'main_menu'
    
    def test_events_ignored_when_hidden(self):
        """Test that events are ignored when menu is hidden."""
        assert self.pause_menu.visible is False
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (640, 360)})
        result = self.pause_menu.handle_event(event)
        assert result is None
