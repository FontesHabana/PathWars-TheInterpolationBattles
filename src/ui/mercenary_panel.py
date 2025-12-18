"""
Mercenary Panel UI for PathWars - The Interpolation Battles.

Displays available mercenaries that can be sent to the opponent in multiplayer.
"""

import pygame
from typing import Optional, Callable

from ui.components import Button, Panel, Label
from entities.mercenaries.mercenary_types import MercenaryType
from entities.mercenaries.mercenary_factory import MercenaryFactory


class MercenaryPanel:
    """
    UI Panel for sending mercenaries to opponent (multiplayer only).
    
    Shows:
    - Available mercenary types
    - Costs for each mercenary
    - Send buttons
    - Only visible in multiplayer mode
    """

    # Constants
    PANEL_WIDTH = 220
    PANEL_HEIGHT = 220

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_send_callback: Optional[Callable[[MercenaryType], bool]] = None
    ) -> None:
        """
        Initialize the mercenary panel.
        
        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            on_send_callback: Callback function called when send button is clicked.
                            Should return True if send succeeded.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_send_callback = on_send_callback

        self._visible: bool = False

        # Position panel in bottom-right (above phase panel)
        self.panel_x = screen_width - self.PANEL_WIDTH - 20
        self.panel_y = screen_height - self.PANEL_HEIGHT - 120  # 120 to leave space for phase panel

        # Build panel
        self._build_panel()

    def _build_panel(self) -> None:
        """Build the mercenary panel with buttons."""
        self.panel = Panel(
            pygame.Rect(self.panel_x, self.panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )

        # Title
        self.panel.add(Label(
            "Send Mercenaries",
            (self.panel_x + 10, self.panel_y + 10),
            font_size=20
        ))

        # Get mercenary data
        mercenary_data = [
            (MercenaryType.REINFORCED_STUDENT, "Reinforced ($100)", self.panel_y + 50),
            (MercenaryType.SPEEDY_VARIABLE_X, "Speedy ($75)", self.panel_y + 90),
            (MercenaryType.TANK_CONSTANT_PI, "Tank ($200)", self.panel_y + 130),
        ]

        # Create send buttons
        for merc_type, text, y_pos in mercenary_data:
            btn = Button(
                text,
                pygame.Rect(self.panel_x + 10, y_pos, self.PANEL_WIDTH - 20, 30),
                lambda mt=merc_type: self._send_mercenary(mt),
                bg_color=(100, 50, 50),
                hover_color=(150, 80, 80),
            )
            self.panel.add(btn)

    def _send_mercenary(self, mercenary_type: MercenaryType) -> None:
        """
        Handle send mercenary button click.
        
        Args:
            mercenary_type: Type of mercenary to send.
        """
        if self.on_send_callback:
            success = self.on_send_callback(mercenary_type)
            if success:
                cost = MercenaryFactory.get_cost(mercenary_type)
                print(f"[MercenaryPanel] Sent {mercenary_type.name} for ${cost}")
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
