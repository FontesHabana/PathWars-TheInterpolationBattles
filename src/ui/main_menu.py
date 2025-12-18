"""
Main Menu UI Module.

Provides the main menu screen with Host/Join/Single Player/Quit options.
"""

import logging
import re
from typing import Optional, Tuple
import pygame

logger = logging.getLogger(__name__)


class MainMenu:
    """
    Main menu screen for game mode selection and multiplayer setup.
    
    Provides options to host a game, join a game, play single player, or quit.
    Includes input fields for IP address and port configuration.
    
    Attributes:
        visible: Whether the main menu is currently visible.
    """
    
    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize the MainMenu.
        
        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._visible = True
        
        # UI State
        self._selected_option: Optional[str] = None  # 'host', 'join', None
        self._hovered_button: Optional[str] = None
        
        # Input fields
        self._ip_input = "127.0.0.1"
        self._port_input = "12345"
        self._active_input: Optional[str] = None  # 'ip', 'port', None
        
        # Connection status
        self._status_message = ""
        self._status_color = (255, 255, 255)
        
        # Fonts
        self._title_font = pygame.font.Font(None, 72)
        self._button_font = pygame.font.Font(None, 48)
        self._input_font = pygame.font.Font(None, 36)
        self._status_font = pygame.font.Font(None, 32)
        
        # Button definitions (text, rect)
        center_x = screen_width // 2
        button_width = 300
        button_height = 60
        button_spacing = 80
        start_y = 250
        
        self._buttons = {
            'host': pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            'join': pygame.Rect(center_x - button_width // 2, start_y + button_spacing, button_width, button_height),
            'single': pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height),
            'codex': pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 3, button_width, button_height),
            'quit': pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 4, button_width, button_height),
        }
        
        # Input field rects
        input_width = 250
        input_height = 40
        input_x = center_x - input_width // 2
        input_y = start_y + button_spacing * 5 + 20
        
        self._input_rects = {
            'ip': pygame.Rect(input_x, input_y, input_width, input_height),
            'port': pygame.Rect(input_x, input_y + 60, input_width, input_height),
        }
        
        # Button for confirming host/join
        self._confirm_button = pygame.Rect(center_x - 100, input_y + 120, 200, 50)
    
    @property
    def visible(self) -> bool:
        """Check if the main menu is visible."""
        return self._visible
    
    @property
    def selected_option(self) -> Optional[str]:
        """Get the currently selected option ('host', 'join', or None)."""
        return self._selected_option
    
    def show(self) -> None:
        """Show the main menu."""
        self._visible = True
    
    def hide(self) -> None:
        """Hide the main menu."""
        self._visible = False
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events.
        
        Args:
            event: Pygame event to handle.
            
        Returns:
            Action string ('host', 'join', 'single', 'quit', 'confirm') or None.
        """
        if not self._visible:
            return None
        
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
            return None
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_mouse_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        
        return None
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion for hover effects."""
        self._hovered_button = None
        
        for button_name, button_rect in self._buttons.items():
            if button_rect.collidepoint(pos):
                self._hovered_button = button_name
                break
        
        if self._confirm_button.collidepoint(pos) and self._selected_option:
            self._hovered_button = 'confirm'
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click events."""
        # Check main buttons
        if self._selected_option is None:
            for button_name, button_rect in self._buttons.items():
                if button_rect.collidepoint(pos):
                    if button_name in ('host', 'join'):
                        self._selected_option = button_name
                        self._status_message = ""
                        return None
                    else:
                        return button_name
        else:
            # Check input fields
            self._active_input = None
            for input_name, input_rect in self._input_rects.items():
                if input_rect.collidepoint(pos):
                    self._active_input = input_name
                    return None
            
            # Check confirm button
            if self._confirm_button.collidepoint(pos):
                return 'confirm'
        
        return None
    
    def _handle_keydown(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard input."""
        if event.key == pygame.K_ESCAPE:
            if self._selected_option is not None:
                self._selected_option = None
                self._active_input = None
                self._status_message = ""
                return None
            else:
                return 'quit'
        
        elif event.key == pygame.K_RETURN and self._selected_option:
            return 'confirm'
        
        # Handle text input
        if self._active_input:
            if event.key == pygame.K_BACKSPACE:
                if self._active_input == 'ip':
                    self._ip_input = self._ip_input[:-1]
                elif self._active_input == 'port':
                    self._port_input = self._port_input[:-1]
            else:
                char = event.unicode
                if self._active_input == 'ip':
                    # Only allow IP address characters (digits, dots)
                    if char in '0123456789.':
                        if len(self._ip_input) < 15:  # Max IPv4 length
                            self._ip_input += char
                elif self._active_input == 'port':
                    # Only allow digits for port
                    if char.isdigit():
                        if len(self._port_input) < 5:  # Max port length
                            self._port_input += char
        
        return None
    
    def get_connection_info(self) -> Tuple[str, int]:
        """
        Get the current connection information from input fields.
        
        Returns:
            Tuple of (ip_address, port_number).
        """
        try:
            port = int(self._port_input) if self._port_input else 12345
            # Validate port range
            if not (1 <= port <= 65535):
                port = 12345
        except ValueError:
            port = 12345
        
        ip = self._ip_input if self._ip_input else "127.0.0.1"
        
        return (ip, port)
    
    def set_status(self, message: str, is_error: bool = False) -> None:
        """
        Set the status message to display.
        
        Args:
            message: Status message to display.
            is_error: Whether this is an error message (displays in red).
        """
        self._status_message = message
        self._status_color = (255, 100, 100) if is_error else (100, 255, 100)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the main menu.
        
        Args:
            surface: Pygame surface to draw on.
        """
        if not self._visible:
            return
        
        # Draw semi-transparent background
        overlay = pygame.Surface((self._screen_width, self._screen_height))
        overlay.set_alpha(240)
        overlay.fill((20, 20, 40))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self._title_font.render("PathWars", True, (255, 200, 50))
        title_rect = title_text.get_rect(center=(self._screen_width // 2, 100))
        surface.blit(title_text, title_rect)
        
        subtitle_text = self._input_font.render("The Interpolation Battles", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self._screen_width // 2, 150))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons or input panel
        if self._selected_option is None:
            self._draw_main_buttons(surface)
        else:
            self._draw_connection_panel(surface)
        
        # Draw status message
        if self._status_message:
            status_text = self._status_font.render(self._status_message, True, self._status_color)
            status_rect = status_text.get_rect(center=(self._screen_width // 2, self._screen_height - 50))
            surface.blit(status_text, status_rect)
    
    def _draw_main_buttons(self, surface: pygame.Surface) -> None:
        """Draw the main menu buttons."""
        button_labels = {
            'host': "Host Game",
            'join': "Join Game",
            'single': "Single Player",
            'codex': "Codex",
            'quit': "Quit",
        }
        
        for button_name, button_rect in self._buttons.items():
            # Button color based on hover state
            is_hovered = (self._hovered_button == button_name)
            color = (100, 100, 200) if is_hovered else (60, 60, 120)
            
            pygame.draw.rect(surface, color, button_rect)
            pygame.draw.rect(surface, (150, 150, 150), button_rect, 2)
            
            # Button text
            text = self._button_font.render(button_labels[button_name], True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            surface.blit(text, text_rect)
    
    def _draw_connection_panel(self, surface: pygame.Surface) -> None:
        """Draw the host/join connection panel."""
        # Panel title
        if self._selected_option == 'host':
            panel_title = "Host Game"
        else:
            panel_title = "Join Game"
        
        title_text = self._button_font.render(panel_title, True, (255, 200, 50))
        title_rect = title_text.get_rect(center=(self._screen_width // 2, 230))
        surface.blit(title_text, title_rect)
        
        # Draw input fields
        y_offset = 320
        
        # IP address field (only for join)
        if self._selected_option == 'join':
            label_text = self._input_font.render("IP Address:", True, (200, 200, 200))
            label_rect = label_text.get_rect(center=(self._screen_width // 2, y_offset))
            surface.blit(label_text, label_rect)
            
            ip_rect = self._input_rects['ip']
            is_active = (self._active_input == 'ip')
            border_color = (200, 200, 255) if is_active else (150, 150, 150)
            
            pygame.draw.rect(surface, (40, 40, 60), ip_rect)
            pygame.draw.rect(surface, border_color, ip_rect, 2)
            
            ip_text = self._input_font.render(self._ip_input, True, (255, 255, 255))
            text_rect = ip_text.get_rect(midleft=(ip_rect.left + 10, ip_rect.centery))
            surface.blit(ip_text, text_rect)
            
            y_offset += 60
        
        # Port field
        port_label_text = self._input_font.render("Port:", True, (200, 200, 200))
        port_label_rect = port_label_text.get_rect(center=(self._screen_width // 2, y_offset))
        surface.blit(port_label_text, port_label_rect)
        
        port_rect = self._input_rects['port']
        is_active = (self._active_input == 'port')
        border_color = (200, 200, 255) if is_active else (150, 150, 150)
        
        pygame.draw.rect(surface, (40, 40, 60), port_rect)
        pygame.draw.rect(surface, border_color, port_rect, 2)
        
        port_text = self._input_font.render(self._port_input, True, (255, 255, 255))
        text_rect = port_text.get_rect(midleft=(port_rect.left + 10, port_rect.centery))
        surface.blit(port_text, text_rect)
        
        # Draw confirm button
        is_hovered = (self._hovered_button == 'confirm')
        button_color = (100, 200, 100) if is_hovered else (60, 120, 60)
        
        pygame.draw.rect(surface, button_color, self._confirm_button)
        pygame.draw.rect(surface, (150, 150, 150), self._confirm_button, 2)
        
        confirm_text = self._button_font.render("Connect", True, (255, 255, 255))
        confirm_rect = confirm_text.get_rect(center=self._confirm_button.center)
        surface.blit(confirm_text, confirm_rect)
        
        # Draw ESC hint
        hint_text = self._input_font.render("Press ESC to go back", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(self._screen_width // 2, self._screen_height - 100))
        surface.blit(hint_text, hint_rect)
