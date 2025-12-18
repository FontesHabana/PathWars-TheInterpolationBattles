"""
Unit tests for game phase state machine.

Tests cover:
- Valid and invalid phase transitions
- Enter/exit hooks
- Time limits
- Input handling per phase
- PhaseManager functionality
"""

import sys
import os
import pytest
import pygame

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.game_phases import (
    GamePhaseState,
    LobbyState,
    OffensePlanningState,
    DefensePlanningState,
    BattleState,
    GameOverState,
    PhaseManager,
)


class TestPhaseManager:
    """Tests for PhaseManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        
        # Register all states
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        self.battle = BattleState(self.manager)
        self.game_over = GameOverState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        self.manager.register_state("Battle", self.battle)
        self.manager.register_state("GameOver", self.game_over)
    
    def test_register_state(self):
        """Test registering a state."""
        manager = PhaseManager()
        lobby = LobbyState(manager)
        manager.register_state("Lobby", lobby)
        
        assert manager.get_state("Lobby") == lobby
    
    def test_initial_state_is_none(self):
        """Test that initial current state is None."""
        manager = PhaseManager()
        assert manager.current_phase_name is None
        assert manager.current_state is None
    
    def test_transition_to_sets_current_state(self):
        """Test that transition_to sets current state."""
        result = self.manager.transition_to("Lobby")
        
        assert result is True
        assert self.manager.current_phase_name == "Lobby"
        assert self.manager.current_state == self.lobby
    
    def test_transition_to_nonexistent_phase_fails(self):
        """Test transitioning to non-existent phase fails."""
        self.manager.transition_to("Lobby")
        result = self.manager.transition_to("NonExistent")
        
        assert result is False
        assert self.manager.current_phase_name == "Lobby"
    
    def test_update_calls_current_state_update(self):
        """Test that update calls current state's update method."""
        self.manager.transition_to("OffensePlanning")
        
        initial_time = self.offense._elapsed_time
        self.manager.update(1.5)
        
        assert self.offense._elapsed_time == initial_time + 1.5
    
    def test_handle_input_routes_to_current_state(self):
        """Test that handle_input routes to current state."""
        self.manager.transition_to("Lobby")
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = self.manager.handle_input(event)
        
        assert result is True
        assert self.lobby._players_ready == 1
    
    def test_get_state_returns_registered_state(self):
        """Test get_state returns correct state."""
        assert self.manager.get_state("Lobby") == self.lobby
        assert self.manager.get_state("Battle") == self.battle


class TestValidTransitions:
    """Tests for valid phase transitions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        self.battle = BattleState(self.manager)
        self.game_over = GameOverState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        self.manager.register_state("Battle", self.battle)
        self.manager.register_state("GameOver", self.game_over)
    
    def test_lobby_to_offense_planning(self):
        """Test transition from Lobby to OffensePlanning."""
        self.manager.transition_to("Lobby")
        result = self.manager.transition_to("OffensePlanning")
        
        assert result is True
        assert self.manager.current_phase_name == "OffensePlanning"
    
    def test_offense_planning_to_defense_planning(self):
        """Test transition from OffensePlanning to DefensePlanning."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        result = self.manager.transition_to("DefensePlanning")
        
        assert result is True
        assert self.manager.current_phase_name == "DefensePlanning"
    
    def test_defense_planning_to_battle(self):
        """Test transition from DefensePlanning to Battle."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        result = self.manager.transition_to("Battle")
        
        assert result is True
        assert self.manager.current_phase_name == "Battle"
    
    def test_battle_to_offense_planning(self):
        """Test transition from Battle to OffensePlanning (next wave)."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        self.manager.transition_to("Battle")
        result = self.manager.transition_to("OffensePlanning")
        
        assert result is True
        assert self.manager.current_phase_name == "OffensePlanning"
    
    def test_battle_to_game_over(self):
        """Test transition from Battle to GameOver."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        self.manager.transition_to("Battle")
        result = self.manager.transition_to("GameOver")
        
        assert result is True
        assert self.manager.current_phase_name == "GameOver"
    
    def test_game_over_to_lobby(self):
        """Test transition from GameOver to Lobby."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        self.manager.transition_to("Battle")
        self.manager.transition_to("GameOver")
        result = self.manager.transition_to("Lobby")
        
        assert result is True
        assert self.manager.current_phase_name == "Lobby"


