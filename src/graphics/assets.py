"""
Asset Manager for PathWars - The Interpolation Battles.

This module handles loading and caching of game assets (images, fonts, sounds).
It provides fallback placeholders if assets are missing to allow rapid prototyping.
"""

import os
import pygame
import logging
from typing import Dict, List, Optional, Tuple
from graphics.placeholder_generator import PlaceholderGenerator
from entities.tower import TowerType
from entities.enemy import EnemyType

logger = logging.getLogger(__name__)


# Asset configuration dictionary
ASSET_CONFIG = {
    "towers": {
        "dean_idle": {"path": "assets/sprites/towers/dean_idle.png", "size": (64, 64)},
        "calculus_idle": {"path": "assets/sprites/towers/calculus_idle.png", "size": (64, 64)},
        "physics_idle": {"path": "assets/sprites/towers/physics_idle.png", "size": (64, 64)},
        "statistics_idle": {"path": "assets/sprites/towers/statistics_idle.png", "size": (64, 64)},
    },
    "enemies": {
        "student_walk": {"path": "assets/sprites/enemies/student_walk.png", "size": (32, 32)},
        "variable_x_walk": {"path": "assets/sprites/enemies/variable_x_walk.png", "size": (32, 32)},
    },
    "tiles": {
        "grid_cell": {"path": "assets/sprites/tiles/grid_cell.png", "size": (32, 32)},
        # Path tiles for autotiling
        "path_h": {"path": "assets/sprites/tiles/path_straight_h.png", "size": (32, 32)},
        "path_v": {"path": "assets/sprites/tiles/path_straight_v.png", "size": (32, 32)},
        "path_ne": {"path": "assets/sprites/tiles/path_curve_ne.png", "size": (32, 32)},
        "path_nw": {"path": "assets/sprites/tiles/path_curve_nw.png", "size": (32, 32)},
        "path_se": {"path": "assets/sprites/tiles/path_curve_se.png", "size": (32, 32)},
        "path_sw": {"path": "assets/sprites/tiles/path_curve_sw.png", "size": (32, 32)},
    },
}


class AssetManager:
    """
    Singleton-like class to manage game assets.
    """
    
    _images: Dict[str, pygame.Surface] = {}
    _sprites: Dict[str, pygame.Surface] = {}
    _animations: Dict[str, List[pygame.Surface]] = {}
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
    
    @classmethod
    def load_sprite(
        cls,
        name: str,
        path: str,
        size: Optional[Tuple[int, int]] = None
    ) -> pygame.Surface:
        """
        Load an individual sprite with optional scaling.
        
        Args:
            name: Identifier for the sprite.
            path: File path to the sprite image.
            size: Optional size to scale the sprite to.
            
        Returns:
            The loaded (and optionally scaled) sprite surface.
        """
        if name in cls._sprites:
            return cls._sprites[name]
        
        try:
            sprite = pygame.image.load(path).convert_alpha()
            if size is not None:
                sprite = pygame.transform.scale(sprite, size)
            cls._sprites[name] = sprite
            logger.info(f"Loaded sprite: {name} from {path}")
            return sprite
        except (pygame.error, FileNotFoundError) as e:
            logger.warning(f"Failed to load sprite {name} from {path}: {e}. Using placeholder.")
            # Generate placeholder based on name
            placeholder = cls._generate_placeholder(name, size or (64, 64))
            cls._sprites[name] = placeholder
            return placeholder
    
    @classmethod
    def load_spritesheet(
        cls,
        name: str,
        path: str,
        frame_width: int,
        frame_height: int,
        frame_count: int
    ) -> List[pygame.Surface]:
        """
        Load spritesheet and extract frames.
        
        Args:
            name: Identifier for the animation.
            path: File path to the spritesheet image.
            frame_width: Width of each frame.
            frame_height: Height of each frame.
            frame_count: Number of frames to extract.
            
        Returns:
            List of frame surfaces.
        """
        if name in cls._animations:
            return cls._animations[name]
        
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = []
            
            for i in range(frame_count):
                x = (i * frame_width) % sheet.get_width()
                y = ((i * frame_width) // sheet.get_width()) * frame_height
                
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
                frames.append(frame)
            
            cls._animations[name] = frames
            logger.info(f"Loaded spritesheet: {name} with {frame_count} frames")
            return frames
        except (pygame.error, FileNotFoundError) as e:
            logger.warning(f"Failed to load spritesheet {name} from {path}: {e}. Using placeholder.")
            # Generate single placeholder frame
            placeholder = cls._generate_placeholder(name, (frame_width, frame_height))
            frames = [placeholder]
            cls._animations[name] = frames
            return frames
    
    @classmethod
    def get_sprite(cls, name: str) -> Optional[pygame.Surface]:
        """
        Get loaded sprite.
        
        Args:
            name: Identifier of the sprite.
            
        Returns:
            The sprite surface, or None if not found.
        """
        return cls._sprites.get(name)
    
    @classmethod
    def get_animation_frames(cls, name: str) -> Optional[List[pygame.Surface]]:
        """
        Get list of animation frames.
        
        Args:
            name: Identifier of the animation.
            
        Returns:
            List of frame surfaces, or None if not found.
        """
        return cls._animations.get(name)
    
    @classmethod
    def preload_all(cls) -> None:
        """
        Preload all assets at startup.
        
        Loads all assets defined in ASSET_CONFIG.
        """
        logger.info("Preloading all assets...")
        
        # Load tower sprites
        for sprite_name, config in ASSET_CONFIG.get("towers", {}).items():
            cls.load_sprite(sprite_name, config["path"], config.get("size"))
        
        # Load enemy sprites
        for sprite_name, config in ASSET_CONFIG.get("enemies", {}).items():
            cls.load_sprite(sprite_name, config["path"], config.get("size"))
        
        # Load tile sprites
        for sprite_name, config in ASSET_CONFIG.get("tiles", {}).items():
            cls.load_sprite(sprite_name, config["path"], config.get("size"))
        
        logger.info(f"Preloading complete. Loaded {len(cls._sprites)} sprites.")
    
    @classmethod
    def _generate_placeholder(cls, name: str, size: Tuple[int, int]) -> pygame.Surface:
        """
        Generate a placeholder sprite based on name.
        
        Args:
            name: Name of the asset to generate placeholder for.
            size: Size of the placeholder.
            
        Returns:
            A generated placeholder surface.
        """
        # Determine type from name
        if "dean" in name:
            return PlaceholderGenerator.create_tower_placeholder(TowerType.DEAN, size)
        elif "calculus" in name:
            return PlaceholderGenerator.create_tower_placeholder(TowerType.CALCULUS, size)
        elif "physics" in name:
            return PlaceholderGenerator.create_tower_placeholder(TowerType.PHYSICS, size)
        elif "statistics" in name:
            return PlaceholderGenerator.create_tower_placeholder(TowerType.STATISTICS, size)
        elif "student" in name:
            return PlaceholderGenerator.create_enemy_placeholder(EnemyType.STUDENT, size)
        elif "variable_x" in name:
            return PlaceholderGenerator.create_enemy_placeholder(EnemyType.VARIABLE_X, size)
        elif "path" in name or "grid" in name:
            return PlaceholderGenerator.create_tile_placeholder(name, size)
        else:
            # Default magenta placeholder
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill((255, 0, 255))
            return surf
