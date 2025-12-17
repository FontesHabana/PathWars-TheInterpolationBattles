"""
Wave Banner module for PathWars - The Interpolation Battles.

Displays temporary banners for wave transitions and game messages.
"""

import pygame
from typing import Optional, Tuple

from graphics.assets import AssetManager


class WaveBanner:
    """
    Displays centered banners for wave transitions.

    The banner appears on screen with a message and auto-hides
    after a configurable duration.

    Attributes:
        screen_width: Width of the game screen.
        screen_height: Height of the game screen.
        visible: Whether the banner is currently visible.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        font_size: int = 48,
        bg_color: Tuple[int, int, int, int] = (20, 20, 40, 220),
        text_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        """
        Initialize the WaveBanner.

        Args:
            screen_width: Width of the game screen.
            screen_height: Height of the game screen.
            font_size: Size of the banner text font.
            bg_color: Background color with alpha (RGBA).
            text_color: Text color (RGB).
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color

        self._message: str = ""
        self._duration: float = 0.0
        self._timer: float = 0.0
        self._visible: bool = False

    @property
    def visible(self) -> bool:
        """Return whether the banner is currently visible."""
        return self._visible

    @property
    def message(self) -> str:
        """Return the current banner message."""
        return self._message

    @property
    def remaining_time(self) -> float:
        """Return the remaining time before the banner hides."""
        return max(0.0, self._duration - self._timer)

    def show(self, message: str, duration: float = 2.0) -> None:
        """
        Display a banner with the given message.

        Args:
            message: Text to display on the banner.
            duration: Time in seconds to display the banner.
        """
        self._message = message
        self._duration = duration
        self._timer = 0.0
        self._visible = True

    def hide(self) -> None:
        """Hide the banner immediately."""
        self._visible = False
        self._timer = 0.0
        self._duration = 0.0
        self._message = ""

    def update(self, dt: float) -> None:
        """
        Update the banner timer.

        Args:
            dt: Delta time in seconds since last update.
        """
        if not self._visible:
            return

        self._timer += dt
        if self._timer >= self._duration:
            self._visible = False

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the banner centered on screen.

        Args:
            screen: Pygame surface to draw on.
        """
        if not self._visible:
            return

        # Get font and render text
        font = AssetManager.get_font(self.font_size)
        text_surf = font.render(self._message, True, self.text_color)
        text_rect = text_surf.get_rect()

        # Calculate banner dimensions with padding
        padding_x = 40
        padding_y = 20
        banner_width = text_rect.width + padding_x * 2
        banner_height = text_rect.height + padding_y * 2

        # Center the banner on screen
        banner_x = (self.screen_width - banner_width) // 2
        banner_y = (self.screen_height - banner_height) // 2

        # Draw semi-transparent background
        banner_surf = pygame.Surface(
            (banner_width, banner_height), pygame.SRCALPHA
        )
        banner_surf.fill(self.bg_color)
        screen.blit(banner_surf, (banner_x, banner_y))

        # Draw border
        border_rect = pygame.Rect(banner_x, banner_y, banner_width, banner_height)
        pygame.draw.rect(screen, (100, 100, 150), border_rect, width=3, border_radius=8)

        # Draw text centered in banner
        text_x = banner_x + padding_x
        text_y = banner_y + padding_y
        screen.blit(text_surf, (text_x, text_y))
