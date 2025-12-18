"""
Curve Editor UI module for PathWars.

Provides a visual interface for editing the enemy path by placing,
dragging, and configuring control points.
"""

import pygame
from enum import Enum, auto
from typing import Optional, List, Tuple

from ui.components import Button, Panel, Label
from core.curve_state import CurveState
from graphics.assets import AssetManager


class EditorMode(Enum):
    """Enumeration of editor modes."""
    NORMAL = auto()
    ADD_POINT = auto()


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

    # Panel layout constants
    PANEL_WIDTH = 200
    PANEL_HEIGHT = 280
    PANEL_X = 20
    PANEL_Y = 120
    BUTTON_WIDTH = 180
    BUTTON_HEIGHT = 30
    BUTTON_MARGIN = 10

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        renderer: "Renderer",
        curve_state: Optional[CurveState] = None,
    ) -> None:
        """
        Initialize the CurveEditorUI.

        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
            renderer: The Renderer instance for coordinate conversion.
            curve_state: Optional CurveState instance. Creates a new one if None.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.renderer = renderer
        self.curve_state = curve_state if curve_state else CurveState()

        # Dragging state
        self._dragging_index: Optional[int] = None
        self._hovered_index: Optional[int] = None

        # Mode
        self._mode: EditorMode = EditorMode.NORMAL

        # Enabled state
        self._enabled: bool = True

        # UI Panel
        self._panel: Panel = self._build_panel()

    def _build_panel(self) -> Panel:
        """
        Build the control panel with buttons.

        Returns:
            The configured Panel instance.
        """
        panel_x = self.PANEL_X
        panel_y = self.PANEL_Y

        panel = Panel(pygame.Rect(
            panel_x, panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT
        ))

        # Title
        panel.add(Label(
            "Curve Editor",
            (panel_x + self.BUTTON_MARGIN, panel_y + self.BUTTON_MARGIN),
            font_size=22
        ))

        # Add Point button
        btn_add = Button(
            "Add Point",
            pygame.Rect(
                panel_x + self.BUTTON_MARGIN,
                panel_y + 50,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT
            ),
            self._on_add_point_click,
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
        )
        panel.add(btn_add)

        # Remove Point button
        btn_remove = Button(
            "Remove Point",
            pygame.Rect(
                panel_x + self.BUTTON_MARGIN,
                panel_y + 90,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT
            ),
            self._on_remove_point_click,
            bg_color=(100, 50, 50),
            hover_color=(150, 80, 80),
        )
        panel.add(btn_remove)

        # Interpolation method buttons
        btn_linear = Button(
            "Linear",
            pygame.Rect(
                panel_x + self.BUTTON_MARGIN,
                panel_y + 140,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT
            ),
            lambda: self._set_method('linear'),
        )
        panel.add(btn_linear)

        btn_lagrange = Button(
            "Lagrange",
            pygame.Rect(
                panel_x + self.BUTTON_MARGIN,
                panel_y + 180,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT
            ),
            lambda: self._set_method('lagrange'),
        )
        panel.add(btn_lagrange)

        btn_spline = Button(
            "Spline",
            pygame.Rect(
                panel_x + self.BUTTON_MARGIN,
                panel_y + 220,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT
            ),
            lambda: self._set_method('spline'),
        )
        panel.add(btn_spline)

        return panel

    def _on_add_point_click(self) -> None:
        """Handle Add Point button click - toggle add mode."""
        if self._mode == EditorMode.ADD_POINT:
            self._mode = EditorMode.NORMAL
        else:
            self._mode = EditorMode.ADD_POINT

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
            # Convert grid point to screen for collision check
            screen_pos = self.renderer.cart_to_iso(point[0], point[1])
            px, py = screen_pos
            dist_sq = (x - px) ** 2 + (y - py) ** 2
            if dist_sq <= self.CONTROL_POINT_RADIUS ** 2:
                return i
        return None

    def _clamp_to_grid(self, gx: float, gy: float) -> Tuple[float, float]:
        """Clamp grid coordinates to valid grid range."""
        max_x = self.renderer.grid.width - 1
        max_y = self.renderer.grid.height - 1
        return max(0, min(gx, max_x)), max(0, min(gy, max_y))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the curve editor.

        Args:
            event: The pygame event to handle.

        Returns:
            True if the event was consumed, False otherwise.
        """
        # Return early if not enabled or curve is locked
        if not self._enabled or self.curve_state.locked:
            return False
        
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
                gx, gy = self.renderer.iso_to_cart(mouse_x, mouse_y)
                gx, gy = self._clamp_to_grid(gx, gy)
                self.curve_state.move_point(self._dragging_index, gx, gy)
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
            elif self._mode == EditorMode.ADD_POINT:
                # Add a new point at click location
                gx, gy = self.renderer.iso_to_cart(mouse_x, mouse_y)
                gx, gy = self._clamp_to_grid(gx, gy)
                if self.curve_state.add_point(gx, gy):
                    self._mode = EditorMode.NORMAL
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

        # Draw locked indicator if curve is locked
        font = AssetManager.get_font(16)
        if self.curve_state.locked:
            locked_text = "🔒 Editing Locked"
            text_surf = font.render(locked_text, True, (255, 100, 100))
            screen.blit(text_surf, (20, self.screen_height - 60))
        elif self._mode == EditorMode.ADD_POINT:
            # Draw mode indicator
            mode_text = "Click on GRID to add a point"
            text_surf = font.render(mode_text, True, (255, 255, 0))
            screen.blit(text_surf, (20, self.screen_height - 60))

        # Draw method indicator
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
            # Convert grid coordinates to screen for rendering
            screen_pos = self.renderer.cart_to_iso(point[0], point[1])
            px, py = int(screen_pos[0]), int(screen_pos[1])

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
    def mode(self) -> EditorMode:
        """
        Get the current editor mode.

        Returns:
            The current EditorMode (NORMAL or ADD_POINT).
        """
        return self._mode

    @property
    def enabled(self) -> bool:
        """
        Get whether the editor is enabled.

        Returns:
            True if enabled, False otherwise.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Set whether the editor is enabled.
        
        When disabled, resets dragging state and mode to prevent stuck states.

        Args:
            value: True to enable, False to disable.
        """
        self._enabled = value
        if not value:
            self._dragging_index = None
            self._mode = EditorMode.NORMAL


