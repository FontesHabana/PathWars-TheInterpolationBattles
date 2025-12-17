"""
Unit tests for Grid and GameState modules.
"""

import pytest
import sys
import os

# Add src to path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.grid import Grid
from core.game_state import (
    GameState,
    GamePhase,
    InsufficientFundsError,
    InvalidPhaseTransitionError,
)


class TestGrid:
    """Test cases for the Grid class."""
    
    def test_grid_initialization(self):
        """Test that grid initializes with correct dimensions."""
        grid = Grid(width=10, height=8, cell_size=32)
        
        assert grid.width == 10
        assert grid.height == 8
        assert grid.cell_size == 32
    
    def test_to_grid_coords_basic(self):
        """Test basic screen to grid coordinate conversion."""
        grid = Grid(width=10, height=10, cell_size=50)
        
        # Point at origin
        assert grid.to_grid_coords(0, 0) == (0, 0)
        
        # Point in first cell
        assert grid.to_grid_coords(25, 25) == (0, 0)
        
        # Point exactly at cell boundary
        assert grid.to_grid_coords(50, 50) == (1, 1)
        
        # Point in middle of grid
        assert grid.to_grid_coords(125, 175) == (2, 3)
    
    def test_to_grid_coords_edge_cases(self):
        """Test screen to grid conversion at boundaries."""
        grid = Grid(width=5, height=5, cell_size=100)
        
        # Just before cell boundary
        assert grid.to_grid_coords(99, 99) == (0, 0)
        
        # Large coordinates
        assert grid.to_grid_coords(450, 350) == (4, 3)
    
    def test_is_valid_position(self):
        """Test position validation within grid bounds."""
        grid = Grid(width=5, height=5, cell_size=32)
        
        # Valid positions
        assert grid.is_valid_position(0, 0) is True
        assert grid.is_valid_position(4, 4) is True
        assert grid.is_valid_position(2, 2) is True
        
        # Invalid positions (outside bounds)
        assert grid.is_valid_position(-1, 0) is False
        assert grid.is_valid_position(0, -1) is False
        assert grid.is_valid_position(5, 0) is False
        assert grid.is_valid_position(0, 5) is False
        assert grid.is_valid_position(10, 10) is False
    
    def test_is_occupied_empty_grid(self):
        """Test that new grid has no occupied cells."""
        grid = Grid(width=5, height=5, cell_size=32)
        
        assert grid.is_occupied(0, 0) is False
        assert grid.is_occupied(2, 2) is False
        assert grid.is_occupied(4, 4) is False
    
    def test_is_occupied_outside_bounds(self):
        """Test that positions outside bounds are considered occupied."""
        grid = Grid(width=5, height=5, cell_size=32)
        
        # Positions outside grid should be considered occupied
        assert grid.is_occupied(-1, 0) is True
        assert grid.is_occupied(0, -1) is True
        assert grid.is_occupied(5, 0) is True
        assert grid.is_occupied(0, 5) is True
    
    def test_set_occupied(self):
        """Test setting and unsetting occupied cells."""
        grid = Grid(width=5, height=5, cell_size=32)
        
        # Set a cell as occupied
        result = grid.set_occupied(2, 2)
        assert result is True
        assert grid.is_occupied(2, 2) is True
        
        # Unset the cell
        result = grid.set_occupied(2, 2, occupied=False)
        assert result is True
        assert grid.is_occupied(2, 2) is False
    
    def test_set_occupied_outside_bounds(self):
        """Test that setting occupied outside bounds fails."""
        grid = Grid(width=5, height=5, cell_size=32)
        
        result = grid.set_occupied(-1, 0)
        assert result is False
        
        result = grid.set_occupied(5, 5)
        assert result is False
    
    def test_get_occupied_cells_returns_copy(self):
        """Test that get_occupied_cells returns a copy."""
        grid = Grid(width=5, height=5, cell_size=32)
        grid.set_occupied(1, 1)
        grid.set_occupied(2, 2)
        
        occupied = grid.get_occupied_cells()
        assert occupied == {(1, 1), (2, 2)}
        
        # Modifying the returned set should not affect the grid
        occupied.add((3, 3))
        assert grid.is_occupied(3, 3) is False


