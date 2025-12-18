"""
UI Manager module for PathWars.

Manages all UI panels and handles event delegation.
"""

import pygame
from typing import List, Optional, Tuple

from ui.components import Button, Panel, Label
from ui.tower_info_panel import TowerInfoPanel
from ui.mercenary_panel import MercenaryPanel
from core.game_state import GameState, GamePhase
from entities.tower import Tower, TowerType
from entities.mercenaries.mercenary_types import MercenaryType


class UIManager:
    """
    Manages all UI elements and their interactions.
    """

    def __init__(self, screen_width: int, screen_height: int, game_state: GameState):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_state = game_state
        self.panels: List[Panel] = []

        # Track currently selected tower type for placement (None = no tower selected)
        self.selected_tower_type: Optional[TowerType] = None

        # Track mouse position for tower preview
        self._mouse_grid_pos: Optional[Tuple[int, int]] = None
        
        # Track phase button for dynamic updates
        self._phase_button: Optional[Button] = None

        # Tower info panel for displaying selected tower details
        self.tower_info_panel = TowerInfoPanel(
            screen_width,
            screen_height,
            on_upgrade_callback=self._on_tower_upgrade
        )

        # Mercenary panel for multiplayer
        self.mercenary_panel = MercenaryPanel(
            screen_width,
            screen_height,
            on_send_mercenary=self._on_send_mercenary
        )

        self._build_shop_panel()
        self._build_phase_panel()

    def _build_shop_panel(self):
        """Create the tower shop panel."""
        panel_width = 200
        panel_height = 250
        panel_x = self.screen_width - panel_width - 20
        panel_y = 20

        panel = Panel(pygame.Rect(panel_x, panel_y, panel_width, panel_height))

        # Title
        panel.add(Label("Tower Shop", (panel_x + 10, panel_y + 10), font_size=22))

        # Tower buttons
        tower_data = [
            (TowerType.DEAN, "Dean ($50)", (panel_x + 10, panel_y + 50)),
            (TowerType.CALCULUS, "Calculus ($75)", (panel_x + 10, panel_y + 90)),
            (TowerType.PHYSICS, "Physics ($100)", (panel_x + 10, panel_y + 130)),
            (TowerType.STATISTICS, "Statistics ($60)", (panel_x + 10, panel_y + 170)),
        ]

        for tower_type, text, pos in tower_data:
            btn = Button(
                text,
                pygame.Rect(pos[0], pos[1], 180, 30),
                lambda tt=tower_type: self._select_tower(tt),
            )
            panel.add(btn)

        self.panels.append(panel)

    def _build_phase_panel(self):
        """Create the phase control panel."""
        panel_width = 200
        panel_height = 80
        panel_x = self.screen_width - panel_width - 20
        panel_y = self.screen_height - panel_height - 20

        panel = Panel(pygame.Rect(panel_x, panel_y, panel_width, panel_height))

        # Phase button - store reference for dynamic updates
        self._phase_button = Button(
            "Start Battle",
            pygame.Rect(panel_x + 10, panel_y + 30, 180, 35),
            self._toggle_phase,
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
        )
        panel.add(self._phase_button)

        self.panels.append(panel)
    
    def _update_phase_button(self):
        """Update phase button based on current game phase."""
        if self._phase_button is None:
            return
        
        if self.game_state.current_phase == GamePhase.PLANNING:
            # During PLANNING: Show "Start Battle" button
            self._phase_button.text = "Start Battle"
            self._phase_button.bg_color = (50, 100, 50)
            self._phase_button.hover_color = (80, 150, 80)
            self._phase_button.enabled = True
        elif self.game_state.current_phase == GamePhase.BATTLE:
            # During BATTLE: Show "Battle in Progress..." and disable
            self._phase_button.text = "Battle in Progress..."
            self._phase_button.bg_color = (80, 80, 80)
            self._phase_button.hover_color = (80, 80, 80)
            self._phase_button.enabled = False
        else:
            # Other phases: disable button
            self._phase_button.enabled = False

    def _select_tower(self, tower_type: TowerType):
        """
        Callback when a tower button is clicked.
        
        Implements toggle behavior: clicking the same tower type deselects it.
        """
        if self.selected_tower_type == tower_type:
            # Toggle off - deselect
            self.selected_tower_type = None
            print(f"[UI] Deselected tower")
        else:
            # Select new tower type
            self.selected_tower_type = tower_type
            print(f"[UI] Selected tower: {tower_type.name}")

    def _toggle_phase(self):
        """Toggle between Planning and Battle phases."""
        try:
            if self.game_state.current_phase == GamePhase.PLANNING:
                self.game_state.change_phase(GamePhase.WAITING)
                self.game_state.change_phase(GamePhase.BATTLE)
                print("[UI] Phase changed to BATTLE")
            elif self.game_state.current_phase == GamePhase.BATTLE:
                self.game_state.change_phase(GamePhase.PLANNING)
                print("[UI] Phase changed to PLANNING")
        except Exception as e:
            print(f"[UI] Cannot change phase: {e}")

    def _on_tower_upgrade(self, tower: Tower) -> bool:
        """
        Handle tower upgrade request.
        
        Args:
            tower: The tower to upgrade.
            
        Returns:
            True if upgrade was successful, False otherwise.
        """
        if not tower.can_upgrade:
            print("[UI] Tower is already at max level")
            return False
        
        cost = tower.upgrade_cost
        
        # Check if player has enough money
        if self.game_state.money < cost:
            print(f"[UI] Not enough money! Need ${cost}, have ${self.game_state.money}")
            return False
        
        # Deduct money
        try:
            self.game_state.deduct_money(cost)
        except Exception as e:
            print(f"[UI] Failed to deduct money: {e}")
            return False
        
        # Upgrade tower
        success = tower.upgrade()
        if success:
            print(f"[UI] Upgraded {tower.tower_type.name} to {tower.level.name} for ${cost}")
        else:
            # Refund if upgrade failed
            self.game_state.add_money(cost)
            print("[UI] Tower upgrade failed")
        
        return success

    def _on_send_mercenary(self, mercenary_type: MercenaryType) -> bool:
        """
        Handle mercenary sending request.
        
        Args:
            mercenary_type: The type of mercenary to send.
            
        Returns:
            True if mercenary was sent successfully, False otherwise.
        """
        # Get cost
        cost = MercenaryPanel.MERCENARY_COSTS.get(mercenary_type, 0)
        
        # Check if player has enough money
        if self.game_state.money < cost:
            print(f"[UI] Not enough money! Need ${cost}, have ${self.game_state.money}")
            return False
        
        # Deduct money
        try:
            self.game_state.deduct_money(cost)
        except Exception as e:
            print(f"[UI] Failed to deduct money: {e}")
            return False
        
        print(f"[UI] Sent {mercenary_type.name} mercenary for ${cost}")
        # Note: Actual sending through network would happen here via DuelSession/SyncEngine
        # For now, we just deduct the money and return success
        return True

    def set_multiplayer_mode(self, is_multiplayer: bool) -> None:
        """
        Set whether the game is in multiplayer mode.
        
        Args:
            is_multiplayer: True if in multiplayer mode, False otherwise.
        """
        if is_multiplayer:
            self.mercenary_panel.show()
        else:
            self.mercenary_panel.hide()

    def select_tower(self, tower: Optional[Tower]) -> None:
        """
        Select a tower to display in the info panel.
        
        Args:
            tower: Tower to select, or None to deselect.
        """
        self.tower_info_panel.select_tower(tower)

    def update_mouse_position(self, screen_pos: Tuple[int, int], renderer) -> None:
        """
        Update the mouse position for tower preview.
        
        Args:
            screen_pos: Screen position of the mouse.
            renderer: Renderer instance for coordinate conversion.
        """
        # Convert screen pos to grid pos
        grid_x, grid_y = renderer.iso_to_cart(*screen_pos)
        
        # Check if position is valid
        from core.grid import Grid
        if hasattr(renderer, 'grid'):
            grid: Grid = renderer.grid
            if grid.is_valid_position(grid_x, grid_y):
                self._mouse_grid_pos = (grid_x, grid_y)
            else:
                self._mouse_grid_pos = None
        else:
            self._mouse_grid_pos = None

    def draw_tower_preview(self, screen: pygame.Surface, renderer) -> None:
        """
        Draw tower preview under mouse cursor.
        
        Args:
            screen: Pygame surface to draw on.
            renderer: Renderer instance for coordinate conversion and sprite access.
        """
        # Don't show preview if no tower selected
        if self.selected_tower_type is None:
            return
        
        # Don't show preview if mouse not on valid grid position
        if self._mouse_grid_pos is None:
            return
        
        # Don't show preview during battle phase
        if self.game_state.current_phase != GamePhase.PLANNING:
            return
        
        grid_x, grid_y = self._mouse_grid_pos
        
        # Determine if position is valid (not occupied)
        from core.grid import Grid
        grid: Grid = renderer.grid
        is_valid = not grid.is_occupied(grid_x, grid_y)
        
        # Choose tint color based on validity
        if is_valid:
            tint_color = (100, 255, 100)  # Green
        else:
            tint_color = (255, 100, 100)  # Red
        
        # Get screen position
        screen_pos = renderer.cart_to_iso(grid_x, grid_y)
        
        # Get sprite for tower type
        from graphics.assets import AssetManager
        
        # Map tower type to sprite name (using actual tower sprite names)
        sprite_name_map = {
            TowerType.DEAN: "dean_idle",
            TowerType.CALCULUS: "calculus_idle",
            TowerType.PHYSICS: "physics_idle",
            TowerType.STATISTICS: "statistics_idle",
        }
        
        sprite_name = sprite_name_map.get(self.selected_tower_type, "dean_idle")
        sprite = AssetManager.get_sprite(sprite_name)
        
        if sprite:
            # Draw with tint and transparency
            draw_pos = (screen_pos[0], screen_pos[1] - renderer.TOWER_OFFSET_Y)
            renderer.draw_sprite_with_tint(sprite, draw_pos, tint_color, alpha=128)
        else:
            # Fallback: draw a semi-transparent circle
            draw_pos = (screen_pos[0], screen_pos[1] - renderer.TOWER_OFFSET_Y)
            circle_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*tint_color, 128), (20, 20), 15)
            screen.blit(circle_surface, (draw_pos[0] - 20, draw_pos[1] - 20))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Pass event to UI elements. Returns True if event was consumed.
        """
        # Tower info panel gets first priority
        if self.tower_info_panel.handle_event(event):
            return True
        
        # Mercenary panel gets second priority
        if self.mercenary_panel.handle_event(event):
            return True
        
        for panel in self.panels:
            if panel.handle_event(event):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw all UI panels."""
        # Update phase button state before drawing
        self._update_phase_button()
        
        for panel in self.panels:
            panel.draw(screen)

        # Draw mercenary panel
        self.mercenary_panel.draw(screen)

        # Draw tower info panel on top
        self.tower_info_panel.draw(screen)

        # Draw selected tower indicator
        font = pygame.font.SysFont("Arial", 18)
        if self.selected_tower_type is None:
            text = "No tower selected"
            color = (150, 150, 150)
        else:
            text = f"Placing: {self.selected_tower_type.name}"
            color = (200, 200, 200)
        surf = font.render(text, True, color)
        screen.blit(surf, (20, self.screen_height - 30))
