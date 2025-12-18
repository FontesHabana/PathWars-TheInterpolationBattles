"""
Codex Panel UI Module.

Provides a panel for viewing all tower and enemy cards with their lore.
"""

import logging
from typing import Optional, Tuple, List
import pygame

from entities.tower import TowerType
from entities.enemy import EnemyType
from ui.card_widget import CardWidget

logger = logging.getLogger(__name__)


class CodexPanel:
    """
    Codex panel for displaying entity cards with lore.
    
    Features:
    - Two tabs: Torres (Towers) and Enemigos (Enemies)
    - Navigation between cards with arrow keys or buttons
    - Close button to return to main menu
    
    Attributes:
        visible: Whether the codex panel is currently visible.
        current_tab: Current tab ('torres' or 'enemigos').
        current_index: Index of the currently displayed card.
    """
    
    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize the CodexPanel.
        
        Args:
            screen_width: Width of the screen in pixels.
            screen_height: Height of the screen in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._visible = False
        self._current_tab = 'torres'  # 'torres' or 'enemigos'
        self._current_index = 0
        
        # Fonts
        self._title_font = pygame.font.Font(None, 64)
        self._tab_font = pygame.font.Font(None, 40)
        self._button_font = pygame.font.Font(None, 32)
        
        # Tab buttons
        tab_width = 200
        tab_height = 50
        center_x = screen_width // 2
        tab_y = 100
        
        self._tab_buttons = {
            'torres': pygame.Rect(center_x - tab_width - 10, tab_y, tab_width, tab_height),
            'enemigos': pygame.Rect(center_x + 10, tab_y, tab_width, tab_height),
        }
        
        # Navigation buttons
        nav_button_width = 60
        nav_button_height = 60
        nav_y = screen_height // 2
        
        self._nav_buttons = {
            'prev': pygame.Rect(50, nav_y, nav_button_width, nav_button_height),
            'next': pygame.Rect(screen_width - 50 - nav_button_width, nav_y, nav_button_width, nav_button_height),
        }
        
        # Close button
        close_width = 150
        close_height = 50
        self._close_button = pygame.Rect(
            center_x - close_width // 2,
            screen_height - 80,
            close_width,
            close_height
        )
        
        # Card widget
        card_x = (screen_width - CardWidget.CARD_WIDTH) // 2
        card_y = 200
        self._card_widget = CardWidget(card_x, card_y)
        
        # Entity lists
        self._tower_types: List[TowerType] = [
            TowerType.DEAN,
            TowerType.CALCULUS,
            TowerType.PHYSICS,
            TowerType.STATISTICS,
        ]
        
        self._enemy_types: List[EnemyType] = [
            EnemyType.STUDENT,
            EnemyType.VARIABLE_X,
        ]
        
        # Hover state
        self._hovered_button: Optional[str] = None
    
    @property
    def visible(self) -> bool:
        """Check if the codex panel is visible."""
        return self._visible
    
    @property
    def current_tab(self) -> str:
        """Get the current tab ('torres' or 'enemigos')."""
        return self._current_tab
    
    @property
    def current_index(self) -> int:
        """Get the current card index."""
        return self._current_index
    
    def show(self) -> None:
        """Show the codex panel."""
        self._visible = True
        self._current_tab = 'torres'
        self._current_index = 0
    
    def hide(self) -> None:
        """Hide the codex panel."""
        self._visible = False
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events.
        
        Args:
            event: Pygame event to handle.
            
        Returns:
            Action string ('close') or None.
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
        
        # Check tab buttons
        for tab_name, tab_rect in self._tab_buttons.items():
            if tab_rect.collidepoint(pos):
                self._hovered_button = tab_name
                return
        
        # Check navigation buttons
        for nav_name, nav_rect in self._nav_buttons.items():
            if nav_rect.collidepoint(pos):
                self._hovered_button = nav_name
                return
        
        # Check close button
        if self._close_button.collidepoint(pos):
            self._hovered_button = 'close'
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click events."""
        # Check tab buttons
        for tab_name, tab_rect in self._tab_buttons.items():
            if tab_rect.collidepoint(pos):
                if self._current_tab != tab_name:
                    self._current_tab = tab_name
                    self._current_index = 0
                return None
        
        # Check navigation buttons
        if self._nav_buttons['prev'].collidepoint(pos):
            self._navigate_prev()
            return None
        
        if self._nav_buttons['next'].collidepoint(pos):
            self._navigate_next()
            return None
        
        # Check close button
        if self._close_button.collidepoint(pos):
            return 'close'
        
        return None
    
    def _handle_keydown(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard input."""
        if event.key == pygame.K_ESCAPE:
            return 'close'
        elif event.key == pygame.K_LEFT:
            self._navigate_prev()
        elif event.key == pygame.K_RIGHT:
            self._navigate_next()
        elif event.key == pygame.K_TAB:
            # Switch tabs
            self._current_tab = 'enemigos' if self._current_tab == 'torres' else 'torres'
            self._current_index = 0
        
        return None
    
    def _navigate_prev(self) -> None:
        """Navigate to the previous card."""
        if self._current_index > 0:
            self._current_index -= 1
    
    def _navigate_next(self) -> None:
        """Navigate to the next card."""
        max_index = self._get_max_index()
        if self._current_index < max_index:
            self._current_index += 1
    
    def _get_max_index(self) -> int:
        """Get the maximum index for the current tab."""
        if self._current_tab == 'torres':
            return len(self._tower_types) - 1
        else:
            return len(self._enemy_types) - 1
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the codex panel.
        
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
        title_text = self._title_font.render("Codex", True, (255, 200, 50))
        title_rect = title_text.get_rect(center=(self._screen_width // 2, 50))
        surface.blit(title_text, title_rect)
        
        # Draw tabs
        self._draw_tabs(surface)
        
        # Draw current card
        self._draw_current_card(surface)
        
        # Draw navigation buttons
        self._draw_navigation_buttons(surface)
        
        # Draw close button
        self._draw_close_button(surface)
        
        # Draw card counter
        self._draw_card_counter(surface)
    
    def _draw_tabs(self, surface: pygame.Surface) -> None:
        """Draw tab buttons."""
        tab_labels = {
            'torres': "Torres",
            'enemigos': "Enemigos",
        }
        
        for tab_name, tab_rect in self._tab_buttons.items():
            # Tab color based on state
            is_active = (self._current_tab == tab_name)
            is_hovered = (self._hovered_button == tab_name)
            
            if is_active:
                color = (100, 100, 200)
            elif is_hovered:
                color = (80, 80, 160)
            else:
                color = (60, 60, 120)
            
            pygame.draw.rect(surface, color, tab_rect)
            pygame.draw.rect(surface, (150, 150, 150), tab_rect, 2)
            
            # Tab text
            text = self._tab_font.render(tab_labels[tab_name], True, (255, 255, 255))
            text_rect = text.get_rect(center=tab_rect.center)
            surface.blit(text, text_rect)
    
    def _draw_current_card(self, surface: pygame.Surface) -> None:
        """Draw the current card based on tab and index."""
        if self._current_tab == 'torres':
            tower_type = self._tower_types[self._current_index]
            self._card_widget.draw_tower_card(surface, tower_type)
        else:
            enemy_type = self._enemy_types[self._current_index]
            self._card_widget.draw_enemy_card(surface, enemy_type)
    
    def _draw_navigation_buttons(self, surface: pygame.Surface) -> None:
        """Draw navigation arrow buttons."""
        max_index = self._get_max_index()
        
        # Previous button
        if self._current_index > 0:
            is_hovered = (self._hovered_button == 'prev')
            color = (100, 200, 100) if is_hovered else (60, 120, 60)
            pygame.draw.rect(surface, color, self._nav_buttons['prev'])
            pygame.draw.rect(surface, (150, 150, 150), self._nav_buttons['prev'], 2)
            
            # Draw arrow
            text = self._button_font.render("<", True, (255, 255, 255))
            text_rect = text.get_rect(center=self._nav_buttons['prev'].center)
            surface.blit(text, text_rect)
        
        # Next button
        if self._current_index < max_index:
            is_hovered = (self._hovered_button == 'next')
            color = (100, 200, 100) if is_hovered else (60, 120, 60)
            pygame.draw.rect(surface, color, self._nav_buttons['next'])
            pygame.draw.rect(surface, (150, 150, 150), self._nav_buttons['next'], 2)
            
            # Draw arrow
            text = self._button_font.render(">", True, (255, 255, 255))
            text_rect = text.get_rect(center=self._nav_buttons['next'].center)
            surface.blit(text, text_rect)
    
    def _draw_close_button(self, surface: pygame.Surface) -> None:
        """Draw the close button."""
        is_hovered = (self._hovered_button == 'close')
        color = (200, 100, 100) if is_hovered else (120, 60, 60)
        
        pygame.draw.rect(surface, color, self._close_button)
        pygame.draw.rect(surface, (150, 150, 150), self._close_button, 2)
        
        text = self._button_font.render("Close", True, (255, 255, 255))
        text_rect = text.get_rect(center=self._close_button.center)
        surface.blit(text, text_rect)
    
    def _draw_card_counter(self, surface: pygame.Surface) -> None:
        """Draw card counter showing current position."""
        max_index = self._get_max_index()
        counter_text = f"{self._current_index + 1} / {max_index + 1}"
        
        counter_font = pygame.font.Font(None, 28)
        text = counter_font.render(counter_text, True, (200, 200, 200))
        text_rect = text.get_rect(center=(self._screen_width // 2, self._screen_height - 120))
        surface.blit(text, text_rect)
