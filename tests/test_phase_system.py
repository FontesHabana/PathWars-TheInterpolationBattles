"""
Unit tests for Phase State and Phase Manager.

Tests the State Pattern implementation for game phases,
including phase transitions, control point constraints,
and round tracking.
"""

import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.phase_state import (
    PhaseType,
    GamePhaseState,
    PreparationPhaseState,
    PathModificationPhaseState,
    BuildingPhaseState,
    CombatPhaseState,
    RoundEndPhaseState,
    create_phase_state,
)
from core.phase_manager import (
    PhaseManager,
    InvalidPhaseTransitionError,
    ControlPointConstraintError,
)


class TestPhaseStates:
    """Test cases for individual phase states."""
    
    def test_preparation_state_permissions(self):
        """Test PreparationPhaseState action permissions."""
        state = PreparationPhaseState()
        
        assert state.phase_type == PhaseType.PREPARATION
        assert state.can_modify_path() is True
        assert state.can_place_tower() is False
        assert state.can_send_mercenaries() is False
        assert state.can_research() is False
    
    def test_preparation_state_transitions(self):
        """Test PreparationPhaseState allowed transitions."""
        state = PreparationPhaseState()
        
        allowed = state.get_allowed_transitions()
        assert PhaseType.BUILDING in allowed
        assert len(allowed) == 1
    
    def test_path_modification_state_permissions(self):
        """Test PathModificationPhaseState action permissions."""
        state = PathModificationPhaseState()
        
        assert state.phase_type == PhaseType.PATH_MODIFICATION
        assert state.can_modify_path() is True
        assert state.can_place_tower() is False
        assert state.can_send_mercenaries() is True
        assert state.can_research() is True
    
    def test_path_modification_state_transitions(self):
        """Test PathModificationPhaseState allowed transitions."""
        state = PathModificationPhaseState()
        
        allowed = state.get_allowed_transitions()
        assert PhaseType.BUILDING in allowed
    
    def test_building_state_permissions(self):
        """Test BuildingPhaseState action permissions."""
        state = BuildingPhaseState()
        
        assert state.phase_type == PhaseType.BUILDING
        assert state.can_modify_path() is False
        assert state.can_place_tower() is True
        assert state.can_send_mercenaries() is False
        assert state.can_research() is False
    
    def test_building_state_transitions(self):
        """Test BuildingPhaseState allowed transitions."""
        state = BuildingPhaseState()
        
        allowed = state.get_allowed_transitions()
        assert PhaseType.COMBAT in allowed
    
    def test_combat_state_permissions(self):
        """Test CombatPhaseState action permissions."""
        state = CombatPhaseState()
        
        assert state.phase_type == PhaseType.COMBAT
        assert state.can_modify_path() is False
        assert state.can_place_tower() is True  # Can build during combat
        assert state.can_send_mercenaries() is False
        assert state.can_research() is False
    
    def test_combat_state_transitions(self):
        """Test CombatPhaseState allowed transitions."""
        state = CombatPhaseState()
        
        allowed = state.get_allowed_transitions()
        assert PhaseType.ROUND_END in allowed
        assert PhaseType.PATH_MODIFICATION in allowed
    
    def test_round_end_state_permissions(self):
        """Test RoundEndPhaseState action permissions."""
        state = RoundEndPhaseState()
        
        assert state.phase_type == PhaseType.ROUND_END
        assert state.can_modify_path() is False
        assert state.can_place_tower() is False
        assert state.can_send_mercenaries() is False
        assert state.can_research() is False
    
    def test_round_end_state_transitions(self):
        """Test RoundEndPhaseState allowed transitions."""
        state = RoundEndPhaseState()
        
        allowed = state.get_allowed_transitions()
        assert PhaseType.PATH_MODIFICATION in allowed
    
    def test_phase_state_factory(self):
        """Test create_phase_state factory function."""
        prep_state = create_phase_state(PhaseType.PREPARATION)
        assert isinstance(prep_state, PreparationPhaseState)
        
        path_state = create_phase_state(PhaseType.PATH_MODIFICATION)
        assert isinstance(path_state, PathModificationPhaseState)
        
        build_state = create_phase_state(PhaseType.BUILDING)
        assert isinstance(build_state, BuildingPhaseState)
        
        combat_state = create_phase_state(PhaseType.COMBAT)
        assert isinstance(combat_state, CombatPhaseState)
        
        end_state = create_phase_state(PhaseType.ROUND_END)
        assert isinstance(end_state, RoundEndPhaseState)