class TestGameState:
    """Test cases for the GameState class."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        GameState.reset_instance()
    
    def test_singleton_pattern(self):
        """Test that GameState is a singleton."""
        state1 = GameState()
        state2 = GameState()
        
        assert state1 is state2
    
    def test_initial_values(self):
        """Test initial game state values."""
        state = GameState()
        
        assert state.money == 100
        assert state.lives == 10
        assert state.current_phase == GamePhase.PLANNING
    
    def test_deduct_money_success(self):
        """Test successful money deduction."""
        state = GameState()
        initial_money = state.money
        
        state.deduct_money(50)
        assert state.money == initial_money - 50
    
    def test_deduct_money_insufficient_funds(self):
        """Test that deducting more than available raises error."""
        state = GameState()
        
        with pytest.raises(InsufficientFundsError):
            state.deduct_money(state.money + 1)
    
    def test_deduct_money_negative_amount(self):
        """Test that deducting negative amount raises error."""
        state = GameState()
        
        with pytest.raises(ValueError):
            state.deduct_money(-10)
    
    def test_add_money(self):
        """Test adding money."""
        state = GameState()
        initial_money = state.money
        
        state.add_money(50)
        assert state.money == initial_money + 50
    
    def test_add_money_negative_amount(self):
        """Test that adding negative amount raises error."""
        state = GameState()
        
        with pytest.raises(ValueError):
            state.add_money(-10)
    
    def test_change_phase_valid_transition(self):
        """Test valid phase transitions."""
        state = GameState()
        
        # PLANNING -> WAITING
        state.change_phase(GamePhase.WAITING)
        assert state.current_phase == GamePhase.WAITING
        
        # WAITING -> BATTLE
        state.change_phase(GamePhase.BATTLE)
        assert state.current_phase == GamePhase.BATTLE
        
        # BATTLE -> RESULT
        state.change_phase(GamePhase.RESULT)
        assert state.current_phase == GamePhase.RESULT
        
        # RESULT -> PLANNING
        state.change_phase(GamePhase.PLANNING)
        assert state.current_phase == GamePhase.PLANNING
    
    def test_change_phase_invalid_transition(self):
        """Test invalid phase transitions raise error."""
        state = GameState()
        
        # Cannot go from PLANNING directly to BATTLE
        with pytest.raises(InvalidPhaseTransitionError):
            state.change_phase(GamePhase.BATTLE)
        
        # Cannot go from PLANNING directly to RESULT
        with pytest.raises(InvalidPhaseTransitionError):
            state.change_phase(GamePhase.RESULT)
    
    def test_lose_life(self):
        """Test losing lives."""
        state = GameState()
        initial_lives = state.lives
        
        result = state.lose_life()
        assert result is True
        assert state.lives == initial_lives - 1
    
    def test_lose_life_game_over(self):
        """Test that losing all lives returns False."""
        state = GameState()
        
        # Lose all but one life
        while state.lives > 1:
            assert state.lose_life() is True
        
        # Lose last life
        result = state.lose_life()
        assert result is False
        assert state.lives == 0
    
    def test_entities_collection_returns_copy(self):
        """Test that entities_collection returns a copy."""
        state = GameState()
        
        entities = state.entities_collection
        entities['towers'].append('fake_tower')
        
        # Original should not be modified
        assert len(state.entities_collection['towers']) == 0
    
    def test_add_entity(self):
        """Test adding entities."""
        state = GameState()
        
        state.add_entity('towers', 'tower1')
        state.add_entity('towers', 'tower2')
        state.add_entity('enemies', 'enemy1')
        
        entities = state.entities_collection
        assert len(entities['towers']) == 2
        assert len(entities['enemies']) == 1
    
    def test_remove_entity(self):
        """Test removing entities."""
        state = GameState()
        
        state.add_entity('towers', 'tower1')
        state.add_entity('towers', 'tower2')
        
        result = state.remove_entity('towers', 'tower1')
        assert result is True
        assert len(state.entities_collection['towers']) == 1
    
    def test_remove_entity_not_found(self):
        """Test removing non-existent entity."""
        state = GameState()
        
        result = state.remove_entity('towers', 'nonexistent')
        assert result is False


class TestGamePhases:
    """Test cases for game phase logic."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        GameState.reset_instance()
    
    def test_all_phases_enum(self):
        """Test that all required phases exist."""
        assert GamePhase.PLANNING
        assert GamePhase.WAITING
        assert GamePhase.BATTLE
        assert GamePhase.RESULT
    
    def test_battle_to_planning_transition(self):
        """Test that battle can transition back to planning."""
        state = GameState()
        
        # Go through the phases
        state.change_phase(GamePhase.WAITING)
        state.change_phase(GamePhase.BATTLE)
        
        # Can go back to planning from battle (for next round)
        state.change_phase(GamePhase.PLANNING)
        assert state.current_phase == GamePhase.PLANNING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
