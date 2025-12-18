"""
Card Widget for displaying entity information in the Codex.

Renders a card with entity image, name, stats, and lore text.
"""

import logging
import pygame
from typing import Dict, Any, Optional, Union
from entities.tower import Tower, TowerType
from entities.enemy import Enemy, EnemyType
from graphics.assets import AssetManager
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
    CARD_WIDTH = 700
    CARD_HEIGHT = 500
    PADDING = 20
    IMAGE_SIZE = 320  # Size for entity image display (much larger for detail)
    
    # Colors
    BG_COLOR = (30, 30, 50)
    BORDER_COLOR = (150, 150, 200)
    TEXT_COLOR = (255, 255, 255)
    STAT_COLOR = (200, 200, 200)
    LORE_COLOR = (180, 180, 220)
    IMAGE_BG_COLOR = (50, 50, 70)
    
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
        
        # Draw tower image on the left side
        self._draw_tower_image(surface, tower_type)
        
        # Draw content on the right side
        content_x = self._x + self.IMAGE_SIZE + self.PADDING * 2
        content_width = self.CARD_WIDTH - self.IMAGE_SIZE - self.PADDING * 3
        y_offset = self._y + self.PADDING
        
        # Draw tower name
        name = get_tower_display_name(tower_type)
        name_text = self._name_font.render(name, True, self.TEXT_COLOR)
        surface.blit(name_text, (content_x, y_offset))
        y_offset += 45
        
        # Draw stats
        stats = Tower._TOWER_STATS[tower_type]
        y_offset = self._draw_stats(surface, stats, content_x, y_offset)
        y_offset += 15
        
        # Draw lore
        lore = get_tower_lore(tower_type)
        self._draw_lore(surface, lore, content_x, content_width, y_offset)
    
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
        
        # Draw enemy image on the left side
        self._draw_enemy_image(surface, enemy_type)
        
        # Draw content on the right side
        content_x = self._x + self.IMAGE_SIZE + self.PADDING * 2
        content_width = self.CARD_WIDTH - self.IMAGE_SIZE - self.PADDING * 3
        y_offset = self._y + self.PADDING
        
        # Draw enemy name
        name = get_enemy_display_name(enemy_type)
        name_text = self._name_font.render(name, True, self.TEXT_COLOR)
        surface.blit(name_text, (content_x, y_offset))
        y_offset += 45
        
        # Draw stats
        stats = Enemy._ENEMY_STATS[enemy_type]
        y_offset = self._draw_stats(surface, stats, content_x, y_offset)
        y_offset += 15
        
        # Draw lore
        lore = get_enemy_lore(enemy_type)
        self._draw_lore(surface, lore, content_x, content_width, y_offset)
    
    def _draw_tower_image(
        self,
        surface: pygame.Surface,
        tower_type: TowerType
    ) -> None:
        """
        Draw tower image on the left side of the card.
        
        Args:
            surface: Pygame surface to draw on.
            tower_type: The type of tower.
        """
        # Load sprite directly from file without pre-scaling for better quality
        sprite_path = f"assets/sprites/towers/{tower_type.name.lower()}_idle.png"
        
        try:
            # Load original image at full resolution
            sprite = pygame.image.load(sprite_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            # Fallback to AssetManager if file not found
            sprite_name = f"{tower_type.name.lower()}_idle"
            sprite = AssetManager.get_sprite(sprite_name)
        
        if sprite:
            # Create image background on the left side
            image_rect = pygame.Rect(
                self._x + self.PADDING,
                self._y + self.PADDING,
                self.IMAGE_SIZE,
                self.IMAGE_SIZE
            )
            pygame.draw.rect(surface, self.IMAGE_BG_COLOR, image_rect)
            pygame.draw.rect(surface, self.BORDER_COLOR, image_rect, 2)
            
            # Scale sprite to fill most of the area with smoothscale for best quality
            target_size = int(self.IMAGE_SIZE * 0.95)
            scaled_sprite = pygame.transform.smoothscale(sprite, (target_size, target_size))
            sprite_rect = scaled_sprite.get_rect(center=image_rect.center)
            surface.blit(scaled_sprite, sprite_rect)
    
    def _draw_enemy_image(
        self,
        surface: pygame.Surface,
        enemy_type: EnemyType
    ) -> None:
        """
        Draw enemy image on the left side of the card.
        
        Args:
            surface: Pygame surface to draw on.
            enemy_type: The type of enemy.
        """
        # Load sprite directly from file without pre-scaling for better quality
        sprite_path = f"assets/sprites/enemies/{enemy_type.name.lower()}_walk.png"
        
        try:
            # Load original image at full resolution
            sprite = pygame.image.load(sprite_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            # Fallback to AssetManager if file not found
            sprite_name = f"{enemy_type.name.lower()}_walk"
            sprite = AssetManager.get_sprite(sprite_name)
        
        if sprite:
            # Create image background on the left side
            image_rect = pygame.Rect(
                self._x + self.PADDING,
                self._y + self.PADDING,
                self.IMAGE_SIZE,
                self.IMAGE_SIZE
            )
            pygame.draw.rect(surface, self.IMAGE_BG_COLOR, image_rect)
            pygame.draw.rect(surface, self.BORDER_COLOR, image_rect, 2)
            
            # Scale sprite to fill most of the area with smoothscale for best quality
            target_size = int(self.IMAGE_SIZE * 0.95)
            scaled_sprite = pygame.transform.smoothscale(sprite, (target_size, target_size))
            sprite_rect = scaled_sprite.get_rect(center=image_rect.center)
            surface.blit(scaled_sprite, sprite_rect)
    
    def _draw_stats(
        self,
        surface: pygame.Surface,
        stats: Dict[str, Any],
        x_offset: int,
        y_offset: int
    ) -> int:
        """
        Draw stats on the card.
        
        Args:
            surface: Pygame surface to draw on.
            stats: Dictionary of stats to display.
            x_offset: X position for drawing.
            y_offset: Current Y offset for drawing.
            
        Returns:
            New Y offset after drawing stats.
        """
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
            y_offset += 28
        
        return y_offset
    
    def _draw_lore(
        self,
        surface: pygame.Surface,
        lore: str,
        x_offset: int,
        max_width: int,
        y_offset: int
    ) -> None:
        """
        Draw lore text on the card with word wrapping.
        
        Args:
            surface: Pygame surface to draw on.
            lore: Lore text to display.
            x_offset: X position for drawing.
            max_width: Maximum width for text wrapping.
            y_offset: Current Y offset for drawing.
        """
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
            y_offset += 24
