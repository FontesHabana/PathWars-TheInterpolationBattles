"""
Input Handler module for PathWars - The Interpolation Battles.

Processes raw Pygame events and translates them into GameState actions.
"""

import pygame
from typing import Optional, Tuple

from core.game_state import GameState, GamePhase, InsufficientFundsError
from core.grid import Grid
from graphics.renderer import Renderer
from entities.tower import TowerType
from entities.factory import EntityFactory

# Tower costs by type
TOWER_COSTS = {
    TowerType.DEAN: 50,
    TowerType.CALCULUS: 75,
    TowerType.PHYSICS: 100,
    TowerType.STATISTICS: 60,
}

class InputHandler:
    """
    Handles user input.
    """

    def __init__(self, game_state: GameState, grid: Grid, renderer: Renderer):
        self.game_state = game_state
        self.grid = grid
        self.renderer = renderer
        
        # State for "Place Tower" mode (placeholder for UI logic)
        self.selected_tower_type: Optional[TowerType] = TowerType.DEAN

    def handle_input(self) -> bool:
        """
        Process events. Returns False if quit is requested.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    self._handle_left_click(event.pos)
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
                
        return True

    def _handle_left_click(self, screen_pos: Tuple[int, int]):
        """Handle left mouse click."""
        # Convert screen pos to grid pos
        grid_x, grid_y = self.renderer.iso_to_cart(*screen_pos)
        
        # Check bounds
        if not self.grid.is_valid_position(grid_x, grid_y):
            return

        # LOGIC: If in Planning phase and has money, try place tower
        if self.game_state.current_phase == GamePhase.PLANNING:
            self._try_place_tower(grid_x, grid_y)

    def _try_place_tower(self, x: int, y: int):
        """Attempt to place a tower at grid coordinates."""
        if self.grid.is_occupied(x, y):
            print(f"Cell {x},{y} is occupied")
            return
        
        # Check tower cost
        cost = TOWER_COSTS.get(self.selected_tower_type, 50)
        
        try:
            # Deduct money first
            self.game_state.deduct_money(cost)
            
            # Create and place tower
            tower = EntityFactory.create_tower(self.selected_tower_type, (x, y))
            self.game_state.add_entity('towers', tower)
            self.grid.set_occupied(x, y, True)
            print(f"Placed {self.selected_tower_type.name} tower at {x},{y} for ${cost}")
        except InsufficientFundsError:
            print(f"Not enough money! Need ${cost}, have ${self.game_state.money}")
        except Exception as e:
            print(f"Failed to place tower: {e}")

    def _handle_keydown(self, key):
        """Handle keyboard input for debug/prototyping."""
        # T: Cycle tower types
        if key == pygame.K_t:
            types = list(TowerType)
            curr_idx = types.index(self.selected_tower_type)
            next_idx = (curr_idx + 1) % len(types)
            self.selected_tower_type = types[next_idx]
            print(f"Selected tower: {self.selected_tower_type.name}")
            
        # SPACE: Toggle Phase (Planning <-> Battle)
        if key == pygame.K_SPACE:
            curr = self.game_state.current_phase
            new = GamePhase.BATTLE if curr == GamePhase.PLANNING else GamePhase.PLANNING
            try:
                self.game_state.change_phase(new)
                print(f"Changed phase to {new.name}")
            except Exception as e:
                print(f"Cannot change phase: {e}")
