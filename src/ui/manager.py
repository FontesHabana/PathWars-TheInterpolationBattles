"""
UI Manager module for PathWars.

Manages all UI panels and handles event delegation.
"""

import pygame
from typing import List

from ui.components import Button, Panel, Label
from core.game_state import GameState, GamePhase
from entities.tower import TowerType


class UIManager:
    """
    Manages all UI elements and their interactions.
    """

    def __init__(self, screen_width: int, screen_height: int, game_state: GameState):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_state = game_state
        self.panels: List[Panel] = []

        # Track currently selected tower type for placement
        self.selected_tower_type: TowerType = TowerType.DEAN

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

        # Phase button
        btn = Button(
            "Start Battle",
            pygame.Rect(panel_x + 10, panel_y + 30, 180, 35),
            self._toggle_phase,
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
        )
        panel.add(btn)

        self.panels.append(panel)

    def _select_tower(self, tower_type: TowerType):
        """Callback when a tower button is clicked."""
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

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Pass event to UI elements. Returns True if event was consumed.
        """
        for panel in self.panels:
            if panel.handle_event(event):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw all UI panels."""
        for panel in self.panels:
            panel.draw(screen)

        # Draw selected tower indicator
        font = pygame.font.SysFont("Arial", 18)
        text = f"Placing: {self.selected_tower_type.name}"
        surf = font.render(text, True, (200, 200, 200))
        screen.blit(surf, (20, self.screen_height - 30))
