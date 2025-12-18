"""
Input Handler module for PathWars - The Interpolation Battles.

Processes raw Pygame events and translates them into GameState actions.
"""

import pygame
from typing import Callable, Optional, Tuple

from core.game_state import GameState, GamePhase, InsufficientFundsError
from core.grid import Grid
from graphics.renderer import Renderer
from entities.tower import Tower, TowerType
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
        self.selected_tower_type: Optional[TowerType] = None
        
        # Tower selection state
        self._selected_tower: Optional[Tower] = None
        self.on_tower_selected: Optional[Callable[[Optional[Tower]], None]] = None

    @property
    def selected_tower(self) -> Optional[Tower]:
        """Get the currently selected tower."""
        return self._selected_tower

    def handle_input(self) -> bool:
        """
        Process events. Returns False if quit is requested.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check for Shift+Click for tower selection
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        self._handle_tower_select_click(event.pos)
                    else:
                        self._handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self._handle_right_click(event.pos)
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
                
        return True

    def select_tower(self, tower: Optional[Tower]) -> None:
        """
        Select a tower.
        
        Args:
            tower: Tower to select, or None to deselect.
        """
        self._selected_tower = tower
        if self.on_tower_selected:
            self.on_tower_selected(tower)

    def deselect_tower(self) -> None:
        """Deselect the currently selected tower."""
        self.select_tower(None)

    def _find_tower_at(self, grid_x: int, grid_y: int) -> Optional[Tower]:
        """
        Find a tower at the given grid coordinates.
        
        Args:
            grid_x: Grid X coordinate.
            grid_y: Grid Y coordinate.
            
        Returns:
            Tower at that position, or None if no tower found.
        """
        towers = self.game_state.entities_collection.get('towers', [])
        for tower in towers:
            tower_x = int(tower.position.x)
            tower_y = int(tower.position.y)
            if tower_x == grid_x and tower_y == grid_y:
                return tower
        return None

    def _handle_right_click(self, screen_pos: Tuple[int, int]) -> None:
        """
        Handle right mouse click for tower selection.
        
        Args:
            screen_pos: Screen position of the click.
        """
        # Convert screen pos to grid pos
        grid_x, grid_y = self.renderer.iso_to_cart(*screen_pos)
        
        # Check bounds
        if not self.grid.is_valid_position(grid_x, grid_y):
            return
        
        # Find tower at position
        tower = self._find_tower_at(grid_x, grid_y)
        if tower:
            self.select_tower(tower)
            print(f"[Input] Selected {tower.tower_type.name} tower at ({grid_x}, {grid_y})")
        else:
            self.deselect_tower()

    def _handle_tower_select_click(self, screen_pos: Tuple[int, int]) -> None:
        """
        Handle Shift+Left click for tower selection.
        
        Args:
            screen_pos: Screen position of the click.
        """
        self._handle_right_click(screen_pos)

    def _handle_left_click(self, screen_pos: Tuple[int, int]):
        """Handle left mouse click."""
        # Convert screen pos to grid pos
        grid_x, grid_y = self.renderer.iso_to_cart(*screen_pos)
        
        # Check bounds
        if not self.grid.is_valid_position(grid_x, grid_y):
            return

        # Check if there's already a tower at this position
        existing_tower = self._find_tower_at(grid_x, grid_y)
        
        if existing_tower:
            # Select the existing tower to show info panel
            self.select_tower(existing_tower)
            print(f"[Input] Selected {existing_tower.tower_type.name} tower at ({grid_x}, {grid_y})")
            return

        # If clicked on empty area with a tower selected for placement, deselect
        if self.selected_tower_type is not None:
            # Try to place tower
            if self.game_state.current_phase == GamePhase.PLANNING:
                self._try_place_tower(grid_x, grid_y)
        # If no tower selected and clicked empty area, do nothing (already deselected)

    def _try_place_tower(self, x: int, y: int):
        """Attempt to place a tower at grid coordinates."""
        # Check if we have a tower type selected
        if self.selected_tower_type is None:
            return
            
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
        # ESC: Deselect tower
        if key == pygame.K_ESCAPE:
            self.deselect_tower()
            print("[Input] Tower deselected")
            return
        
        # U: Debug upgrade shortcut
        if key == pygame.K_u:
            if self._selected_tower and self._selected_tower.can_upgrade:
                success = self._selected_tower.upgrade()
                if success:
                    print(f"[Input] DEBUG: Upgraded tower to {self._selected_tower.level.name}")
                    # Notify callback to refresh UI
                    if self.on_tower_selected:
                        self.on_tower_selected(self._selected_tower)
            return
        
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
