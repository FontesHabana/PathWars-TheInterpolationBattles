"""
Mercenary Panel UI for PathWars - The Interpolation Battles.

Provides UI for sending mercenaries to the opponent in multiplayer mode.
"""

import pygame
from typing import Optional, Callable

from ui.components import Button, Panel, Label
from entities.mercenaries.mercenary_types import MercenaryType


class MercenaryPanel:
    """
    UI Panel for sending mercenaries in multiplayer mode.
    
    Shows buttons for each mercenary type with their cost.
    Only visible during multiplayer games.
    """

    # Constants
    PANEL_WIDTH = 200
    PANEL_HEIGHT = 200
    
    # Mercenary costs (as specified in problem statement)
    MERCENARY_COSTS = {
        MercenaryType.REINFORCED_STUDENT: 30,
        MercenaryType.SPEEDY_VARIABLE_X: 40,
        MercenaryType.TANK_CONSTANT_PI: 60,
    }

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_send_mercenary: Optional[Callable[[MercenaryType], bool]] = None
    ) -> None:
        """
        Initialize the mercenary panel.
        
        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            on_send_mercenary: Callback function called when a mercenary is sent.
                              Should return True if sending succeeded.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_send_mercenary = on_send_mercenary

        self._visible: bool = False

        # Position panel on the left side, below curve editor
        self.panel_x = 20
        self.panel_y = 420

        # Build panel
        self._build_panel()

    def _build_panel(self) -> None:
        """Build the mercenary panel with buttons."""
        self.panel = Panel(
            pygame.Rect(self.panel_x, self.panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )

        y_offset = self.panel_y + 10

        # Title
        self.panel.add(Label(
            "Mercenaries",
            (self.panel_x + 10, y_offset),
            font_size=22
        ))
        y_offset += 35

        # Reinforced Student button
        btn_student = Button(
            "Reinforced Student ($30)",
            pygame.Rect(
                self.panel_x + 10,
                y_offset,
                self.PANEL_WIDTH - 20,
                30
            ),
            lambda: self._send_mercenary(MercenaryType.REINFORCED_STUDENT),
            bg_color=(100, 50, 50),
            hover_color=(150, 80, 80),
        )
        self.panel.add(btn_student)
        y_offset += 40

        # Speedy Variable X button
        btn_speedy = Button(
            "Speedy Variable X ($40)",
            pygame.Rect(
                self.panel_x + 10,
                y_offset,
                self.PANEL_WIDTH - 20,
                30
            ),
            lambda: self._send_mercenary(MercenaryType.SPEEDY_VARIABLE_X),
            bg_color=(50, 50, 100),
            hover_color=(80, 80, 150),
        )
        self.panel.add(btn_speedy)
        y_offset += 40

        # Tank Constant Pi button
        btn_tank = Button(
            "Tank Constant Pi ($60)",
            pygame.Rect(
                self.panel_x + 10,
                y_offset,
                self.PANEL_WIDTH - 20,
                30
            ),
            lambda: self._send_mercenary(MercenaryType.TANK_CONSTANT_PI),
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
        )
        self.panel.add(btn_tank)

    def _send_mercenary(self, mercenary_type: MercenaryType) -> None:
        """
        Handle sending a mercenary.
        
        Args:
            mercenary_type: Type of mercenary to send.
        """
        if self.on_send_mercenary:
            success = self.on_send_mercenary(mercenary_type)
            if success:
                print(f"[MercenaryPanel] Sent {mercenary_type.name}")
            else:
                print(f"[MercenaryPanel] Failed to send {mercenary_type.name}")

    @property
    def visible(self) -> bool:
        """Check if the panel is visible."""
        return self._visible

    def show(self) -> None:
        """Show the mercenary panel."""
        self._visible = True

    def hide(self) -> None:
        """Hide the mercenary panel."""
        self._visible = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: Pygame event to handle.
            
        Returns:
            True if event was consumed by the panel, False otherwise.
        """
        if not self._visible:
            return False

        return self.panel.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the panel to the screen.
        
        Args:
            screen: Pygame surface to draw on.
        """
        if not self._visible:
            return

        self.panel.draw(screen)
