"""
Research Panel UI for PathWars - The Interpolation Battles.

Displays available research (I+D) that can be unlocked to access advanced
interpolation methods and features.
"""

import pygame
from typing import Optional, Callable

from ui.components import Button, Panel, Label
from core.research.research_type import ResearchType, RESEARCH_INFO
from core.research.research_manager import ResearchManager


class ResearchPanel:
    """
    UI Panel for managing research/technology unlocks.
    
    Shows:
    - Available research options
    - Costs and prerequisites
    - Unlock buttons
    - Current unlocked research
    """

    # Constants
    PANEL_WIDTH = 280
    PANEL_HEIGHT = 350

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        research_manager: ResearchManager,
        on_unlock_callback: Optional[Callable[[ResearchType], bool]] = None
    ) -> None:
        """
        Initialize the research panel.
        
        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            research_manager: The ResearchManager instance.
            on_unlock_callback: Callback function called when unlock button is clicked.
                              Should return True if unlock succeeded.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.research_manager = research_manager
        self.on_unlock_callback = on_unlock_callback

        self._visible: bool = False

        # Position panel in top-left (below curve editor)
        self.panel_x = 20
        self.panel_y = 420

        # Build panel
        self._build_panel()

    def _build_panel(self) -> None:
        """Build the research panel with buttons."""
        self.panel = Panel(
            pygame.Rect(self.panel_x, self.panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )

        # Title
        self.panel.add(Label(
            "Research (I+D)",
            (self.panel_x + 10, self.panel_y + 10),
            font_size=22
        ))

        # Research items
        y_offset = 50
        for research_type in ResearchType:
            info = RESEARCH_INFO.get(research_type)
            if not info:
                continue
            
            is_unlocked = self.research_manager.is_unlocked(research_type)
            can_unlock = self.research_manager.can_unlock(research_type)
            
            # Research name and status
            if is_unlocked:
                status = "✓ UNLOCKED"
                color = (100, 255, 100)
            elif can_unlock:
                status = f"${info.cost}"
                color = (255, 255, 255)
            else:
                status = "LOCKED"
                color = (150, 150, 150)
            
            # Display name label
            self.panel.add(Label(
                info.display_name,
                (self.panel_x + 10, self.panel_y + y_offset),
                font_size=16,
                color=color
            ))
            y_offset += 20
            
            # Status/Cost label
            self.panel.add(Label(
                status,
                (self.panel_x + 15, self.panel_y + y_offset),
                font_size=14,
                color=color
            ))
            y_offset += 25
            
            # Unlock button (if not unlocked and can unlock)
            if not is_unlocked and can_unlock:
                btn = Button(
                    "Unlock",
                    pygame.Rect(
                        self.panel_x + 10,
                        self.panel_y + y_offset,
                        self.PANEL_WIDTH - 20,
                        30
                    ),
                    lambda rt=research_type: self._unlock_research(rt),
                    bg_color=(50, 100, 150),
                    hover_color=(80, 150, 200),
                )
                self.panel.add(btn)
                y_offset += 35
            else:
                y_offset += 10
            
            # Spacing between items
            y_offset += 5

    def _unlock_research(self, research_type: ResearchType) -> None:
        """
        Handle unlock research button click.
        
        Args:
            research_type: Type of research to unlock.
        """
        if self.on_unlock_callback:
            success = self.on_unlock_callback(research_type)
            if success:
                # Rebuild panel to reflect new state
                self._rebuild_panel()

    def _rebuild_panel(self) -> None:
        """Rebuild the panel with updated research states."""
        self.panel.children.clear()
        self._build_panel()

    @property
    def visible(self) -> bool:
        """Check if the panel is visible."""
        return self._visible

    def show(self) -> None:
        """Show the research panel."""
        self._visible = True

    def hide(self) -> None:
        """Hide the research panel."""
        self._visible = False

    def toggle(self) -> None:
        """Toggle research panel visibility."""
        self._visible = not self._visible

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
