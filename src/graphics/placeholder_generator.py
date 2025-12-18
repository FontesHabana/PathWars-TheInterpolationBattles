"""
Placeholder Generator for PathWars - The Interpolation Battles.

Generates visual placeholders when asset files are missing to allow
the game to run gracefully without all assets.
"""

import pygame
from typing import Tuple
from entities.tower import TowerType
from entities.enemy import EnemyType


class PlaceholderGenerator:
    """Generates sprite placeholders when assets are missing."""
    
    # Color palette for placeholders
    TOWER_COLORS = {
        TowerType.DEAN: (0, 0, 255),          # Blue
        TowerType.CALCULUS: (0, 255, 0),      # Green
        TowerType.PHYSICS: (255, 165, 0),     # Orange
        TowerType.STATISTICS: (128, 0, 128),  # Purple
    }
    
    ENEMY_COLORS = {
        EnemyType.STUDENT: (255, 0, 0),       # Red
        EnemyType.VARIABLE_X: (255, 255, 0),  # Yellow
    }
    
    @staticmethod
    def create_tower_placeholder(
        tower_type: TowerType,
        size: Tuple[int, int] = (64, 64)
    ) -> pygame.Surface:
        """
        Create a placeholder for tower with distinctive shape and color.
        
        Args:
            tower_type: The type of tower.
            size: Size of the placeholder surface.
            
        Returns:
            A pygame Surface with the placeholder graphic.
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        color = PlaceholderGenerator.TOWER_COLORS.get(tower_type, (255, 0, 255))
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        radius = min(size[0], size[1]) // 3
        
        # Draw different shapes based on tower type
        if tower_type == TowerType.DEAN:
            # Square for tank/blocker
            rect = pygame.Rect(
                center_x - radius,
                center_y - radius,
                radius * 2,
                radius * 2
            )
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            
        elif tower_type == TowerType.CALCULUS:
            # Triangle for ranged
            points = [
                (center_x, center_y - radius),
                (center_x - radius, center_y + radius),
                (center_x + radius, center_y + radius),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            
        elif tower_type == TowerType.PHYSICS:
            # Pentagon for cannon/AoE
            import math
            points = []
            for i in range(5):
                angle = (i * 2 * math.pi / 5) - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            
        elif tower_type == TowerType.STATISTICS:
            # Star for support
            import math
            outer_radius = radius
            inner_radius = radius * 0.5
            points = []
            for i in range(10):
                angle = (i * math.pi / 5) - math.pi / 2
                r = outer_radius if i % 2 == 0 else inner_radius
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        else:
            # Default circle
            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 2)
        
        return surface
    
    @staticmethod
    def create_enemy_placeholder(
        enemy_type: EnemyType,
        size: Tuple[int, int] = (32, 32)
    ) -> pygame.Surface:
        """
        Create a placeholder for enemy.
        
        Args:
            enemy_type: The type of enemy.
            size: Size of the placeholder surface.
            
        Returns:
            A pygame Surface with the placeholder graphic.
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        color = PlaceholderGenerator.ENEMY_COLORS.get(enemy_type, (255, 0, 255))
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        radius = min(size[0], size[1]) // 3
        
        # Draw different shapes for enemies
        if enemy_type == EnemyType.STUDENT:
            # Circle for basic enemy
            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 2)
            
        elif enemy_type == EnemyType.VARIABLE_X:
            # Diamond for fast enemy
            points = [
                (center_x, center_y - radius),
                (center_x + radius, center_y),
                (center_x, center_y + radius),
                (center_x - radius, center_y),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        else:
            # Default circle
            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 2)
        
        return surface
    
    @staticmethod
    def create_tile_placeholder(
        tile_type: str,
        size: Tuple[int, int] = (32, 32)
    ) -> pygame.Surface:
        """
        Create a placeholder for tile.
        
        Args:
            tile_type: The type of tile (e.g., "path_h", "path_v").
            size: Size of the placeholder surface.
            
        Returns:
            A pygame Surface with the placeholder graphic.
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Base color for path tiles
        path_color = (150, 100, 50)  # Brown
        grid_color = (50, 50, 50)    # Dark gray
        
        if tile_type == "grid_cell":
            # Grid cell - just a border
            pygame.draw.rect(surface, grid_color, surface.get_rect(), 1)
            
        elif "path" in tile_type:
            # Path tiles - filled rectangle with direction indicator
            pygame.draw.rect(surface, path_color, surface.get_rect())
            
            # Add direction indicator based on type
            center_x = size[0] // 2
            center_y = size[1] // 2
            
            if "h" in tile_type:  # Horizontal
                pygame.draw.line(surface, (200, 150, 100), (0, center_y), (size[0], center_y), 3)
            elif "v" in tile_type:  # Vertical
                pygame.draw.line(surface, (200, 150, 100), (center_x, 0), (center_x, size[1]), 3)
            elif "ne" in tile_type:  # North-East curve
                pygame.draw.arc(surface, (200, 150, 100), 
                              pygame.Rect(0, 0, size[0], size[1]), 0, 1.57, 3)
            elif "nw" in tile_type:  # North-West curve
                pygame.draw.arc(surface, (200, 150, 100),
                              pygame.Rect(0, 0, size[0], size[1]), 1.57, 3.14, 3)
            elif "se" in tile_type:  # South-East curve
                pygame.draw.arc(surface, (200, 150, 100),
                              pygame.Rect(0, 0, size[0], size[1]), -1.57, 0, 3)
            elif "sw" in tile_type:  # South-West curve
                pygame.draw.arc(surface, (200, 150, 100),
                              pygame.Rect(0, 0, size[0], size[1]), 3.14, 4.71, 3)
        else:
            # Unknown tile type - magenta placeholder
            surface.fill((255, 0, 255))
        
        return surface