class TestInvalidTransitions:
    """Tests for invalid phase transitions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        self.battle = BattleState(self.manager)
        self.game_over = GameOverState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        self.manager.register_state("Battle", self.battle)
        self.manager.register_state("GameOver", self.game_over)
    
    def test_lobby_to_defense_planning_invalid(self):
        """Test invalid transition from Lobby to DefensePlanning."""
        self.manager.transition_to("Lobby")
        result = self.manager.transition_to("DefensePlanning")
        
        assert result is False
        assert self.manager.current_phase_name == "Lobby"
    
    def test_lobby_to_battle_invalid(self):
        """Test invalid transition from Lobby to Battle."""
        self.manager.transition_to("Lobby")
        result = self.manager.transition_to("Battle")
        
        assert result is False
        assert self.manager.current_phase_name == "Lobby"
    
    def test_offense_planning_to_battle_invalid(self):
        """Test invalid transition from OffensePlanning to Battle."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        result = self.manager.transition_to("Battle")
        
        assert result is False
        assert self.manager.current_phase_name == "OffensePlanning"
    
    def test_defense_planning_to_offense_planning_invalid(self):
        """Test invalid transition from DefensePlanning to OffensePlanning."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        result = self.manager.transition_to("OffensePlanning")
        
        assert result is False
        assert self.manager.current_phase_name == "DefensePlanning"
    
    def test_game_over_to_offense_planning_invalid(self):
        """Test invalid transition from GameOver to OffensePlanning."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        self.manager.transition_to("Battle")
        self.manager.transition_to("GameOver")
        result = self.manager.transition_to("OffensePlanning")
        
        assert result is False
        assert self.manager.current_phase_name == "GameOver"


