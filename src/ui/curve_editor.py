"""
Curve Editor UI module for PathWars.

Provides a visual interface for editing the enemy path by placing,
dragging, and configuring control points.
"""

import pygame
from typing import Optional, List, Tuple

from ui.components import Button, Panel, Label
from core.curve_state import CurveState
from graphics.assets import AssetManager


class CurveEditorUI:
    """
    Visual editor for the curve/path control points.

    Renders control points as draggable circles and provides
    buttons to add/remove points and switch interpolation methods.

    Attributes:
        curve_state: The CurveState instance managing the control points.
        screen_width: Width of the screen in pixels.
        screen_height: Height of the screen in pixels.
    """

    # Visual constants
    CONTROL_POINT_RADIUS = 10
    CONTROL_POINT_COLOR = (255, 255, 0)  # Yellow
    CONTROL_POINT_SELECTED_COLOR = (255, 165, 0)  # Orange
    CONTROL_POINT_HOVER_COLOR = (255, 200, 100)  # Light orange

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        curve_state: Optional[CurveState] = None,
    ) -> None:
        """
        Initialize the CurveEditorUI.

        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
            curve_state: Optional CurveState instance. Creates a new one if None.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.curve_state = curve_state if curve_state else CurveState()

        # Dragging state
        self._dragging_index: Optional[int] = None
        self._hovered_index: Optional[int] = None

        # Mode: 'normal' or 'add_point'
        self._mode: str = 'normal'

        # UI Panel
        self._panel: Panel = self._build_panel()

    def _build_panel(self) -> Panel:
        """
        Build the control panel with buttons.

        Returns:
            The configured Panel instance.
        """
        panel_width = 200
        panel_height = 280
        panel_x = 20
        panel_y = 120

        panel = Panel(pygame.Rect(panel_x, panel_y, panel_width, panel_height))

        # Title
        panel.add(Label("Curve Editor", (panel_x + 10, panel_y + 10), font_size=22))

        # Add Point button
        btn_add = Button(
            "Add Point",
            pygame.Rect(panel_x + 10, panel_y + 50, 180, 30),
            self._on_add_point_click,
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
        )
        panel.add(btn_add)

        # Remove Point button
        btn_remove = Button(
            "Remove Point",
            pygame.Rect(panel_x + 10, panel_y + 90, 180, 30),
            self._on_remove_point_click,
            bg_color=(100, 50, 50),
            hover_color=(150, 80, 80),
        )
        panel.add(btn_remove)

        # Interpolation method buttons
        btn_linear = Button(
            "Linear",
            pygame.Rect(panel_x + 10, panel_y + 140, 180, 30),
            lambda: self._set_method('linear'),
        )
        panel.add(btn_linear)

        btn_lagrange = Button(
            "Lagrange",
            pygame.Rect(panel_x + 10, panel_y + 180, 180, 30),
            lambda: self._set_method('lagrange'),
        )
        panel.add(btn_lagrange)

        btn_spline = Button(
            "Spline",
            pygame.Rect(panel_x + 10, panel_y + 220, 180, 30),
            lambda: self._set_method('spline'),
        )
        panel.add(btn_spline)

        return panel

    def _on_add_point_click(self) -> None:
        """Handle Add Point button click - toggle add mode."""
        if self._mode == 'add_point':
            self._mode = 'normal'
        else:
            self._mode = 'add_point'

    def _on_remove_point_click(self) -> None:
        """Handle Remove Point button click - remove last point."""
        if self.curve_state.get_point_count() > 0:
            self.curve_state.remove_point(self.curve_state.get_point_count() - 1)

    def _set_method(self, method: str) -> None:
        """Set the interpolation method."""
        self.curve_state.set_method(method)

    def _find_point_at(
        self, x: int, y: int
    ) -> Optional[int]:
        """
        Find the index of the control point at the given screen position.

        Args:
            x: Screen x coordinate.
            y: Screen y coordinate.

        Returns:
            Index of the control point if found, None otherwise.
        """
        for i, point in enumerate(self.curve_state.control_points):
            px, py = point
            dist_sq = (x - px) ** 2 + (y - py) ** 2
            if dist_sq <= self.CONTROL_POINT_RADIUS ** 2:
                return i
        return None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the curve editor.

        Args:
            event: The pygame event to handle.

        Returns:
            True if the event was consumed, False otherwise.
        """
        # Let panel handle events first
        if self._panel.handle_event(event):
            return True

        # Handle mouse motion for hover detection and dragging
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos

            # Update hover state
            self._hovered_index = self._find_point_at(mouse_x, mouse_y)

            # Handle dragging
            if self._dragging_index is not None:
                self.curve_state.move_point(self._dragging_index, mouse_x, mouse_y)
                return True

        # Handle mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Check if clicking on a control point
            point_index = self._find_point_at(mouse_x, mouse_y)

            if point_index is not None:
                # Start dragging
                self._dragging_index = point_index
                return True
            elif self._mode == 'add_point':
                # Add a new point at click location
                self.curve_state.add_point(mouse_x, mouse_y)
                self._mode = 'normal'
                return True

        # Handle mouse button up
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_index is not None:
                self._dragging_index = None
                return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the curve editor UI elements.

        Args:
            screen: The pygame surface to draw on.
        """
        # Draw the panel
        self._panel.draw(screen)

        # Draw mode indicator
        if self._mode == 'add_point':
            font = AssetManager.get_font(16)
            mode_text = "Click to add a point"
            text_surf = font.render(mode_text, True, (255, 255, 0))
            screen.blit(text_surf, (20, self.screen_height - 60))

        # Draw method indicator
        font = AssetManager.get_font(16)
        method_text = f"Method: {self.curve_state.interpolation_method}"
        text_surf = font.render(method_text, True, (200, 200, 200))
        screen.blit(text_surf, (20, self.screen_height - 80))

    def draw_control_points(self, screen: pygame.Surface) -> None:
        """
        Draw the control points on the screen.

        Args:
            screen: The pygame surface to draw on.
        """
        for i, point in enumerate(self.curve_state.control_points):
            px, py = int(point[0]), int(point[1])

            # Choose color based on state
            if i == self._dragging_index:
                color = self.CONTROL_POINT_SELECTED_COLOR
            elif i == self._hovered_index:
                color = self.CONTROL_POINT_HOVER_COLOR
            else:
                color = self.CONTROL_POINT_COLOR

            # Draw the control point circle
            pygame.draw.circle(screen, color, (px, py), self.CONTROL_POINT_RADIUS)
            pygame.draw.circle(
                screen, (255, 255, 255), (px, py), self.CONTROL_POINT_RADIUS, 2
            )

            # Draw point index
            font = AssetManager.get_font(12)
            index_text = font.render(str(i), True, (0, 0, 0))
            text_rect = index_text.get_rect(center=(px, py))
            screen.blit(index_text, text_rect)

    @property
    def is_dragging(self) -> bool:
        """
        Check if a control point is currently being dragged.

        Returns:
            True if dragging, False otherwise.
        """
        return self._dragging_index is not None

    @property
    def mode(self) -> str:
        """
        Get the current editor mode.

        Returns:
            The current mode string ('normal' or 'add_point').
        """
        return self._mode
