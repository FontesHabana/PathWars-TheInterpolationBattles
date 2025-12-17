"""
Asset Manager for PathWars - The Interpolation Battles.

This module handles loading and caching of game assets (images, fonts, sounds).
It provides fallback placeholders if assets are missing to allow rapid prototyping.
"""

import os
import pygame
from typing import Dict, Tuple

class AssetManager:
    """
    Singleton-like class to manage game assets.
    """
    
    _images: Dict[str, pygame.Surface] = {}
    _fonts: Dict[str, pygame.font.Font] = {}
    
    # Placeholder colors
    COLORS = {
        "grid_line": (0, 255, 255),       # Cyan
        "background": (10, 10, 30),       # Dark Blue
        "tower_dean": (0, 0, 255),        # Blue
        "tower_calculus": (0, 255, 0),    # Green
        "tower_physics": (255, 165, 0),   # Orange
        "tower_statistics": (128, 0, 128),# Purple
        "enemy_student": (255, 0, 0),     # Red
        "enemy_variable_x": (255, 255, 0),# Yellow
        "text": (255, 255, 255),          # White
    }

    @classmethod
    def load_image(cls, name: str, path: str) -> pygame.Surface:
        """
        Load an image from disk or return a placeholder if not found.
        """
        if name in cls._images:
            return cls._images[name]
            
        try:
            image = pygame.image.load(path).convert_alpha()
            cls._images[name] = image
            return image
        except (pygame.error, FileNotFoundError):
            # Create a placeholder surface
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 255)) # Magenta = Missing Texture
            cls._images[name] = surf
            return surf

    @classmethod
    def get_font(cls, size: int = 24) -> pygame.font.Font:
        """
        Get a default system font of the specified size.
        """
        key = f"default_{size}"
        if key in cls._fonts:
            return cls._fonts[key]
            
        font = pygame.font.SysFont("Arial", size)
        cls._fonts[key] = font
        return font

    @classmethod
    def get_color(cls, key: str) -> Tuple[int, int, int]:
        """Get a color from the palette."""
        return cls.COLORS.get(key, (255, 255, 255))
