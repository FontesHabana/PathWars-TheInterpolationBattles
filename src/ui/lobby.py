"""
Lobby Screen UI Module.

Provides the lobby screen for multiplayer match configuration.
Shows configurable parameters and ready status for both players.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any
import pygame

from core.match_config import MatchConfig, Difficulty, GameSpeed, MapSize

logger = logging.getLogger(__name__)


class LobbyScreen:
    """
    Lobby screen for multiplayer match configuration.
    
    Shows configurable parameters and ready status for both players.
    Only the host can modify settings.
    
    Attributes:
        is_host: Whether the local player is the host.
        local_ready: Whether the local player is ready.
        remote_ready: Whether the remote player is ready.
    """
    
    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize the LobbyScreen.
        
        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        
        self._is_host = False
        self._config = MatchConfig()
        self._local_ready = False
        self._remote_ready = False
        self._remote_connected = True  # Assume connected for now
        
        # UI State
        self._hovered_button: Optional[str] = None
        self._active_dropdown: Optional[str] = None
        
        # Fonts
        self._title_font = pygame.font.Font(None, 72)
        self._section_font = pygame.font.Font(None, 48)
        self._label_font = pygame.font.Font(None, 36)
        self._button_font = pygame.font.Font(None, 32)
        
        # Layout constants
        self._center_x = screen_width // 2
        self._button_width = 250
        self._button_height = 50
        self._dropdown_width = 200
        self._dropdown_height = 40
        
        # Dropdown option values
        self._wave_options = [3, 5, 7, 10]
        self._difficulty_options = [Difficulty.EASY, Difficulty.NORMAL, Difficulty.HARD]
        self._speed_options = [GameSpeed.NORMAL, GameSpeed.FAST, GameSpeed.VERY_FAST]
        self._size_options = [MapSize.SMALL, MapSize.MEDIUM, MapSize.LARGE]
        self._money_options = [300, 500, 700, 1000, 1500]
        
        # Create UI elements
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up UI element positions."""
        # Configuration section starts at y=150
        config_start_y = 150
        row_height = 60
        
        # Dropdown positions (label on left, dropdown on right)
        label_x = self._center_x - 250
        dropdown_x = self._center_x + 50
        
        self._dropdowns: Dict[str, pygame.Rect] = {
            'wave_count': pygame.Rect(dropdown_x, config_start_y, self._dropdown_width, self._dropdown_height),
            'difficulty': pygame.Rect(dropdown_x, config_start_y + row_height, self._dropdown_width, self._dropdown_height),
            'game_speed': pygame.Rect(dropdown_x, config_start_y + row_height * 2, self._dropdown_width, self._dropdown_height),
            'map_size': pygame.Rect(dropdown_x, config_start_y + row_height * 3, self._dropdown_width, self._dropdown_height),
            'starting_money': pygame.Rect(dropdown_x, config_start_y + row_height * 4, self._dropdown_width, self._dropdown_height),
        }
        
        self._labels = {
            'wave_count': (label_x, config_start_y + self._dropdown_height // 2),
            'difficulty': (label_x, config_start_y + row_height + self._dropdown_height // 2),
            'game_speed': (label_x, config_start_y + row_height * 2 + self._dropdown_height // 2),
            'map_size': (label_x, config_start_y + row_height * 3 + self._dropdown_height // 2),
            'starting_money': (label_x, config_start_y + row_height * 4 + self._dropdown_height // 2),
        }
        
        # Ready status section
        ready_y = config_start_y + row_height * 5 + 40
        self._ready_positions = {
            'local': (self._center_x - 150, ready_y),
            'remote': (self._center_x + 150, ready_y),
        }
        
        # Buttons
        button_y = ready_y + 80
        self._buttons = {
            'ready': pygame.Rect(self._center_x - self._button_width // 2, button_y, self._button_width, self._button_height),
            'start': pygame.Rect(self._center_x - self._button_width // 2, button_y + 70, self._button_width, self._button_height),
            'back': pygame.Rect(self._center_x - self._button_width // 2, button_y + 140, self._button_width, self._button_height),
        }
    
    def set_host_mode(self, is_host: bool) -> None:
        """
        Set whether local player is host (can edit settings).
        
        Args:
            is_host: True if local player is the host.
        """
        self._is_host = is_host
    
    def set_config(self, config: MatchConfig) -> None:
        """
        Set the current match configuration.
        
        Args:
            config: Match configuration to use.
        """
        self._config = config
    
    def get_config(self) -> MatchConfig:
        """
        Get the current match configuration.
        
        Returns:
            Current match configuration.
        """
        return self._config
    
    def set_local_ready(self, ready: bool) -> None:
        """
        Set local player ready status.
        
        Args:
            ready: True if local player is ready.
        """
        self._local_ready = ready
    
    def set_remote_ready(self, ready: bool) -> None:
        """
        Set remote player ready status.
        
        Args:
            ready: True if remote player is ready.
        """
        self._remote_ready = ready
    
    def set_remote_connected(self, connected: bool) -> None:
        """
        Set remote player connection status.
        
        Args:
            connected: True if remote player is connected.
        """
        self._remote_connected = connected
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events.
        
        Args:
            event: Pygame event to handle.
            
        Returns:
            'start' when both players ready and host clicks start.
            'back' when back button pressed.
            None otherwise.
        """
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
            return None
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_mouse_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
        
        return None
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        """Handle mouse motion for hover effects."""
        self._hovered_button = None
        
        # Check button hovers
        for button_name, button_rect in self._buttons.items():
            if button_rect.collidepoint(pos):
                # Only highlight enabled buttons
                if button_name == 'start':
                    if self._is_host and self._local_ready and self._remote_ready:
                        self._hovered_button = button_name
                else:
                    self._hovered_button = button_name
                break
        
        # Check dropdown hovers
        if self._is_host:
            for dropdown_name, dropdown_rect in self._dropdowns.items():
                if dropdown_rect.collidepoint(pos):
                    self._hovered_button = dropdown_name
                    break
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click events."""
        # Check if clicking on active dropdown options
        if self._active_dropdown:
            result = self._handle_dropdown_click(pos)
            self._active_dropdown = None
            return result
        
        # Check dropdowns (only if host)
        if self._is_host:
            for dropdown_name, dropdown_rect in self._dropdowns.items():
                if dropdown_rect.collidepoint(pos):
                    self._active_dropdown = dropdown_name
                    return None
        
        # Check buttons
        if self._buttons['ready'].collidepoint(pos):
            self._local_ready = not self._local_ready
            return None
        
        if self._buttons['start'].collidepoint(pos):
            if self._is_host and self._local_ready and self._remote_ready:
                return 'start'
            return None
        
        if self._buttons['back'].collidepoint(pos):
            return 'back'
        
        return None
    
    def _handle_dropdown_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Handle click on dropdown menu options.
        
        Args:
            pos: Mouse position.
            
        Returns:
            None (configuration is updated internally).
        """
        if not self._active_dropdown:
            return None
        
        dropdown_rect = self._dropdowns[self._active_dropdown]
        
        # Get options for this dropdown
        if self._active_dropdown == 'wave_count':
            options = self._wave_options
        elif self._active_dropdown == 'difficulty':
            options = self._difficulty_options
        elif self._active_dropdown == 'game_speed':
            options = self._speed_options
        elif self._active_dropdown == 'map_size':
            options = self._size_options
        elif self._active_dropdown == 'starting_money':
            options = self._money_options
        else:
            return None
        
        # Check which option was clicked
        option_height = 35
        for i, option in enumerate(options):
            option_rect = pygame.Rect(
                dropdown_rect.left,
                dropdown_rect.bottom + i * option_height,
                dropdown_rect.width,
                option_height
            )
            
            if option_rect.collidepoint(pos):
                self._set_config_value(self._active_dropdown, option)
                break
        
        return None
    
    def _set_config_value(self, field: str, value: Any) -> None:
        """
        Set a configuration field value.
        
        Args:
            field: Field name to set.
            value: Value to set.
        """
        if field == 'wave_count':
            self._config.wave_count = value
        elif field == 'difficulty':
            self._config.difficulty = value
        elif field == 'game_speed':
            self._config.game_speed = value
        elif field == 'map_size':
            self._config.map_size = value
        elif field == 'starting_money':
            self._config.starting_money = value
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the lobby screen.
        
        Args:
            surface: Pygame surface to draw on.
        """
        # Draw semi-transparent background
        overlay = pygame.Surface((self._screen_width, self._screen_height))
        overlay.set_alpha(240)
        overlay.fill((20, 20, 40))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self._title_font.render("Match Configuration", True, (255, 200, 50))
        title_rect = title_text.get_rect(center=(self._center_x, 80))
        surface.blit(title_text, title_rect)
        
        # Draw configuration options
        self._draw_config_options(surface)
        
        # Draw ready status
        self._draw_ready_status(surface)
        
        # Draw buttons
        self._draw_buttons(surface)
        
        # Draw status message if remote not connected
        if not self._remote_connected:
            status_text = self._label_font.render("Waiting for opponent...", True, (200, 200, 100))
            status_rect = status_text.get_rect(center=(self._center_x, self._screen_height - 30))
            surface.blit(status_text, status_rect)
    
    def _draw_config_options(self, surface: pygame.Surface) -> None:
        """Draw configuration option labels and dropdowns."""
        label_texts = {
            'wave_count': "Wave Count:",
            'difficulty': "Difficulty:",
            'game_speed': "Game Speed:",
            'map_size': "Map Size:",
            'starting_money': "Starting Money:",
        }
        
        for field, (x, y) in self._labels.items():
            # Draw label
            label_text = self._label_font.render(label_texts[field], True, (200, 200, 200))
            label_rect = label_text.get_rect(midright=(x + 180, y))
            surface.blit(label_text, label_rect)
            
            # Draw dropdown
            self._draw_dropdown(surface, field)
    
    def _draw_dropdown(self, surface: pygame.Surface, field: str) -> None:
        """
        Draw a dropdown control.
        
        Args:
            surface: Surface to draw on.
            field: Field name for the dropdown.
        """
        dropdown_rect = self._dropdowns[field]
        
        # Determine if this dropdown is hovered or active
        is_hovered = (self._hovered_button == field)
        is_active = (self._active_dropdown == field)
        
        # Get current value text
        if field == 'wave_count':
            value_text = str(self._config.wave_count)
        elif field == 'difficulty':
            value_text = self._config.difficulty.name.capitalize()
        elif field == 'game_speed':
            speed_names = {GameSpeed.NORMAL: "1x", GameSpeed.FAST: "1.5x", GameSpeed.VERY_FAST: "2x"}
            value_text = speed_names.get(self._config.game_speed, "1x")
        elif field == 'map_size':
            size_names = {MapSize.SMALL: "15x15", MapSize.MEDIUM: "20x20", MapSize.LARGE: "25x25"}
            value_text = size_names.get(self._config.map_size, "20x20")
        elif field == 'starting_money':
            value_text = f"${self._config.starting_money}"
        else:
            value_text = ""
        
        # Draw dropdown box
        if not self._is_host:
            # Disabled appearance for non-host
            bg_color = (40, 40, 60)
            border_color = (100, 100, 100)
        elif is_hovered or is_active:
            bg_color = (70, 70, 130)
            border_color = (150, 150, 200)
        else:
            bg_color = (60, 60, 120)
            border_color = (120, 120, 150)
        
        pygame.draw.rect(surface, bg_color, dropdown_rect)
        pygame.draw.rect(surface, border_color, dropdown_rect, 2)
        
        # Draw value text
        text_color = (180, 180, 180) if not self._is_host else (255, 255, 255)
        text = self._button_font.render(value_text, True, text_color)
        text_rect = text.get_rect(midleft=(dropdown_rect.left + 10, dropdown_rect.centery))
        surface.blit(text, text_rect)
        
        # Draw dropdown arrow
        arrow_x = dropdown_rect.right - 20
        arrow_y = dropdown_rect.centery
        arrow_size = 6
        if self._is_host:
            pygame.draw.polygon(surface, text_color, [
                (arrow_x - arrow_size, arrow_y - 3),
                (arrow_x + arrow_size, arrow_y - 3),
                (arrow_x, arrow_y + 3),
            ])
        
        # Draw dropdown menu if active
        if is_active and self._is_host:
            self._draw_dropdown_menu(surface, field, dropdown_rect)
    
    def _draw_dropdown_menu(self, surface: pygame.Surface, field: str, dropdown_rect: pygame.Rect) -> None:
        """
        Draw dropdown menu options.
        
        Args:
            surface: Surface to draw on.
            field: Field name.
            dropdown_rect: Dropdown rectangle.
        """
        # Get options
        if field == 'wave_count':
            options = self._wave_options
            option_texts = [str(x) for x in options]
        elif field == 'difficulty':
            options = self._difficulty_options
            option_texts = [d.name.capitalize() for d in options]
        elif field == 'game_speed':
            options = self._speed_options
            option_texts = ["1x", "1.5x", "2x"]
        elif field == 'map_size':
            options = self._size_options
            option_texts = ["15x15", "20x20", "25x25"]
        elif field == 'starting_money':
            options = self._money_options
            option_texts = [f"${m}" for m in options]
        else:
            return
        
        # Draw menu background
        option_height = 35
        menu_height = len(options) * option_height
        menu_rect = pygame.Rect(dropdown_rect.left, dropdown_rect.bottom, dropdown_rect.width, menu_height)
        
        pygame.draw.rect(surface, (50, 50, 100), menu_rect)
        pygame.draw.rect(surface, (120, 120, 150), menu_rect, 2)
        
        # Draw options
        mouse_pos = pygame.mouse.get_pos()
        for i, (option, option_text) in enumerate(zip(options, option_texts)):
            option_rect = pygame.Rect(
                dropdown_rect.left,
                dropdown_rect.bottom + i * option_height,
                dropdown_rect.width,
                option_height
            )
            
            # Highlight on hover
            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (80, 80, 140), option_rect)
            
            # Draw option text
            text = self._button_font.render(option_text, True, (255, 255, 255))
            text_rect = text.get_rect(midleft=(option_rect.left + 10, option_rect.centery))
            surface.blit(text, text_rect)
    
    def _draw_ready_status(self, surface: pygame.Surface) -> None:
        """Draw ready status indicators for both players."""
        # Draw section title
        ready_section_y = self._ready_positions['local'][1] - 40
        section_text = self._section_font.render("Ready Status", True, (200, 200, 200))
        section_rect = section_text.get_rect(center=(self._center_x, ready_section_y))
        surface.blit(section_text, section_rect)
        
        # Draw local player status
        local_pos = self._ready_positions['local']
        self._draw_player_ready(surface, "You", self._local_ready, local_pos)
        
        # Draw remote player status
        remote_pos = self._ready_positions['remote']
        self._draw_player_ready(surface, "Opponent", self._remote_ready, remote_pos)
    
    def _draw_player_ready(self, surface: pygame.Surface, label: str, ready: bool, pos: Tuple[int, int]) -> None:
        """
        Draw a single player ready indicator.
        
        Args:
            surface: Surface to draw on.
            label: Player label text.
            ready: Whether the player is ready.
            pos: Center position.
        """
        # Draw label
        label_text = self._label_font.render(label, True, (200, 200, 200))
        label_rect = label_text.get_rect(center=(pos[0], pos[1] - 25))
        surface.blit(label_text, label_rect)
        
        # Draw checkmark or X
        indicator_size = 30
        indicator_rect = pygame.Rect(pos[0] - indicator_size // 2, pos[1], indicator_size, indicator_size)
        
        if ready:
            # Draw green checkmark
            color = (60, 200, 60)
            pygame.draw.rect(surface, color, indicator_rect, 3)
            # Draw check symbol
            pygame.draw.line(surface, color,
                           (indicator_rect.left + 5, indicator_rect.centery),
                           (indicator_rect.centerx - 2, indicator_rect.bottom - 8), 3)
            pygame.draw.line(surface, color,
                           (indicator_rect.centerx - 2, indicator_rect.bottom - 8),
                           (indicator_rect.right - 5, indicator_rect.top + 5), 3)
        else:
            # Draw red X
            color = (200, 60, 60)
            pygame.draw.rect(surface, color, indicator_rect, 3)
            # Draw X symbol
            pygame.draw.line(surface, color,
                           (indicator_rect.left + 5, indicator_rect.top + 5),
                           (indicator_rect.right - 5, indicator_rect.bottom - 5), 3)
            pygame.draw.line(surface, color,
                           (indicator_rect.right - 5, indicator_rect.top + 5),
                           (indicator_rect.left + 5, indicator_rect.bottom - 5), 3)
    
    def _draw_buttons(self, surface: pygame.Surface) -> None:
        """Draw control buttons."""
        # Ready button
        ready_color = (60, 120, 60) if self._local_ready else (100, 100, 200)
        if self._hovered_button == 'ready':
            ready_color = tuple(min(c + 40, 255) for c in ready_color)
        
        pygame.draw.rect(surface, ready_color, self._buttons['ready'])
        pygame.draw.rect(surface, (150, 150, 150), self._buttons['ready'], 2)
        
        ready_text = "Unready" if self._local_ready else "Ready"
        text = self._button_font.render(ready_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self._buttons['ready'].center)
        surface.blit(text, text_rect)
        
        # Start button (host only, enabled when both ready)
        start_enabled = self._is_host and self._local_ready and self._remote_ready
        
        if start_enabled:
            start_color = (60, 200, 60) if self._hovered_button != 'start' else (80, 220, 80)
        else:
            start_color = (40, 40, 60)
        
        pygame.draw.rect(surface, start_color, self._buttons['start'])
        pygame.draw.rect(surface, (150, 150, 150), self._buttons['start'], 2)
        
        text_color = (255, 255, 255) if start_enabled else (100, 100, 100)
        text = self._button_font.render("Start Game", True, text_color)
        text_rect = text.get_rect(center=self._buttons['start'].center)
        surface.blit(text, text_rect)
        
        # Back button
        back_color = (100, 100, 200) if self._hovered_button != 'back' else (120, 120, 220)
        
        pygame.draw.rect(surface, back_color, self._buttons['back'])
        pygame.draw.rect(surface, (150, 150, 150), self._buttons['back'], 2)
        
        text = self._button_font.render("Back", True, (255, 255, 255))
        text_rect = text.get_rect(center=self._buttons['back'].center)
        surface.blit(text, text_rect)
