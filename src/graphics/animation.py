"""
Animation System for PathWars - The Interpolation Battles.

This module provides sprite animation support with multiple animation states.
"""

import pygame
from enum import Enum, auto
from typing import List, Dict, Optional


class AnimationState(Enum):
    """Animation states for sprites."""
    IDLE = auto()
    WALK = auto()
    ATTACK = auto()
    DIE = auto()


class SpriteAnimator:
    """
    Manages frame-based sprite animations.
    
    Attributes:
        frames: List of animation frames.
        fps: Frames per second for animation playback.
        loop: Whether the animation should loop.
    """
    
    def __init__(
        self,
        frames: List[pygame.Surface],
        fps: float = 10.0,
        loop: bool = True
    ):
        """
        Initialize a SpriteAnimator.
        
        Args:
            frames: List of pygame surfaces representing animation frames.
            fps: Animation playback speed in frames per second.
            loop: Whether to loop the animation when it reaches the end.
        """
        if not frames:
            raise ValueError("SpriteAnimator requires at least one frame")
        
        self._frames = frames
        self._fps = fps
        self._loop = loop
        self._frame_index = 0
        self._time_accumulator = 0.0
        self._finished = False
    
    @property
    def current_frame(self) -> pygame.Surface:
        """Get the current animation frame."""
        return self._frames[self._frame_index]
    
    @property
    def is_finished(self) -> bool:
        """Check if animation has finished (only meaningful for non-looping animations)."""
        return self._finished
    
    @property
    def frame_index(self) -> int:
        """Get the current frame index."""
        return self._frame_index
    
    def update(self, dt: float) -> None:
        """
        Update animation state.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        if self._finished:
            return
        
        self._time_accumulator += dt
        frame_duration = 1.0 / self._fps
        
        # Advance frames based on accumulated time
        while self._time_accumulator >= frame_duration:
            self._time_accumulator -= frame_duration
            self._frame_index += 1
            
            if self._frame_index >= len(self._frames):
                if self._loop:
                    self._frame_index = 0
                else:
                    self._frame_index = len(self._frames) - 1
                    self._finished = True
                    break
    
    def reset(self) -> None:
        """Reset animation to the first frame."""
        self._frame_index = 0
        self._time_accumulator = 0.0
        self._finished = False
    
    def set_fps(self, fps: float) -> None:
        """
        Set animation playback speed.
        
        Args:
            fps: New frames per second value.
        """
        self._fps = fps


class AnimatedSprite:
    """
    Sprite with multiple animation states.
    
    Manages different animations for different states (idle, walk, attack, etc.)
    and handles transitions between them.
    """
    
    def __init__(self):
        """Initialize an AnimatedSprite with no animations."""
        self._animations: Dict[AnimationState, SpriteAnimator] = {}
        self._current_state: Optional[AnimationState] = None
        self._current_animator: Optional[SpriteAnimator] = None
    
    def add_animation(
        self,
        state: AnimationState,
        animator: SpriteAnimator
    ) -> None:
        """
        Add an animation for a specific state.
        
        Args:
            state: The animation state to associate with this animator.
            animator: The SpriteAnimator to use for this state.
        """
        self._animations[state] = animator
        
        # If this is the first animation, set it as current
        if self._current_state is None:
            self._current_state = state
            self._current_animator = animator
    
    def set_state(self, state: AnimationState) -> None:
        """
        Change to a different animation state.
        
        Args:
            state: The new animation state to switch to.
        """
        if state not in self._animations:
            return
        
        # Only switch if it's a different state
        if state != self._current_state:
            self._current_state = state
            self._current_animator = self._animations[state]
            self._current_animator.reset()
    
    def update(self, dt: float) -> None:
        """
        Update the current animation.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        if self._current_animator is not None:
            self._current_animator.update(dt)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """
        Get the current animation frame.
        
        Returns:
            The current frame surface, or None if no animation is set.
        """
        if self._current_animator is not None:
            return self._current_animator.current_frame
        return None
    
    @property
    def current_state(self) -> Optional[AnimationState]:
        """Get the current animation state."""
        return self._current_state
