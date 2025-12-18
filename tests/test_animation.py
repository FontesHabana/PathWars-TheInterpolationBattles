"""
Unit tests for animation system in PathWars - The Interpolation Battles.

Tests cover SpriteAnimator and AnimatedSprite classes.
"""

import pytest
import sys
import os
import pygame

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from graphics.animation import AnimationState, SpriteAnimator, AnimatedSprite


@pytest.fixture
def dummy_frames():
    """Create dummy frames for testing."""
    frames = []
    for i in range(5):
        surface = pygame.Surface((32, 32))
        surface.fill((i * 50, i * 50, i * 50))
        frames.append(surface)
    return frames


class TestSpriteAnimator:
    """Tests for the SpriteAnimator class."""
    
    def test_initial_frame_is_zero(self, dummy_frames):
        """Test that animator starts at frame 0."""
        animator = SpriteAnimator(dummy_frames)
        assert animator.frame_index == 0
        assert animator.current_frame == dummy_frames[0]
    
    def test_update_advances_frame(self, dummy_frames):
        """Test that update advances to next frame."""
        animator = SpriteAnimator(dummy_frames, fps=10.0)
        
        # One frame at 10fps takes 0.1 seconds
        animator.update(0.1)
        assert animator.frame_index == 1
        
        animator.update(0.1)
        assert animator.frame_index == 2
    
    def test_loop_returns_to_start(self, dummy_frames):
        """Test that looping animation returns to start."""
        animator = SpriteAnimator(dummy_frames, fps=10.0, loop=True)
        
        # Advance through all frames
        for i in range(len(dummy_frames)):
            animator.update(0.1)
        
        # Should loop back to frame 0
        assert animator.frame_index == 0
        assert not animator.is_finished
    
    def test_no_loop_stays_at_end(self, dummy_frames):
        """Test that non-looping animation stays at last frame."""
        animator = SpriteAnimator(dummy_frames, fps=10.0, loop=False)
        
        # Advance through all frames
        for i in range(len(dummy_frames) + 2):
            animator.update(0.1)
        
        # Should stay at last frame
        assert animator.frame_index == len(dummy_frames) - 1
        assert animator.is_finished
    
    def test_is_finished_only_when_not_looping(self, dummy_frames):
        """Test that is_finished is only True for non-looping animations."""
        looping = SpriteAnimator(dummy_frames, fps=10.0, loop=True)
        non_looping = SpriteAnimator(dummy_frames, fps=10.0, loop=False)
        
        # Advance both
        for i in range(len(dummy_frames)):
            looping.update(0.1)
            non_looping.update(0.1)
        
        assert not looping.is_finished
        assert non_looping.is_finished
    
    def test_reset_resets_to_start(self, dummy_frames):
        """Test that reset returns animation to first frame."""
        animator = SpriteAnimator(dummy_frames, fps=10.0)
        
        # Advance a few frames
        animator.update(0.3)
        assert animator.frame_index > 0
        
        # Reset
        animator.reset()
        assert animator.frame_index == 0
        assert not animator.is_finished
    
    def test_set_fps_changes_speed(self, dummy_frames):
        """Test that set_fps changes animation speed."""
        animator = SpriteAnimator(dummy_frames, fps=10.0)
        
        # At 10fps, 0.1s should advance one frame
        animator.update(0.1)
        assert animator.frame_index == 1
        
        # Change to 20fps
        animator.set_fps(20.0)
        
        # Now 0.05s should advance one frame
        animator.update(0.05)
        assert animator.frame_index == 2
    
    def test_requires_at_least_one_frame(self):
        """Test that animator requires at least one frame."""
        with pytest.raises(ValueError):
            SpriteAnimator([])


class TestAnimatedSprite:
    """Tests for the AnimatedSprite class."""
    
    def test_add_animation(self, dummy_frames):
        """Test adding an animation to a sprite."""
        sprite = AnimatedSprite()
        animator = SpriteAnimator(dummy_frames)
        
        sprite.add_animation(AnimationState.IDLE, animator)
        
        # First animation should be set as current
        assert sprite.current_state == AnimationState.IDLE
        assert sprite.get_current_frame() is not None
    
    def test_set_state_changes_animation(self, dummy_frames):
        """Test that set_state switches to a different animation."""
        sprite = AnimatedSprite()
        
        idle_frames = dummy_frames[:2]
        walk_frames = dummy_frames[2:]
        
        idle_animator = SpriteAnimator(idle_frames)
        walk_animator = SpriteAnimator(walk_frames)
        
        sprite.add_animation(AnimationState.IDLE, idle_animator)
        sprite.add_animation(AnimationState.WALK, walk_animator)
        
        # Start with IDLE
        assert sprite.current_state == AnimationState.IDLE
        
        # Switch to WALK
        sprite.set_state(AnimationState.WALK)
        assert sprite.current_state == AnimationState.WALK
    
    def test_update_delegates_to_animator(self, dummy_frames):
        """Test that update delegates to current animator."""
        sprite = AnimatedSprite()
        animator = SpriteAnimator(dummy_frames, fps=10.0)
        
        sprite.add_animation(AnimationState.IDLE, animator)
        
        # Update sprite
        sprite.update(0.1)
        
        # Animator should have advanced
        assert animator.frame_index == 1
    
    def test_switching_state_resets_animation(self, dummy_frames):
        """Test that switching state resets the new animation."""
        sprite = AnimatedSprite()
        
        idle_animator = SpriteAnimator(dummy_frames[:2], fps=10.0)
        walk_animator = SpriteAnimator(dummy_frames[2:], fps=10.0)
        
        sprite.add_animation(AnimationState.IDLE, idle_animator)
        sprite.add_animation(AnimationState.WALK, walk_animator)
        
        # Advance WALK animation before it's active
        walk_animator.update(0.2)
        initial_frame = walk_animator.frame_index
        
        # Switch to WALK
        sprite.set_state(AnimationState.WALK)
        
        # WALK animation should be reset
        assert walk_animator.frame_index == 0
    
    def test_get_current_frame_returns_none_when_no_animation(self):
        """Test that get_current_frame returns None when no animation is set."""
        sprite = AnimatedSprite()
        assert sprite.get_current_frame() is None
