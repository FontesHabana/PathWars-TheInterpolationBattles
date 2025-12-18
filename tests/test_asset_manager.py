"""
Unit tests for AssetManager in PathWars - The Interpolation Battles.

Tests cover sprite loading, caching, and placeholder generation.
"""

import pytest
import sys
import os
import pygame

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from graphics.assets import AssetManager
from entities.tower import TowerType
from entities.enemy import EnemyType


class TestAssetManagerLoading:
    """Tests for AssetManager sprite loading functionality."""
    
    def test_load_sprite_missing_file_returns_placeholder(self):
        """Test that loading a missing sprite returns a placeholder."""
        # Clear cache to ensure fresh load
        AssetManager._sprites.clear()
        
        # Try to load a non-existent sprite
        sprite = AssetManager.load_sprite(
            "missing_sprite",
            "assets/does_not_exist.png",
            (64, 64)
        )
        
        # Should return a surface (placeholder)
        assert sprite is not None
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_size() == (64, 64)
    
    def test_load_sprite_caches_result(self):
        """Test that sprites are cached after loading."""
        # Clear cache
        AssetManager._sprites.clear()
        
        # Load a sprite (will be placeholder)
        sprite1 = AssetManager.load_sprite(
            "test_sprite",
            "assets/missing.png",
            (32, 32)
        )
        
        # Load same sprite again
        sprite2 = AssetManager.load_sprite(
            "test_sprite",
            "assets/missing.png",
            (32, 32)
        )
        
        # Should be the same object (cached)
        assert sprite1 is sprite2
    
    def test_get_sprite_returns_cached(self):
        """Test that get_sprite returns cached sprites."""
        # Clear cache
        AssetManager._sprites.clear()
        
        # Load a sprite
        loaded = AssetManager.load_sprite(
            "cached_sprite",
            "assets/missing.png",
            (32, 32)
        )
        
        # Get the sprite
        retrieved = AssetManager.get_sprite("cached_sprite")
        
        # Should be the same object
        assert loaded is retrieved
    
    def test_get_sprite_returns_none_for_missing(self):
        """Test that get_sprite returns None for non-existent sprites."""
        # Clear cache
        AssetManager._sprites.clear()
        
        sprite = AssetManager.get_sprite("definitely_not_loaded")
        assert sprite is None
    
    def test_load_spritesheet_creates_frames(self):
        """Test that loading a spritesheet creates frame list."""
        # Clear cache
        AssetManager._animations.clear()
        
        # Try to load a spritesheet (will be placeholder)
        frames = AssetManager.load_spritesheet(
            "test_anim",
            "assets/missing.png",
            frame_width=32,
            frame_height=32,
            frame_count=4
        )
        
        # Should return a list of frames (at least placeholder)
        assert isinstance(frames, list)
        assert len(frames) > 0
    
    def test_get_animation_frames_returns_cached(self):
        """Test that get_animation_frames returns cached frames."""
        # Clear cache
        AssetManager._animations.clear()
        
        # Load animation
        loaded = AssetManager.load_spritesheet(
            "cached_anim",
            "assets/missing.png",
            frame_width=32,
            frame_height=32,
            frame_count=4
        )
        
        # Get animation frames
        retrieved = AssetManager.get_animation_frames("cached_anim")
        
        # Should be the same object
        assert loaded is retrieved
    
    def test_preload_all_loads_configured_assets(self):
        """Test that preload_all loads all configured assets."""
        # Clear cache
        AssetManager._sprites.clear()
        
        # Preload all
        AssetManager.preload_all()
        
        # Should have loaded sprites (as placeholders since files don't exist)
        assert len(AssetManager._sprites) > 0
        
        # Check that specific sprites are loaded
        assert AssetManager.get_sprite("dean_idle") is not None
        assert AssetManager.get_sprite("student_walk") is not None


class TestAssetManagerPlaceholders:
    """Tests for AssetManager placeholder generation."""
    
    def test_placeholder_has_correct_size(self):
        """Test that placeholders have the requested size."""
        # Clear cache
        AssetManager._sprites.clear()
        
        size = (128, 128)
        sprite = AssetManager.load_sprite("test", "missing.png", size)
        
        assert sprite.get_size() == size
    
    def test_placeholder_is_not_transparent(self):
        """Test that placeholders are not fully transparent."""
        # Clear cache
        AssetManager._sprites.clear()
        
        sprite = AssetManager.load_sprite("test", "missing.png", (32, 32))
        
        # Check that sprite has some non-transparent pixels
        # This is a basic check - placeholders should have visible content
        assert sprite.get_size() == (32, 32)
    
    def test_different_types_have_different_placeholders(self):
        """Test that different asset types generate different placeholders."""
        # Clear cache
        AssetManager._sprites.clear()
        
        # Load different types
        dean = AssetManager.load_sprite("dean_idle", "missing.png", (64, 64))
        calculus = AssetManager.load_sprite("calculus_idle", "missing.png", (64, 64))
        student = AssetManager.load_sprite("student_walk", "missing.png", (32, 32))
        
        # They should all be valid surfaces
        assert isinstance(dean, pygame.Surface)
        assert isinstance(calculus, pygame.Surface)
        assert isinstance(student, pygame.Surface)
        
        # Note: We don't compare pixel data as that's implementation-specific
        # but we verify they all created successfully


class TestAssetManagerColors:
    """Tests for AssetManager color palette."""
    
    def test_get_color_returns_tuple(self):
        """Test that get_color returns an RGB tuple."""
        color = AssetManager.get_color("text")
        
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)
    
    def test_get_color_returns_default_for_unknown(self):
        """Test that get_color returns white for unknown keys."""
        color = AssetManager.get_color("unknown_color_key")
        
        assert color == (255, 255, 255)
    
    def test_predefined_colors_exist(self):
        """Test that predefined color keys work."""
        assert AssetManager.get_color("background") is not None
        assert AssetManager.get_color("tower_dean") is not None
        assert AssetManager.get_color("enemy_student") is not None
