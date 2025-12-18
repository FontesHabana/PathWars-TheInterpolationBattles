"""
Result Screen module for PathWars - The Interpolation Battles.

Displays Victory and Game Over screens with restart/quit options.
"""

import pygame
from typing import Any, Dict, Optional, Tuple

from graphics.assets import AssetManager
from ui.components import Button


class ResultScreen:
    """
    Full-screen display for Victory or Game Over states.

    Shows game statistics and provides buttons to restart or quit.

    Attributes:
        screen_width: Width of the game screen.
        screen_height: Height of the game screen.
        visible: Whether the screen is currently visible.
    """

    # Result types
    VICTORY = "victory"
    GAME_OVER = "game_over"

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        bg_color: Tuple[int, int, int, int] = (10, 10, 30, 240),
    ):
        """
        Initialize the ResultScreen.

        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            bg_color: Background color with alpha (RGBA).
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = bg_color

        self._visible: bool = False
        self._result_type: Optional[str] = None
        self._stats: Dict[str, Any] = {}
        self._action: Optional[str] = None

        # Create buttons (positioned later)
        self._restart_button: Optional[Button] = None
        self._quit_button: Optional[Button] = None
        self._build_buttons()

    def _build_buttons(self) -> None:
        """Create the restart and quit buttons."""
        button_width = 180
        button_height = 50
        button_spacing = 30
        total_width = button_width * 2 + button_spacing

        # Center buttons horizontally
        start_x = (self.screen_width - total_width) // 2
        button_y = self.screen_height // 2 + 100

        self._restart_button = Button(
            "Play Again",
            pygame.Rect(start_x, button_y, button_width, button_height),
            self._on_restart,
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
            text_color=(255, 255, 255),
        )

        self._quit_button = Button(
            "Main Menu",
            pygame.Rect(
                start_x + button_width + button_spacing,
                button_y,
                button_width,
                button_height,
            ),
            self._on_quit,
            bg_color=(100, 50, 50),
            hover_color=(150, 80, 80),
            text_color=(255, 255, 255),
        )

    def _on_restart(self) -> None:
        """Callback when restart button is clicked."""
        self._action = "restart"

    def _on_quit(self) -> None:
        """Callback when quit button is clicked."""
        self._action = "quit"

    @property
    def visible(self) -> bool:
        """Return whether the screen is currently visible."""
        return self._visible

    @property
    def result_type(self) -> Optional[str]:
        """Return the current result type ('victory' or 'game_over')."""
        return self._result_type

    @property
    def stats(self) -> Dict[str, Any]:
        """Return the current game statistics."""
        return self._stats.copy()

    def show_victory(self, stats: Optional[Dict[str, Any]] = None) -> None:
        """
        Display the victory screen.

        Args:
            stats: Dictionary of game statistics to display.
        """
        self._result_type = self.VICTORY
        self._stats = stats or {}
        self._visible = True
        self._action = None

    def show_game_over(self, stats: Optional[Dict[str, Any]] = None) -> None:
        """
        Display the game over screen.

        Args:
            stats: Dictionary of game statistics to display.
        """
        self._result_type = self.GAME_OVER
        self._stats = stats or {}
        self._visible = True
        self._action = None

    def hide(self) -> None:
        """Hide the result screen."""
        self._visible = False
        self._result_type = None
        self._stats = {}
        self._action = None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events and return any action triggered.

        Args:
            event: Pygame event to process.

        Returns:
            'restart' if Play Again was clicked,
            'quit' if Quit was clicked,
            None otherwise.
        """
        if not self._visible:
            return None

        # Reset action before processing
        self._action = None

        # Let buttons handle the event
        if self._restart_button:
            self._restart_button.handle_event(event)
        if self._quit_button:
            self._quit_button.handle_event(event)

        return self._action

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the result screen.

        Args:
            screen: Pygame surface to draw on.
        """
        if not self._visible:
            return

        # Draw semi-transparent full-screen overlay
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill(self.bg_color)
        screen.blit(overlay, (0, 0))

        # Draw title
        title_font = AssetManager.get_font(72)
        if self._result_type == self.VICTORY:
            title_text = "VICTORY!"
            title_color = (0, 255, 100)
        else:
            title_text = "GAME OVER"
            title_color = (255, 50, 50)

        title_surf = title_font.render(title_text, True, title_color)
        title_rect = title_surf.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 100)
        )
        screen.blit(title_surf, title_rect)

        # Draw statistics
        if self._stats:
            stat_font = AssetManager.get_font(24)
            stat_y = self.screen_height // 2 - 20

            for key, value in self._stats.items():
                stat_text = f"{key}: {value}"
                stat_surf = stat_font.render(stat_text, True, (200, 200, 200))
                stat_rect = stat_surf.get_rect(
                    center=(self.screen_width // 2, stat_y)
                )
                screen.blit(stat_surf, stat_rect)
                stat_y += 35

        # Draw buttons
        if self._restart_button:
            self._restart_button.draw(screen)
        if self._quit_button:
            self._quit_button.draw(screen)
