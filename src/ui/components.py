"""
UI Components module for PathWars.

Basic UI widgets: Button, Panel, Label.
"""

import pygame
from typing import Callable, Optional, Tuple
from graphics.assets import AssetManager


class Label:
    """Simple text display."""

    def __init__(
        self,
        text: str,
        pos: Tuple[int, int],
        font_size: int = 20,
        color: Optional[Tuple[int, int, int]] = None,
    ):
        self.text = text
        self.pos = pos
        self.font_size = font_size
        self.color = color or AssetManager.get_color("text")

    def draw(self, screen: pygame.Surface):
        font = AssetManager.get_font(self.font_size)
        surf = font.render(self.text, True, self.color)
        screen.blit(surf, self.pos)


class Button:
    """Clickable rectangle with text."""

    def __init__(
        self,
        text: str,
        rect: pygame.Rect,
        on_click: Callable[[], None],
        bg_color: Tuple[int, int, int] = (50, 50, 80),
        hover_color: Tuple[int, int, int] = (80, 80, 120),
        text_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        self.text = text
        self.rect = rect
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self._hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Returns True if this button consumed the event.
        """
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, screen: pygame.Surface):
        # Use dimmer colors if disabled
        if not self.enabled:
            color = self.bg_color
            text_color = (150, 150, 150)
        else:
            color = self.hover_color if self._hovered else self.bg_color
            text_color = self.text_color
            
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, width=2, border_radius=5)

        font = AssetManager.get_font(18)
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class Panel:
    """Background container for UI elements."""

    def __init__(
        self,
        rect: pygame.Rect,
        bg_color: Tuple[int, int, int, int] = (20, 20, 40, 200),
    ):
        self.rect = rect
        self.bg_color = bg_color
        self.children: list = []

    def add(self, child):
        self.children.append(child)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for child in self.children:
            if hasattr(child, "handle_event") and child.handle_event(event):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        # Draw semi-transparent background
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        surf.fill(self.bg_color)
        screen.blit(surf, self.rect.topleft)

        # Draw border
        pygame.draw.rect(screen, (80, 80, 120), self.rect, width=2, border_radius=5)

        # Draw children
        for child in self.children:
            child.draw(screen)