class TestEnterExitHooks:
    """Tests for enter/exit hooks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
    
    def test_enter_hook_resets_elapsed_time(self):
        """Test that enter hook resets elapsed time."""
        self.manager.transition_to("OffensePlanning")
        self.offense._elapsed_time = 10.0
        
        # Exit and re-enter through valid path: OffensePlanning -> DefensePlanning -> Battle -> OffensePlanning
        manager = PhaseManager()
        lobby = LobbyState(manager)
        offense = OffensePlanningState(manager)
        defense = DefensePlanningState(manager)
        battle = BattleState(manager)
        
        manager.register_state("Lobby", lobby)
        manager.register_state("OffensePlanning", offense)
        manager.register_state("DefensePlanning", defense)
        manager.register_state("Battle", battle)
        
        manager.transition_to("Lobby")
        manager.transition_to("OffensePlanning")
        offense._elapsed_time = 10.0
        
        manager.transition_to("DefensePlanning")
        manager.transition_to("Battle")
        manager.transition_to("OffensePlanning")
        
        assert offense._elapsed_time == 0.0
    
    def test_offense_exit_locks_control_points(self):
        """Test that offense planning exit locks control points."""
        self.manager.transition_to("OffensePlanning")
        self.offense.add_control_point(10.0, 20.0)
        self.offense.add_control_point(30.0, 40.0)
        
        assert len(self.offense._locked_points) == 0
        
        self.manager.transition_to("DefensePlanning")
        
        # Points should be locked after exit
        assert len(self.offense._locked_points) == 2
        assert (10.0, 20.0) in self.offense._locked_points
        assert (30.0, 40.0) in self.offense._locked_points
    
    def test_offense_exit_disables_editing(self):
        """Test that offense planning exit disables editing."""
        self.manager.transition_to("OffensePlanning")
        assert self.offense._editing_enabled is True
        
        self.manager.transition_to("DefensePlanning")
        assert self.offense._editing_enabled is False
    
    def test_defense_exit_disables_placement(self):
        """Test that defense planning exit disables placement."""
        self.manager.transition_to("DefensePlanning")
        assert self.defense._placement_enabled is True
        
        # Need to transition through valid path
        manager = PhaseManager()
        lobby = LobbyState(manager)
        offense = OffensePlanningState(manager)
        defense = DefensePlanningState(manager)
        battle = BattleState(manager)
        
        manager.register_state("Lobby", lobby)
        manager.register_state("OffensePlanning", offense)
        manager.register_state("DefensePlanning", defense)
        manager.register_state("Battle", battle)
        
        manager.transition_to("Lobby")
        manager.transition_to("OffensePlanning")
        manager.transition_to("DefensePlanning")
        assert defense._placement_enabled is True
        
        manager.transition_to("Battle")
        assert defense._placement_enabled is False


class TestTimeLimits:
    """Tests for time limits on phases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager, time_limit=60.0)
        self.defense = DefensePlanningState(self.manager, time_limit=45.0)
        self.battle = BattleState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        self.manager.register_state("Battle", self.battle)
    
    def test_lobby_has_no_time_limit(self):
        """Test that Lobby has no time limit."""
        assert self.lobby._time_limit is None
        assert self.lobby.time_remaining is None
    
    def test_offense_planning_time_limit(self):
        """Test OffensePlanning time limit."""
        assert self.offense._time_limit == 60.0
        assert self.offense.time_remaining == 60.0
    
    def test_defense_planning_time_limit(self):
        """Test DefensePlanning time limit."""
        assert self.defense._time_limit == 45.0
        assert self.defense.time_remaining == 45.0
    
    def test_battle_has_no_time_limit(self):
        """Test that Battle has no time limit."""
        assert self.battle._time_limit is None
        assert self.battle.time_remaining is None
    
    def test_time_remaining_decreases(self):
        """Test that time remaining decreases with updates."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        
        assert self.offense.time_remaining == 60.0
        
        self.manager.update(10.0)
        assert pytest.approx(self.offense.time_remaining, abs=0.01) == 50.0
        
        self.manager.update(20.0)
        assert pytest.approx(self.offense.time_remaining, abs=0.01) == 30.0
    
    def test_time_remaining_does_not_go_negative(self):
        """Test that time remaining doesn't go below zero."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        
        self.manager.update(70.0)
        assert self.offense.time_remaining == 0.0
    
    def test_offense_auto_transitions_when_time_expires(self):
        """Test offense planning auto-transitions when time expires."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        
        # Update past the time limit
        self.manager.update(61.0)
        
        assert self.manager.current_phase_name == "DefensePlanning"
    
    def test_defense_auto_transitions_when_time_expires(self):
        """Test defense planning auto-transitions when time expires."""
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
        
        # Update past the time limit
        self.manager.update(46.0)
        
        assert self.manager.current_phase_name == "Battle"


class TestLobbyState:
    """Tests for LobbyState input handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.lobby = LobbyState(self.manager)
        self.manager.register_state("Lobby", self.lobby)
        self.manager.transition_to("Lobby")
    
    def test_lobby_ready_input(self):
        """Test lobby ready input handling."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = self.lobby.handle_input(event)
        
        assert result is True
        assert self.lobby._players_ready == 1
    
    def test_lobby_set_players_connected(self):
        """Test setting players connected."""
        assert self.lobby._both_players_connected is False
        
        self.lobby.set_players_connected(True)
        assert self.lobby._both_players_connected is True
    
    def test_lobby_is_ready_to_start(self):
        """Test lobby ready to start check."""
        assert self.lobby.is_ready_to_start() is False
        
        self.lobby.set_players_connected(True)
        assert self.lobby.is_ready_to_start() is False
        
        self.lobby._players_ready = 2
        assert self.lobby.is_ready_to_start() is True


class TestOffensePlanningState:
    """Tests for OffensePlanningState input handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
    
    def test_offense_add_control_point_with_click(self):
        """Test adding control point with mouse click."""
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 200))
        result = self.offense.handle_input(event)
        
        assert result is True
        assert len(self.offense._control_points) == 1
        assert self.offense._control_points[0] == (100.0, 200.0)
    
    def test_offense_remove_control_point_with_right_click(self):
        """Test removing control point with right click."""
        self.offense.add_control_point(10.0, 20.0)
        assert len(self.offense._control_points) == 1
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(0, 0))
        result = self.offense.handle_input(event)
        
        assert result is True
        assert len(self.offense._control_points) == 0
    
    def test_offense_manual_transition_with_space(self):
        """Test manual transition with space key."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = self.offense.handle_input(event)
        
        assert result is True
        assert self.manager.current_phase_name == "DefensePlanning"
    
    def test_offense_add_control_point_method(self):
        """Test add_control_point method."""
        result = self.offense.add_control_point(50.0, 75.0)
        
        assert result is True
        assert (50.0, 75.0) in self.offense._control_points
    
    def test_offense_remove_control_point_method(self):
        """Test remove_control_point method."""
        self.offense.add_control_point(50.0, 75.0)
        self.offense.add_control_point(100.0, 125.0)
        
        result = self.offense.remove_control_point(0)
        assert result is True
        assert (50.0, 75.0) not in self.offense._control_points
        assert (100.0, 125.0) in self.offense._control_points


class TestDefensePlanningState:
    """Tests for DefensePlanningState input handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.lobby = LobbyState(self.manager)
        self.offense = OffensePlanningState(self.manager)
        self.defense = DefensePlanningState(self.manager)
        self.battle = BattleState(self.manager)
        
        self.manager.register_state("Lobby", self.lobby)
        self.manager.register_state("OffensePlanning", self.offense)
        self.manager.register_state("DefensePlanning", self.defense)
        self.manager.register_state("Battle", self.battle)
        
        self.manager.transition_to("Lobby")
        self.manager.transition_to("OffensePlanning")
        self.manager.transition_to("DefensePlanning")
    
    def test_defense_place_tower_with_click(self):
        """Test placing tower with mouse click."""
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(64, 96))
        result = self.defense.handle_input(event)
        
        assert result is True
        assert len(self.defense._tower_placements) == 1
        # Grid position should be pos // 32
        assert self.defense._tower_placements[0] == (2, 3, "basic")
    
    def test_defense_remove_tower_with_right_click(self):
        """Test removing tower with right click."""
        self.defense.place_tower(5, 5, "basic")
        assert len(self.defense._tower_placements) == 1
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(0, 0))
        result = self.defense.handle_input(event)
        
        assert result is True
        assert len(self.defense._tower_placements) == 0
    
    def test_defense_manual_transition_with_space(self):
        """Test manual transition with space key."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = self.defense.handle_input(event)
        
        assert result is True
        assert self.manager.current_phase_name == "Battle"
    
    def test_defense_place_tower_method(self):
        """Test place_tower method."""
        result = self.defense.place_tower(3, 4, "cannon")
        
        assert result is True
        assert (3, 4, "cannon") in self.defense._tower_placements
    
    def test_defense_remove_tower_method(self):
        """Test remove_tower method."""
        self.defense.place_tower(3, 4, "cannon")
        self.defense.place_tower(5, 6, "laser")
        
        result = self.defense.remove_tower(3, 4)
        assert result is True
        assert (3, 4, "cannon") not in self.defense._tower_placements
        assert (5, 6, "laser") in self.defense._tower_placements


class TestBattleState:
    """Tests for BattleState input handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.battle = BattleState(self.manager)
        self.manager.register_state("Battle", self.battle)
        self.manager.transition_to("Battle")
    
    def test_battle_pause_with_p_key(self):
        """Test pausing battle with P key."""
        assert self.battle._paused is False
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        result = self.battle.handle_input(event)
        
        assert result is True
        assert self.battle._paused is True
    
    def test_battle_pause_with_escape(self):
        """Test pausing battle with Escape key."""
        assert self.battle._paused is False
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = self.battle.handle_input(event)
        
        assert result is True
        assert self.battle._paused is True
    
    def test_battle_pause_toggle(self):
        """Test pause toggle."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        
        self.battle.handle_input(event)
        assert self.battle._paused is True
        
        self.battle.handle_input(event)
        assert self.battle._paused is False
    
    def test_battle_camera_controls(self):
        """Test camera controls are handled."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        result = self.battle.handle_input(event)
        assert result is True
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
        result = self.battle.handle_input(event)
        assert result is True
    
    def test_battle_complete_battle(self):
        """Test completing battle."""
        assert self.battle._battle_complete is False
        
        self.battle.complete_battle(victory=True)
        
        assert self.battle._battle_complete is True
        assert self.battle.is_victory() is True
    
    def test_battle_paused_does_not_update_time(self):
        """Test that paused battle doesn't update time."""
        self.battle._paused = True
        initial_time = self.battle._elapsed_time
        
        self.battle.update(5.0)
        
        assert self.battle._elapsed_time == initial_time


