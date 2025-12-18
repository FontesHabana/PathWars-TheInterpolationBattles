"""
Tower Info Panel UI for PathWars - The Interpolation Battles.

Displays detailed tower information and upgrade options.
"""

import pygame
from typing import Callable, Optional

from entities.tower import Tower, TowerLevel
from ui.components import Button, Panel, Label


class TowerInfoPanel:
    """
    UI Panel for displaying tower information and upgrade options.
    
    Shows:
    - Tower type and level
    - Current stats (damage, range, cooldown)
    - Type-specific stats
    - Upgrade preview (if available)
    - Upgrade button
    """

    # Constants
    PANEL_WIDTH = 220
    PANEL_HEIGHT = 300

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_upgrade_callback: Optional[Callable[[Tower], bool]] = None
    ) -> None:
        """
        Initialize the tower info panel.
        
        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            on_upgrade_callback: Callback function called when upgrade button is clicked.
                                Should return True if upgrade succeeded.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.on_upgrade_callback = on_upgrade_callback

        self._selected_tower: Optional[Tower] = None
        self._visible: bool = False

        # Position panel on the left side
        self.panel_x = 20
        self.panel_y = screen_height - self.PANEL_HEIGHT - 20

        # Create panel
        self.panel = Panel(
            pygame.Rect(self.panel_x, self.panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )

        # Upgrade button (created dynamically)
        self._upgrade_button: Optional[Button] = None

    @property
    def selected_tower(self) -> Optional[Tower]:
        """Get the currently selected tower."""
        return self._selected_tower

    @property
    def visible(self) -> bool:
        """Check if the panel is visible."""
        return self._visible

    def select_tower(self, tower: Optional[Tower]) -> None:
        """
        Select a tower to display information for.
        
        Args:
            tower: The tower to select, or None to deselect.
        """
        self._selected_tower = tower
        self._visible = tower is not None
        self._rebuild_panel()

    def deselect(self) -> None:
        """Deselect the current tower and hide the panel."""
        self._selected_tower = None
        self._visible = False

    def _rebuild_panel(self) -> None:
        """Rebuild the panel contents based on selected tower."""
        # Clear existing children
        self.panel.children.clear()

        if not self._selected_tower:
            return

        tower = self._selected_tower
        y_offset = self.panel_y + 10

        # Title: Tower Type and Level
        level_name = "MASTERY" if tower.level == TowerLevel.MASTERY else "DOCTORATE"
        title = f"{tower.tower_type.name} ({level_name})"
        self.panel.add(Label(title, (self.panel_x + 10, y_offset), font_size=20))
        y_offset += 30

        # Current Stats Section
        self.panel.add(Label("Current Stats:", (self.panel_x + 10, y_offset), font_size=16))
        y_offset += 25

        # Display stats
        stats_text = [
            f"Damage: {tower.damage}",
            f"Range: {tower.attack_range:.2f}",
            f"Cooldown: {tower.cooldown:.2f}s",
        ]

        # Add type-specific stats
        if tower.tower_type.name == "DEAN" and tower.stun_duration > 0:
            stats_text.append(f"Stun: {tower.stun_duration:.1f}s")
        elif tower.tower_type.name == "PHYSICS" and tower.splash_radius > 0:
            stats_text.append(f"Splash: {tower.splash_radius:.1f}")
        elif tower.tower_type.name == "STATISTICS":
            if tower.slow_amount > 0:
                stats_text.append(f"Slow: {int(tower.slow_amount * 100)}%")
            if tower.slow_duration > 0:
                stats_text.append(f"Duration: {tower.slow_duration:.1f}s")

        for stat in stats_text:
            self.panel.add(Label(stat, (self.panel_x + 15, y_offset), font_size=14))
            y_offset += 20

        # Upgrade Preview Section (if can upgrade)
        if tower.can_upgrade:
            y_offset += 10
            self.panel.add(Label("After Upgrade:", (self.panel_x + 10, y_offset), font_size=16))
            y_offset += 25

            preview = tower.get_upgrade_preview()
            if preview:
                upgraded = preview["upgraded"]
                upgrade_text = [
                    f"Damage: {int(upgraded['damage'])} (+{int(upgraded['damage'] - tower.damage)})",
                    f"Range: {upgraded['attack_range']:.2f} (+{upgraded['attack_range'] - tower.attack_range:.2f})",
                    f"Cooldown: {upgraded['cooldown']:.2f}s ({upgraded['cooldown'] - tower.cooldown:.2f}s)",
                ]

                for text in upgrade_text:
                    self.panel.add(Label(text, (self.panel_x + 15, y_offset), font_size=14, color=(100, 255, 100)))
                    y_offset += 20

        # Upgrade Button or Max Level Indicator
        y_offset += 10
        if tower.can_upgrade:
            cost = tower.upgrade_cost
            button_text = f"Upgrade (${cost})"
            self._upgrade_button = Button(
                button_text,
                pygame.Rect(self.panel_x + 10, y_offset, self.PANEL_WIDTH - 20, 35),
                self._on_upgrade_click,
                bg_color=(50, 100, 50),
                hover_color=(80, 150, 80),
            )
            self.panel.add(self._upgrade_button)
        else:
            self.panel.add(Label(
                "MAX LEVEL",
                (self.panel_x + 60, y_offset + 10),
                font_size=18,
                color=(255, 215, 0)
            ))

    def _on_upgrade_click(self) -> None:
        """Handle upgrade button click."""
        if self._selected_tower and self.on_upgrade_callback:
            success = self.on_upgrade_callback(self._selected_tower)
            if success:
                # Rebuild panel to show updated stats
                self._rebuild_panel()

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
