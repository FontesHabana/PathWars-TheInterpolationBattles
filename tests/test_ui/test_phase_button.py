import pytest
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.manager import UIManager
from core.game_state import GameState, GamePhase


class TestPhaseButton:
    """Tests for phase button behavior in UIManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        # Reset GameState singleton
        GameState.reset_instance()
        self.game_state = GameState()
        self.ui_manager = UIManager(1280, 720, self.game_state)
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_phase_button_exists(self):
        """Test that phase button exists."""
        assert self.ui_manager._phase_button is not None
        assert len(self.ui_manager.panels) >= 2  # Shop + Phase panels
    
    def test_button_enabled_during_planning(self):
        """Test button is enabled during PLANNING phase."""
        assert self.game_state.current_phase == GamePhase.PLANNING
        self.ui_manager._update_phase_button()
        assert self.ui_manager._phase_button.enabled is True
        assert self.ui_manager._phase_button.text == "Start Battle"
    
    def test_button_disabled_during_battle(self):
        """Test button is disabled during BATTLE phase."""
        # Transition to BATTLE phase
        self.game_state.change_phase(GamePhase.WAITING)
        self.game_state.change_phase(GamePhase.BATTLE)
        
        # Update button state
        self.ui_manager._update_phase_button()
        
        # Verify button is disabled
        assert self.ui_manager._phase_button.enabled is False
        assert self.ui_manager._phase_button.text == "Battle in Progress..."
    
    def test_button_state_updates_correctly(self):
        """Test button state updates when phase changes."""
        # Start in PLANNING
        self.ui_manager._update_phase_button()
        assert self.ui_manager._phase_button.enabled is True
        
        # Change to BATTLE
        self.game_state.change_phase(GamePhase.WAITING)
        self.game_state.change_phase(GamePhase.BATTLE)
        self.ui_manager._update_phase_button()
        assert self.ui_manager._phase_button.enabled is False
        
        # Change back to PLANNING
        self.game_state.change_phase(GamePhase.PLANNING)
        self.ui_manager._update_phase_button()
        assert self.ui_manager._phase_button.enabled is True