class TestPhaseManager:
    """Test cases for PhaseManager."""
    
    def test_initialization(self):
        """Test PhaseManager initializes correctly."""
        manager = PhaseManager(max_rounds=5)
        
        assert manager.current_round == 1
        assert manager.max_rounds == 5
        assert manager.is_preparation_phase is True
        assert manager.current_phase.phase_type == PhaseType.PREPARATION
    
    def test_custom_max_rounds(self):
        """Test PhaseManager with custom max rounds."""
        manager = PhaseManager(max_rounds=7)
        
        assert manager.max_rounds == 7
        assert manager.is_match_complete() is False
    
    def test_preparation_phase_initial_points_limit(self):
        """Test that only 2 initial points can be placed during preparation."""
        manager = PhaseManager()
        
        # Should allow first point
        assert manager.can_add_control_point() is True
        manager.register_point_added(0)
        assert manager.initial_points_placed == 1
        
        # Should allow second point
        assert manager.can_add_control_point() is True
        manager.register_point_added(1)
        assert manager.initial_points_placed == 2
        
        # Should not allow third point
        assert manager.can_add_control_point() is False
        with pytest.raises(ControlPointConstraintError):
            manager.register_point_added(2)
    
    def test_preparation_phase_no_point_removal(self):
        """Test that points cannot be removed during preparation."""
        manager = PhaseManager()
        manager.register_point_added(0)
        
        # Cannot remove during preparation
        assert manager.can_remove_control_point(0) is False
    
    def test_initial_point_border_validation_start(self):
        """Test start point must be on left border (x=0)."""
        manager = PhaseManager()
        
        # Valid start point on left border
        manager.validate_initial_point_placement(
            x=0, y=10, grid_width=20, grid_height=20, is_start_point=True
        )
        
        # Invalid start point not on left border
        with pytest.raises(ControlPointConstraintError):
            manager.validate_initial_point_placement(
                x=5, y=10, grid_width=20, grid_height=20, is_start_point=True
            )
    
    def test_initial_point_border_validation_end(self):
        """Test end point must be on right border (x=grid_width-1)."""
        manager = PhaseManager()
        manager.register_point_added(0)  # Register start point first
        
        # Valid end point on right border
        manager.validate_initial_point_placement(
            x=19, y=10, grid_width=20, grid_height=20, is_start_point=False
        )
        
        # Invalid end point not on right border
        with pytest.raises(ControlPointConstraintError):
            manager.validate_initial_point_placement(
                x=15, y=10, grid_width=20, grid_height=20, is_start_point=False
            )
    
    def test_initial_point_y_bounds_validation(self):
        """Test that Y coordinate is validated for initial points."""
        manager = PhaseManager()
        
        # Valid Y coordinate
        manager.validate_initial_point_placement(
            x=0, y=15, grid_width=20, grid_height=20, is_start_point=True
        )
        
        # Invalid Y coordinate (too high)
        with pytest.raises(ControlPointConstraintError):
            manager.validate_initial_point_placement(
                x=0, y=25, grid_width=20, grid_height=20, is_start_point=True
            )
        
        # Invalid Y coordinate (negative)
        with pytest.raises(ControlPointConstraintError):
            manager.validate_initial_point_placement(
                x=0, y=-1, grid_width=20, grid_height=20, is_start_point=True
            )
    
    def test_valid_phase_transition_preparation_to_building(self):
        """Test valid transition from preparation to building."""
        manager = PhaseManager()
        
        manager.transition_to(PhaseType.BUILDING)
        
        assert manager.current_phase.phase_type == PhaseType.BUILDING
        assert manager.current_round == 1
    
    def test_valid_phase_transition_building_to_combat(self):
        """Test valid transition from building to combat."""
        manager = PhaseManager()
        manager.transition_to(PhaseType.BUILDING)
        
        manager.transition_to(PhaseType.COMBAT)
        
        assert manager.current_phase.phase_type == PhaseType.COMBAT
    
    def test_valid_phase_transition_combat_to_round_end(self):
        """Test valid transition from combat to round end."""
        manager = PhaseManager()
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        
        manager.transition_to(PhaseType.ROUND_END)
        
        assert manager.current_phase.phase_type == PhaseType.ROUND_END
        assert manager.current_round == 1  # Round increments when leaving round_end
    
    def test_valid_phase_transition_round_end_to_path_modification(self):
        """Test valid transition from round end to path modification."""
        manager = PhaseManager()
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        assert manager.current_phase.phase_type == PhaseType.PATH_MODIFICATION
        assert manager.current_round == 2  # Round incremented
    
    def test_invalid_phase_transition(self):
        """Test that invalid phase transitions are rejected."""
        manager = PhaseManager()
        
        # Cannot go from preparation directly to combat
        with pytest.raises(InvalidPhaseTransitionError):
            manager.transition_to(PhaseType.COMBAT)
    
    def test_path_modification_one_point_limit(self):
        """Test that only 1 point can be modified per round after preparation."""
        manager = PhaseManager()
        
        # Complete preparation phase
        manager.register_point_added(0)
        manager.register_point_added(1)
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        # Now in round 2 path modification
        assert manager.current_round == 2
        assert manager.points_modified_this_round == 0
        
        # Can add one point
        assert manager.can_add_control_point() is True
        manager.register_point_added(2)
        assert manager.points_modified_this_round == 1
        
        # Cannot add another point
        assert manager.can_add_control_point() is False
        with pytest.raises(ControlPointConstraintError):
            manager.register_point_added(3)
    
    def test_cannot_remove_points_from_previous_rounds(self):
        """Test that points from previous rounds cannot be removed."""
        manager = PhaseManager()
        
        # Place initial points in round 1
        manager.register_point_added(0)
        manager.register_point_added(1)
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        # Now in round 2 - cannot remove points from round 1
        assert manager.can_remove_control_point(0) is False
        assert manager.can_remove_control_point(1) is False
    
    def test_can_remove_points_from_current_round(self):
        """Test that points from current round can be removed."""
        manager = PhaseManager()
        
        # Complete preparation and get to round 2
        manager.register_point_added(0)
        manager.register_point_added(1)
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        # Add a point in round 2
        manager.register_point_added(2)
        
        # Should be able to remove it (before adding another)
        # But we've already used our 1 modification
        assert manager.can_remove_control_point(2) is False
    
    def test_modification_counter_resets_each_round(self):
        """Test that modification counter resets when entering new round."""
        manager = PhaseManager()
        
        # Round 1 preparation
        manager.register_point_added(0)
        manager.register_point_added(1)
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        # Round 2 - counter should be reset
        assert manager.points_modified_this_round == 0
        
        manager.register_point_added(2)
        assert manager.points_modified_this_round == 1
        
        # Move to round 3
        manager.transition_to(PhaseType.BUILDING)
        manager.transition_to(PhaseType.COMBAT)
        manager.transition_to(PhaseType.ROUND_END)
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        # Counter should be reset again
        assert manager.points_modified_this_round == 0
    
    def test_match_completion(self):
        """Test match completion detection."""
        manager = PhaseManager(max_rounds=3)
        
        assert manager.is_match_complete() is False
        
        # Complete 3 rounds
        for round_num in range(3):
            if round_num > 0:
                manager.transition_to(PhaseType.PATH_MODIFICATION)
            else:
                # First round starts in preparation
                pass
            
            manager.transition_to(PhaseType.BUILDING)
            manager.transition_to(PhaseType.COMBAT)
            manager.transition_to(PhaseType.ROUND_END)
        
        # After round 3 ends, transitioning to next round should increment past max
        manager.transition_to(PhaseType.PATH_MODIFICATION)
        
        assert manager.is_match_complete() is True
    
    def test_reset(self):
        """Test PhaseManager reset functionality."""
        manager = PhaseManager(max_rounds=5)
        
        # Make some progress
        manager.register_point_added(0)
        manager.register_point_added(1)
        manager.transition_to(PhaseType.BUILDING)
        
        # Reset
        manager.reset()
        
        assert manager.current_round == 1
        assert manager.max_rounds == 5
        assert manager.is_preparation_phase is True
        assert manager.initial_points_placed == 0
        assert manager.points_modified_this_round == 0
    
    def test_reset_with_new_max_rounds(self):
        """Test PhaseManager reset with new max rounds."""
        manager = PhaseManager(max_rounds=5)
        
        manager.reset(max_rounds=7)
        
        assert manager.max_rounds == 7
        assert manager.current_round == 1
