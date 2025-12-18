"""
Pause Menu module for PathWars.

Provides a pause menu for single player mode with Resume, Restart,
and Main Menu options.
"""

import pygame
from typing import Optional, Dict

from ui.components import Button


class PauseMenu:
    """
    Pause menu for single player mode.
    
    Allows players to pause the game and access options like
    Resume, Restart, and Return to Main Menu.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the PauseMenu.
        
        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._visible = False
        
        # Fonts
        self._title_font = pygame.font.Font(None, 64)
        self._button_font = pygame.font.Font(None, 42)
        
        # Build buttons
        self._buttons: Dict[str, Button] = {}
        self._build_buttons()
    
    def _build_buttons(self) -> None:
        """Create the pause menu buttons."""
        button_width = 250
        button_height = 60
        button_spacing = 80
        
        center_x = self._screen_width // 2
        center_y = self._screen_height // 2
        
        # Start position for buttons
        start_y = center_y - 40
        
        # Resume button
        resume_rect = pygame.Rect(
            center_x - button_width // 2,
            start_y,
            button_width,
            button_height
        )
        self._buttons['resume'] = Button(
            "Resume",
            resume_rect,
            lambda: None,  # Action handled in handle_event
            bg_color=(50, 100, 50),
            hover_color=(80, 150, 80),
            text_color=(255, 255, 255)
        )
        
        # Restart button
        restart_rect = pygame.Rect(
            center_x - button_width // 2,
            start_y + button_spacing,
            button_width,
            button_height
        )
        self._buttons['restart'] = Button(
            "Restart",
            restart_rect,
            lambda: None,  # Action handled in handle_event
            bg_color=(100, 100, 50),
            hover_color=(150, 150, 80),
            text_color=(255, 255, 255)
        )
        
        # Main Menu button
        main_menu_rect = pygame.Rect(
            center_x - button_width // 2,
            start_y + button_spacing * 2,
            button_width,
            button_height
        )
        self._buttons['main_menu'] = Button(
            "Main Menu",
            main_menu_rect,
            lambda: None,  # Action handled in handle_event
            bg_color=(100, 50, 50),
            hover_color=(150, 80, 80),
            text_color=(255, 255, 255)
        )
    
    @property
    def visible(self) -> bool:
        """Check if pause menu is visible."""
        return self._visible
    
    def show(self) -> None:
        """Show the pause menu."""
        self._visible = True
    
    def hide(self) -> None:
        """Hide the pause menu."""
        self._visible = False
    
    def toggle(self) -> None:
        """Toggle pause menu visibility."""
        self._visible = not self._visible
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle events. Returns action string or None.
        
        Args:
            event: Pygame event to handle.
        
        Returns:
            'resume' - Continue playing
            'restart' - Restart current game
            'main_menu' - Return to main menu
            None - No action
        """
        if not self._visible:
            return None
        
        # Check if any button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button_name, button in self._buttons.items():
                if button.rect.collidepoint(event.pos):
                    return button_name
        
        # Update button hover states
        if event.type == pygame.MOUSEMOTION:
            for button in self._buttons.values():
                button.handle_event(event)
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the pause menu overlay.
        
        Args:
            surface: Pygame surface to draw on.
        """
        if not self._visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self._screen_width, self._screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self._title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self._screen_width // 2, self._screen_height // 2 - 150))
        surface.blit(title_text, title_rect)
        
        # Draw buttons
        for button in self._buttons.values():
            button.draw(surface)