class TestGameOverState:
    """Tests for GameOverState input handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PhaseManager()
        self.game_over = GameOverState(self.manager)
        self.lobby = LobbyState(self.manager)
        
        self.manager.register_state("GameOver", self.game_over)
        self.manager.register_state("Lobby", self.lobby)
        
        self.manager.transition_to("GameOver")
    
    def test_game_over_return_to_lobby_with_enter(self):
        """Test returning to lobby with Enter key."""
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = self.game_over.handle_input(event)
        
        assert result is True
        assert self.manager.current_phase_name == "Lobby"
    
    def test_game_over_return_to_lobby_with_space(self):
        """Test returning to lobby with Space key."""
        self.manager.transition_to("GameOver")
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        result = self.game_over.handle_input(event)
        
        assert result is True
        assert self.manager.current_phase_name == "Lobby"
    
    def test_game_over_return_to_lobby_with_click(self):
        """Test returning to lobby with mouse click."""
        self.manager.transition_to("GameOver")
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
        result = self.game_over.handle_input(event)
        
        assert result is True
        assert self.manager.current_phase_name == "Lobby"
    
    def test_game_over_set_results(self):
        """Test setting game over results."""
        self.game_over.set_results("Player1", 1000)
        
        assert self.game_over.winner == "Player1"
        assert self.game_over.final_score == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
