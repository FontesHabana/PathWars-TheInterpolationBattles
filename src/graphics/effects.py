"""
Visual Effects System for PathWars - The Interpolation Battles.

This module provides particle effects and visual feedback for game events.
"""

import pygame
import random
import math
from enum import Enum, auto
from typing import List, Tuple, Callable, Optional


class ParticleType(Enum):
    """Types of particle effects."""
    EXPLOSION = auto()
    IMPACT = auto()
    SPARKLE = auto()
    MATH_SYMBOL = auto()


class Particle:
    """A single particle in a visual effect."""
    
    def __init__(
        self,
        position: Tuple[float, float],
        velocity: Tuple[float, float],
        lifetime: float,
        color: Tuple[int, int, int],
        size: float = 4.0
    ):
        """
        Initialize a Particle.
        
        Args:
            position: Initial (x, y) position in grid coordinates.
            velocity: Initial (vx, vy) velocity in grid units per second.
            lifetime: How long the particle lives in seconds.
            color: RGB color tuple.
            size: Particle radius in pixels.
        """
        self._position = list(position)
        self._velocity = list(velocity)
        self._lifetime = lifetime
        self._max_lifetime = lifetime
        self._color = color
        self._size = size
    
    def update(self, dt: float) -> bool:
        """
        Update particle state.
        
        Args:
            dt: Delta time since last update in seconds.
            
        Returns:
            False if the particle is dead, True if still alive.
        """
        self._lifetime -= dt
        
        if self._lifetime <= 0:
            return False
        
        # Update position based on velocity
        self._position[0] += self._velocity[0] * dt
        self._position[1] += self._velocity[1] * dt
        
        # Apply gravity
        self._velocity[1] += 9.8 * dt  # Simple gravity
        
        return True
    
    def draw(
        self,
        screen: pygame.Surface,
        cart_to_iso: Callable[[float, float], Tuple[int, int]]
    ) -> None:
        """
        Draw the particle on screen.
        
        Args:
            screen: The pygame surface to draw on.
            cart_to_iso: Function to convert grid coordinates to screen coordinates.
        """
        # Fade out based on lifetime
        alpha = int(255 * (self._lifetime / self._max_lifetime))
        alpha = max(0, min(255, alpha))
        
        # Convert position to screen coordinates
        screen_pos = cart_to_iso(self._position[0], self._position[1])
        
        # Create a surface with alpha
        size = int(self._size)
        if size < 1:
            size = 1
        
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self._color, alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
        
        screen.blit(particle_surface, (screen_pos[0] - size, screen_pos[1] - size))


class ParticleEmitter:
    """Emits particles from a position."""
    
    def __init__(
        self,
        position: Tuple[float, float],
        particle_type: ParticleType
    ):
        """
        Initialize a ParticleEmitter.
        
        Args:
            position: Grid position to emit particles from.
            particle_type: Type of particle effect.
        """
        self._position = position
        self._particle_type = particle_type
        self._particles: List[Particle] = []
    
    def emit(self, count: int = 10) -> None:
        """
        Emit particles.
        
        Args:
            count: Number of particles to emit.
        """
        if self._particle_type == ParticleType.EXPLOSION:
            self._emit_explosion(count)
        elif self._particle_type == ParticleType.IMPACT:
            self._emit_impact(count)
        elif self._particle_type == ParticleType.SPARKLE:
            self._emit_sparkle(count)
        else:
            self._emit_generic(count)
    
    def _emit_explosion(self, count: int) -> None:
        """Emit explosion particles."""
        colors = [(255, 100, 0), (255, 200, 0), (255, 50, 0), (200, 50, 0)]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = random.choice(colors)
            lifetime = random.uniform(0.3, 0.8)
            size = random.uniform(3, 7)
            
            particle = Particle(
                self._position,
                (vx, vy),
                lifetime,
                color,
                size
            )
            self._particles.append(particle)
    
    def _emit_impact(self, count: int) -> None:
        """Emit impact particles."""
        colors = [(255, 255, 100), (255, 200, 50)]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.0  # Bias upward
            
            color = random.choice(colors)
            lifetime = random.uniform(0.2, 0.5)
            size = random.uniform(2, 4)
            
            particle = Particle(
                self._position,
                (vx, vy),
                lifetime,
                color,
                size
            )
            self._particles.append(particle)
    
    def _emit_sparkle(self, count: int) -> None:
        """Emit sparkle particles."""
        colors = [(255, 255, 255), (200, 200, 255), (255, 255, 200)]
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = random.choice(colors)
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(1, 3)
            
            particle = Particle(
                self._position,
                (vx, vy),
                lifetime,
                color,
                size
            )
            self._particles.append(particle)
    
    def _emit_generic(self, count: int) -> None:
        """Emit generic particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = (255, 255, 255)
            lifetime = random.uniform(0.3, 0.7)
            size = random.uniform(2, 5)
            
            particle = Particle(
                self._position,
                (vx, vy),
                lifetime,
                color,
                size
            )
            self._particles.append(particle)
    
    def update(self, dt: float) -> None:
        """
        Update all particles.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        # Update particles and remove dead ones
        self._particles = [p for p in self._particles if p.update(dt)]
    
    def draw(
        self,
        screen: pygame.Surface,
        cart_to_iso: Callable[[float, float], Tuple[int, int]]
    ) -> None:
        """
        Draw all particles.
        
        Args:
            screen: The pygame surface to draw on.
            cart_to_iso: Function to convert grid coordinates to screen coordinates.
        """
        for particle in self._particles:
            particle.draw(screen, cart_to_iso)
    
    @property
    def is_finished(self) -> bool:
        """Check if all particles are dead."""
        return len(self._particles) == 0


class VisualEffectManager:
    """Manages all active visual effects."""
    
    def __init__(self):
        """Initialize the VisualEffectManager."""
        self._emitters: List[ParticleEmitter] = []
    
    def spawn_explosion(
        self,
        position: Tuple[float, float],
        size: str = "small"
    ) -> None:
        """
        Spawn an explosion effect.
        
        Args:
            position: Grid position for the explosion.
            size: Size of explosion ("small", "medium", "large").
        """
        emitter = ParticleEmitter(position, ParticleType.EXPLOSION)
        
        particle_count = {
            "small": 10,
            "medium": 20,
            "large": 30
        }.get(size, 10)
        
        emitter.emit(particle_count)
        self._emitters.append(emitter)
    
    def spawn_impact(self, position: Tuple[float, float]) -> None:
        """
        Spawn an impact effect.
        
        Args:
            position: Grid position for the impact.
        """
        emitter = ParticleEmitter(position, ParticleType.IMPACT)
        emitter.emit(8)
        self._emitters.append(emitter)
    
    def spawn_death_effect(self, position: Tuple[float, float]) -> None:
        """
        Spawn a death effect.
        
        Args:
            position: Grid position for the death effect.
        """
        # Death effect is like a medium explosion
        self.spawn_explosion(position, "medium")
    
    def update(self, dt: float) -> None:
        """
        Update all effects.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        for emitter in self._emitters:
            emitter.update(dt)
        
        # Remove finished emitters
        self._emitters = [e for e in self._emitters if not e.is_finished]
    
    def draw(
        self,
        screen: pygame.Surface,
        cart_to_iso: Callable[[float, float], Tuple[int, int]]
    ) -> None:
        """
        Draw all effects.
        
        Args:
            screen: The pygame surface to draw on.
            cart_to_iso: Function to convert grid coordinates to screen coordinates.
        """
        for emitter in self._emitters:
            emitter.draw(screen, cart_to_iso)
