"""
Card Widget for displaying entity information in the Codex.

Renders a card with entity image, name, stats, and lore text.
"""

import logging
import pygame
from typing import Dict, Any, Optional, Union
from entities.tower import Tower, TowerType
from entities.enemy import Enemy, EnemyType
from data.lore import (
    get_tower_display_name,
    get_tower_lore,
    get_enemy_display_name,
    get_enemy_lore,
)

logger = logging.getLogger(__name__)


class CardWidget:
    """
    Widget for rendering entity cards with stats and lore.
    
    Displays:
    - Entity name at the top
    - Stats in the middle
    - Lore text at the bottom
    - Border/frame for visual appeal
    """
    
    # Card dimensions
    CARD_WIDTH = 400
    CARD_HEIGHT = 500
    PADDING = 20
    
    # Colors
    BG_COLOR = (30, 30, 50)
    BORDER_COLOR = (150, 150, 200)
    TEXT_COLOR = (255, 255, 255)
    STAT_COLOR = (200, 200, 200)
    LORE_COLOR = (180, 180, 220)
    
    def __init__(self, x: int, y: int) -> None:
        """
        Initialize a card widget.
        
        Args:
            x: X position of the card.
            y: Y position of the card.
        """
        self._x = x
        self._y = y
        self._rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        # Fonts
        self._name_font = pygame.font.Font(None, 32)
        self._stat_font = pygame.font.Font(None, 24)
        self._lore_font = pygame.font.Font(None, 20)
    
    def draw_tower_card(
        self, 
        surface: pygame.Surface, 
        tower_type: TowerType
    ) -> None:
        """
        Draw a tower card.
        
        Args:
            surface: Pygame surface to draw on.
            tower_type: The type of tower to display.
        """
        # Draw card background and border
        pygame.draw.rect(surface, self.BG_COLOR, self._rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self._rect, 3)
        
        y_offset = self._y + self.PADDING
        
        # Draw tower name
        name = get_tower_display_name(tower_type)
        name_text = self._name_font.render(name, True, self.TEXT_COLOR)
        name_rect = name_text.get_rect(centerx=self._x + self.CARD_WIDTH // 2, top=y_offset)
        surface.blit(name_text, name_rect)
        y_offset += 50
        
        # Draw stats
        stats = Tower._TOWER_STATS[tower_type]
        y_offset = self._draw_stats(surface, stats, y_offset)
        y_offset += 20
        
        # Draw lore
        lore = get_tower_lore(tower_type)
        self._draw_lore(surface, lore, y_offset)
    
    def draw_enemy_card(
        self,
        surface: pygame.Surface,
        enemy_type: EnemyType
    ) -> None:
        """
        Draw an enemy card.
        
        Args:
            surface: Pygame surface to draw on.
            enemy_type: The type of enemy to display.
        """
        # Draw card background and border
        pygame.draw.rect(surface, self.BG_COLOR, self._rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self._rect, 3)
        
        y_offset = self._y + self.PADDING
        
        # Draw enemy name
        name = get_enemy_display_name(enemy_type)
        name_text = self._name_font.render(name, True, self.TEXT_COLOR)
        name_rect = name_text.get_rect(centerx=self._x + self.CARD_WIDTH // 2, top=y_offset)
        surface.blit(name_text, name_rect)
        y_offset += 50
        
        # Draw stats
        stats = Enemy._ENEMY_STATS[enemy_type]
        y_offset = self._draw_stats(surface, stats, y_offset)
        y_offset += 20
        
        # Draw lore
        lore = get_enemy_lore(enemy_type)
        self._draw_lore(surface, lore, y_offset)
    
    def _draw_stats(
        self,
        surface: pygame.Surface,
        stats: Dict[str, Any],
        y_offset: int
    ) -> int:
        """
        Draw stats on the card.
        
        Args:
            surface: Pygame surface to draw on.
            stats: Dictionary of stats to display.
            y_offset: Current Y offset for drawing.
            
        Returns:
            New Y offset after drawing stats.
        """
        x_offset = self._x + self.PADDING
        
        for key, value in stats.items():
            # Format stat name
            stat_name = key.replace('_', ' ').title()
            
            # Format stat value
            if isinstance(value, float):
                stat_value = f"{value:.2f}"
            else:
                stat_value = str(value)
            
            # Draw stat line
            stat_text = self._stat_font.render(
                f"{stat_name}: {stat_value}",
                True,
                self.STAT_COLOR
            )
            surface.blit(stat_text, (x_offset, y_offset))
            y_offset += 30
        
        return y_offset
    
    def _draw_lore(
        self,
        surface: pygame.Surface,
        lore: str,
        y_offset: int
    ) -> None:
        """
        Draw lore text on the card with word wrapping.
        
        Args:
            surface: Pygame surface to draw on.
            lore: Lore text to display.
            y_offset: Current Y offset for drawing.
        """
        x_offset = self._x + self.PADDING
        max_width = self.CARD_WIDTH - (2 * self.PADDING)
        
        # Word wrap the lore text
        words = lore.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self._lore_font.render(test_line, True, self.LORE_COLOR)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        for line in lines:
            line_text = self._lore_font.render(line, True, self.LORE_COLOR)
            surface.blit(line_text, (x_offset, y_offset))
            y_offset += 25
