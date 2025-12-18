"""
Ready Panel UI component for PathWars.

Displays ready button, countdown timer, and ready status during planning phase.
"""

import pygame
from typing import Callable, Optional
from graphics.assets import AssetManager
from core.ready_manager import ReadyManager


class ReadyPanel:
    """
    Visual panel for ready system during planning phase.
    
    Shows countdown timer, ready status, and a toggle button.
    
    Attributes:
        ready_manager: The ReadyManager instance to sync with.
        player_id: The ID of the local player.
        on_ready_callback: Optional callback when ready state changes.
    """
    
    # Panel dimensions and positioning
    PANEL_WIDTH = 300
    PANEL_HEIGHT = 120
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 40
    
    # Colors
    BG_COLOR = (40, 40, 60, 200)  # Semi-transparent background
    BUTTON_NOT_READY_COLOR = (80, 80, 80)
    BUTTON_READY_COLOR = (50, 150, 50)
    BUTTON_HOVER_COLOR = (100, 100, 100)
    BUTTON_READY_HOVER_COLOR = (70, 180, 70)
    
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        ready_manager: ReadyManager,
        player_id: int = 0,
        on_ready_callback: Optional[Callable[[bool], None]] = None,
    ) -> None:
        """
        Initialize the ReadyPanel.
        
        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
            ready_manager: The ReadyManager instance.
            player_id: The ID of the local player (default: 0).
            on_ready_callback: Optional callback called when ready state changes.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ready_manager = ready_manager
        self.player_id = player_id
        self.on_ready_callback = on_ready_callback
        
        # Calculate centered position at bottom of screen
        self.panel_x = (screen_width - self.PANEL_WIDTH) // 2
        self.panel_y = screen_height - self.PANEL_HEIGHT - 20
        
        # Button rect
        button_x = self.panel_x + (self.PANEL_WIDTH - self.BUTTON_WIDTH) // 2
        button_y = self.panel_y + 70
        self.button_rect = pygame.Rect(
            button_x, button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT
        )
        
        # State
        self._is_ready = False
        self._button_hovered = False
    
    @property
    def is_ready(self) -> bool:
        """Return whether the player is ready."""
        return self._is_ready
    
    def reset(self) -> None:
        """Reset the panel state."""
        self._is_ready = False
        self._button_hovered = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            True if the event was consumed, False otherwise.
        """
        if not self.ready_manager.is_active:
            return False
        
        # Track hover state
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self._button_hovered = self.button_rect.collidepoint(mouse_x, mouse_y)
        
        # Handle button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if self.button_rect.collidepoint(mouse_x, mouse_y):
                self._toggle_ready()
                return True
        
        return False
    
    def _toggle_ready(self) -> None:
        """Toggle ready state."""
        if self._is_ready:
            # Unready
            self.ready_manager.set_unready(self.player_id)
            self._is_ready = False
        else:
            # Ready
            self.ready_manager.set_ready(self.player_id)
            self._is_ready = True
        
        # Call callback if provided
        if self.on_ready_callback:
            self.on_ready_callback(self._is_ready)
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the ready panel.
        
        Args:
            screen: The pygame surface to draw on.
        """
        if not self.ready_manager.is_active:
            return
        
        # Draw semi-transparent background
        panel_surf = pygame.Surface((self.PANEL_WIDTH, self.PANEL_HEIGHT), pygame.SRCALPHA)
        panel_surf.fill(self.BG_COLOR)
        screen.blit(panel_surf, (self.panel_x, self.panel_y))
        
        # Draw border
        pygame.draw.rect(
            screen,
            (100, 100, 120),
            (self.panel_x, self.panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT),
            2
        )
        
        # Draw timer
        time_remaining = self.ready_manager.time_remaining
        if self.ready_manager.ready_timeout > 0:
            # Color based on time remaining
            if time_remaining <= 5:
                timer_color = (255, 50, 50)  # Red
            elif time_remaining <= 10:
                timer_color = (255, 200, 0)  # Yellow
            else:
                timer_color = (255, 255, 255)  # White
            
            timer_text = f"{int(time_remaining)}s"
            timer_font = AssetManager.get_font(32)
            timer_surf = timer_font.render(timer_text, True, timer_color)
            timer_rect = timer_surf.get_rect(
                center=(self.panel_x + self.PANEL_WIDTH // 2, self.panel_y + 25)
            )
            screen.blit(timer_surf, timer_rect)
        
        # Draw ready status
        ready_count = self.ready_manager.ready_count
        player_count = self.ready_manager.player_count
        status_text = f"Ready: {ready_count}/{player_count}"
        status_font = AssetManager.get_font(18)
        status_surf = status_font.render(status_text, True, (200, 200, 200))
        status_rect = status_surf.get_rect(
            center=(self.panel_x + self.PANEL_WIDTH // 2, self.panel_y + 50)
        )
        screen.blit(status_surf, status_rect)
        
        # Draw button
        if self._is_ready:
            button_color = self.BUTTON_READY_HOVER_COLOR if self._button_hovered else self.BUTTON_READY_COLOR
            button_text = "Cancel Ready"
        else:
            button_color = self.BUTTON_HOVER_COLOR if self._button_hovered else self.BUTTON_NOT_READY_COLOR
            button_text = "Ready!"
        
        pygame.draw.rect(screen, button_color, self.button_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 2)
        
        # Draw button text
        button_font = AssetManager.get_font(20)
        text_surf = button_font.render(button_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.button_rect.center)
        screen.blit(text_surf, text_rect)
