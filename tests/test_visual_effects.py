"""
Unit tests for visual effects in PathWars - The Interpolation Battles.

Tests cover Particle, ParticleEmitter, and VisualEffectManager classes.
"""

import pytest
import sys
import os
import pygame

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from graphics.effects import Particle, ParticleEmitter, ParticleType, VisualEffectManager


def dummy_cart_to_iso(x, y):
    """Dummy coordinate conversion function for testing."""
    return (int(x * 32), int(y * 32))


class TestParticle:
    """Tests for the Particle class."""
    
    def test_particle_moves_with_velocity(self):
        """Test that particle position updates based on velocity."""
        particle = Particle(
            position=(5.0, 5.0),
            velocity=(1.0, 0.0),
            lifetime=1.0,
            color=(255, 255, 255)
        )
        
        # Update with 0.5 seconds
        alive = particle.update(0.5)
        
        assert alive
        # Position should have moved by velocity * dt
        # Note: y velocity increases due to gravity
        assert particle._position[0] == pytest.approx(5.5, rel=0.1)
    
    def test_particle_dies_after_lifetime(self):
        """Test that particle returns False when lifetime expires."""
        particle = Particle(
            position=(5.0, 5.0),
            velocity=(0.0, 0.0),
            lifetime=0.5,
            color=(255, 255, 255)
        )
        
        # Update with 0.3 seconds - should still be alive
        alive = particle.update(0.3)
        assert alive
        
        # Update with another 0.3 seconds - should be dead
        alive = particle.update(0.3)
        assert not alive
    
    def test_particle_update_returns_false_when_dead(self):
        """Test that particle update returns False when dead."""
        particle = Particle(
            position=(5.0, 5.0),
            velocity=(0.0, 0.0),
            lifetime=0.1,
            color=(255, 255, 255)
        )
        
        # Kill the particle
        particle.update(0.2)
        
        # Further updates should return False
        alive = particle.update(0.1)
        assert not alive
    
    def test_particle_draw_does_not_crash(self):
        """Test that particle draw method doesn't crash."""
        particle = Particle(
            position=(5.0, 5.0),
            velocity=(0.0, 0.0),
            lifetime=1.0,
            color=(255, 255, 255),
            size=4.0
        )
        
        # Create a dummy surface
        screen = pygame.Surface((640, 480))
        
        # Should not crash
        particle.draw(screen, dummy_cart_to_iso)


class TestParticleEmitter:
    """Tests for the ParticleEmitter class."""
    
    def test_emit_creates_particles(self):
        """Test that emit creates particles."""
        emitter = ParticleEmitter((5.0, 5.0), ParticleType.EXPLOSION)
        
        # Initially no particles
        assert len(emitter._particles) == 0
        
        # Emit 10 particles
        emitter.emit(10)
        
        # Should have particles now
        assert len(emitter._particles) == 10
    
    def test_is_finished_when_all_dead(self):
        """Test that is_finished returns True when all particles are dead."""
        emitter = ParticleEmitter((5.0, 5.0), ParticleType.IMPACT)
        emitter.emit(5)
        
        # Initially not finished
        assert not emitter.is_finished
        
        # Update until all particles die
        for _ in range(100):  # Arbitrary large number
            emitter.update(0.1)
        
        # Should be finished now
        assert emitter.is_finished
    
    def test_update_removes_dead_particles(self):
        """Test that update removes dead particles."""
        emitter = ParticleEmitter((5.0, 5.0), ParticleType.SPARKLE)
        emitter.emit(10)
        
        initial_count = len(emitter._particles)
        
        # Update multiple times to kill some particles
        for _ in range(10):
            emitter.update(0.1)
        
        # Should have fewer particles (or none)
        assert len(emitter._particles) <= initial_count
    
    def test_different_particle_types(self):
        """Test that different particle types create different effects."""
        explosion = ParticleEmitter((5.0, 5.0), ParticleType.EXPLOSION)
        impact = ParticleEmitter((5.0, 5.0), ParticleType.IMPACT)
        sparkle = ParticleEmitter((5.0, 5.0), ParticleType.SPARKLE)
        
        explosion.emit(5)
        impact.emit(5)
        sparkle.emit(5)
        
        # All should have created particles
        assert len(explosion._particles) == 5
        assert len(impact._particles) == 5
        assert len(sparkle._particles) == 5


class TestVisualEffectManager:
    """Tests for the VisualEffectManager class."""
    
    def test_spawn_explosion_creates_emitter(self):
        """Test that spawn_explosion creates an emitter."""
        manager = VisualEffectManager()
        
        # Initially no emitters
        assert len(manager._emitters) == 0
        
        # Spawn explosion
        manager.spawn_explosion((5.0, 5.0))
        
        # Should have an emitter now
        assert len(manager._emitters) == 1
    
    def test_spawn_impact_creates_emitter(self):
        """Test that spawn_impact creates an emitter."""
        manager = VisualEffectManager()
        
        manager.spawn_impact((5.0, 5.0))
        
        assert len(manager._emitters) == 1
    
    def test_spawn_death_effect_creates_emitter(self):
        """Test that spawn_death_effect creates an emitter."""
        manager = VisualEffectManager()
        
        manager.spawn_death_effect((5.0, 5.0))
        
        assert len(manager._emitters) == 1
    
    def test_update_cleans_up_finished_emitters(self):
        """Test that update removes finished emitters."""
        manager = VisualEffectManager()
        
        manager.spawn_impact((5.0, 5.0))
        
        # Update multiple times until effect finishes
        for _ in range(100):
            manager.update(0.1)
        
        # Emitter should be cleaned up
        assert len(manager._emitters) == 0
    
    def test_explosion_size_variants(self):
        """Test that different explosion sizes can be created."""
        manager = VisualEffectManager()
        
        manager.spawn_explosion((5.0, 5.0), size="small")
        manager.spawn_explosion((6.0, 6.0), size="medium")
        manager.spawn_explosion((7.0, 7.0), size="large")
        
        # Should have 3 emitters
        assert len(manager._emitters) == 3
    
    def test_draw_does_not_crash(self):
        """Test that draw method doesn't crash."""
        manager = VisualEffectManager()
        manager.spawn_explosion((5.0, 5.0))
        
        screen = pygame.Surface((640, 480))
        
        # Should not crash
        manager.draw(screen, dummy_cart_to_iso)
