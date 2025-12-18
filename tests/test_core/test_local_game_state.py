"""
Unit tests for LocalGameState and GameState serialization.

Tests cover:
- GameState serialization (to_dict) and deserialization (from_dict)
- LocalGameState instantiation and update
- LocalGameState sync_with_server functionality
- Particle, animation, and interpolation updates
"""

import sys
import os
import pytest

# Insert src at the beginning of sys.path to ensure it's found before tests/core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from core.game_state import GameState, GamePhase
from core.local_game_state import (
    LocalGameState,
    Particle,
    Animation,
    InterpolatedPosition,
)


class TestGameStateSerialization:
    """Tests for GameState serialization methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        GameState.reset_instance()
        self.game_state = GameState()
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_to_dict_basic(self):
        """Test basic to_dict returns expected structure."""
        data = self.game_state.to_dict()
        
        assert 'money' in data
        assert 'lives' in data
        assert 'phase' in data
        assert 'entities' in data
    
    def test_to_dict_values(self):
        """Test to_dict returns correct values."""
        self.game_state.add_money(500)  # Now 1500
        self.game_state.lose_life()     # Now 9 lives
        
        data = self.game_state.to_dict()
        
        assert data['money'] == 1500
        assert data['lives'] == 9
        assert data['phase'] == 'PLANNING'
    
    def test_to_dict_entities_summary(self):
        """Test to_dict includes entities summary."""
        # Create a mock entity with id and position
        class MockEntity:
            def __init__(self, entity_id, x, y):
                self.id = entity_id
                self.position = type('Position', (), {'x': x, 'y': y})()
        
        entity1 = MockEntity('entity-1', 10.0, 20.0)
        entity2 = MockEntity('entity-2', 30.0, 40.0)
        
        self.game_state.add_entity('enemies', entity1)
        self.game_state.add_entity('enemies', entity2)
        
        data = self.game_state.to_dict()
        
        assert 'enemies' in data['entities']
        assert len(data['entities']['enemies']) == 2
        
        # Check first entity data
        enemy1_data = data['entities']['enemies'][0]
        assert enemy1_data['id'] == 'entity-1'
        assert enemy1_data['position']['x'] == 10.0
        assert enemy1_data['position']['y'] == 20.0
    
    def test_from_dict_updates_money(self):
        """Test from_dict updates money."""
        data = {'money': 2000}
        self.game_state.from_dict(data)
        
        assert self.game_state.money == 2000
    
    def test_from_dict_updates_lives(self):
        """Test from_dict updates lives."""
        data = {'lives': 5}
        self.game_state.from_dict(data)
        
        assert self.game_state.lives == 5
    
    def test_from_dict_updates_phase(self):
        """Test from_dict updates phase."""
        data = {'phase': 'BATTLE'}
        self.game_state.from_dict(data)
        
        assert self.game_state.current_phase == GamePhase.BATTLE
    
    def test_from_dict_partial_update(self):
        """Test from_dict can update only some fields."""
        original_lives = self.game_state.lives
        data = {'money': 3000}
        self.game_state.from_dict(data)
        
        assert self.game_state.money == 3000
        assert self.game_state.lives == original_lives
    
    def test_from_dict_invalid_phase_ignored(self):
        """Test from_dict ignores invalid phase names."""
        original_phase = self.game_state.current_phase
        data = {'phase': 'INVALID_PHASE'}
        self.game_state.from_dict(data)
        
        assert self.game_state.current_phase == original_phase
    
    def test_to_dict_from_dict_roundtrip(self):
        """Test serialization roundtrip preserves state."""
        self.game_state.add_money(500)
        self.game_state.lose_life()
        self.game_state.lose_life()
        
        original_money = self.game_state.money
        original_lives = self.game_state.lives
        original_phase = self.game_state.current_phase
        
        data = self.game_state.to_dict()
        
        # Reset and apply
        self.game_state.reset()
        self.game_state.from_dict(data)
        
        assert self.game_state.money == original_money
        assert self.game_state.lives == original_lives
        assert self.game_state.current_phase == original_phase


class TestLocalGameStateInstantiation:
    """Tests for LocalGameState instantiation."""
    
    def test_local_game_state_creation(self):
        """Test LocalGameState can be instantiated."""
        local_state = LocalGameState()
        
        assert local_state is not None
        assert isinstance(local_state, LocalGameState)
    
    def test_local_game_state_initial_state(self):
        """Test LocalGameState has correct initial state."""
        local_state = LocalGameState()
        
        assert local_state.particles == []
        assert local_state.animations == {}
        assert local_state.interpolated_entity_positions == {}
    
    def test_multiple_instances_independent(self):
        """Test multiple LocalGameState instances are independent."""
        state1 = LocalGameState()
        state2 = LocalGameState()
        
        state1.add_particle(Particle(x=1.0, y=2.0))
        
        assert len(state1.particles) == 1
        assert len(state2.particles) == 0


class TestLocalGameStateParticles:
    """Tests for LocalGameState particle management."""
    
    def test_add_particle(self):
        """Test adding a particle."""
        local_state = LocalGameState()
        particle = Particle(x=10.0, y=20.0, vx=1.0, vy=-1.0)
        
        local_state.add_particle(particle)
        
        assert len(local_state.particles) == 1
        assert local_state.particles[0] == particle
    
    def test_particle_update_moves_particle(self):
        """Test particle update moves particles based on velocity."""
        local_state = LocalGameState()
        particle = Particle(x=10.0, y=20.0, vx=5.0, vy=-10.0, lifetime=2.0)
        local_state.add_particle(particle)
        
        local_state.update(0.5)  # 0.5 seconds
        
        # Position should be updated: x = 10 + 5*0.5 = 12.5, y = 20 + (-10)*0.5 = 15
        assert pytest.approx(particle.x, abs=0.01) == 12.5
        assert pytest.approx(particle.y, abs=0.01) == 15.0
    
    def test_particle_removed_when_lifetime_expires(self):
        """Test particles are removed when lifetime expires."""
        local_state = LocalGameState()
        particle = Particle(x=10.0, y=20.0, lifetime=0.5)
        local_state.add_particle(particle)
        
        local_state.update(1.0)  # Lifetime expired
        
        assert len(local_state.particles) == 0
    
    def test_particle_lifetime_decreases(self):
        """Test particle lifetime decreases with update."""
        local_state = LocalGameState()
        particle = Particle(x=10.0, y=20.0, lifetime=2.0)
        local_state.add_particle(particle)
        
        local_state.update(0.3)
        
        assert pytest.approx(particle.lifetime, abs=0.01) == 1.7


class TestLocalGameStateAnimations:
    """Tests for LocalGameState animation management."""
    
    def test_add_animation(self):
        """Test adding an animation."""
        local_state = LocalGameState()
        animation = Animation(
            entity_id='enemy-1',
            animation_name='walk',
            total_frames=4,
            frame_duration=0.1,
        )
        
        local_state.add_animation(animation)
        
        assert 'enemy-1' in local_state.animations
        assert local_state.animations['enemy-1'] == animation
    
    def test_remove_animation(self):
        """Test removing an animation."""
        local_state = LocalGameState()
        animation = Animation(entity_id='enemy-1', animation_name='walk')
        local_state.add_animation(animation)
        
        result = local_state.remove_animation('enemy-1')
        
        assert result is True
        assert 'enemy-1' not in local_state.animations
    
    def test_remove_animation_not_exists(self):
        """Test removing non-existent animation returns False."""
        local_state = LocalGameState()
        
        result = local_state.remove_animation('non-existent')
        
        assert result is False
    
    def test_animation_frame_advances(self):
        """Test animation frames advance with time."""
        local_state = LocalGameState()
        animation = Animation(
            entity_id='enemy-1',
            animation_name='walk',
            total_frames=4,
            frame_duration=0.1,
        )
        local_state.add_animation(animation)
        
        local_state.update(0.15)  # Should advance past first frame
        
        assert animation.current_frame == 1
    
    def test_animation_loops(self):
        """Test looping animation wraps around."""
        local_state = LocalGameState()
        animation = Animation(
            entity_id='enemy-1',
            animation_name='walk',
            total_frames=3,
            frame_duration=0.1,
            looping=True,
        )
        local_state.add_animation(animation)
        
        local_state.update(0.35)  # Should go through all frames and loop back
        
        assert animation.current_frame == 0  # Wrapped back to start
    
    def test_non_looping_animation_stops(self):
        """Test non-looping animation stops at last frame and is removed."""
        local_state = LocalGameState()
        animation = Animation(
            entity_id='enemy-1',
            animation_name='death',
            total_frames=3,
            frame_duration=0.1,
            looping=False,
        )
        local_state.add_animation(animation)
        
        local_state.update(0.5)  # Enough time to finish animation
        
        # Animation should be removed after completing
        assert 'enemy-1' not in local_state.animations


class TestLocalGameStateInterpolation:
    """Tests for LocalGameState position interpolation."""
    
    def test_set_entity_position_new_entity(self):
        """Test setting position for new entity."""
        local_state = LocalGameState()
        
        local_state.set_entity_position('entity-1', 100.0, 200.0)
        
        pos = local_state.get_entity_position('entity-1')
        assert pos is not None
        assert pos == (100.0, 200.0)
    
    def test_set_entity_position_updates_target(self):
        """Test setting position updates target for existing entity."""
        local_state = LocalGameState()
        local_state.set_entity_position('entity-1', 0.0, 0.0)
        
        local_state.set_entity_position('entity-1', 100.0, 100.0)
        
        pos_data = local_state.interpolated_entity_positions['entity-1']
        assert pos_data.target_x == 100.0
        assert pos_data.target_y == 100.0
        # Current position should still be at origin (not yet interpolated)
        assert pos_data.current_x == 0.0
        assert pos_data.current_y == 0.0
    
    def test_get_entity_position_not_exists(self):
        """Test getting position for non-existent entity returns None."""
        local_state = LocalGameState()
        
        pos = local_state.get_entity_position('non-existent')
        
        assert pos is None
    
    def test_remove_entity_position(self):
        """Test removing entity position."""
        local_state = LocalGameState()
        local_state.set_entity_position('entity-1', 100.0, 200.0)
        
        result = local_state.remove_entity_position('entity-1')
        
        assert result is True
        assert local_state.get_entity_position('entity-1') is None
    
    def test_interpolation_moves_towards_target(self):
        """Test position interpolates towards target over time."""
        local_state = LocalGameState()
        # Use a slower interpolation speed so we can observe partial interpolation
        local_state.set_entity_position('entity-1', 0.0, 0.0, interpolation_speed=2.0)
        local_state.set_entity_position('entity-1', 100.0, 100.0, interpolation_speed=2.0)  # Update target
        
        # Run update
        local_state.update(0.1)  # 0.1 second, t = 2.0 * 0.1 = 0.2
        
        pos = local_state.get_entity_position('entity-1')
        assert pos is not None
        # Position should have moved towards target (about 20% of the way)
        assert pos[0] > 0.0
        assert pos[1] > 0.0
        assert pos[0] < 100.0
        assert pos[1] < 100.0
    
    def test_interpolation_reaches_target(self):
        """Test position eventually reaches target."""
        local_state = LocalGameState()
        local_state.set_entity_position('entity-1', 0.0, 0.0, interpolation_speed=10.0)
        local_state.set_entity_position('entity-1', 100.0, 100.0)
        
        # Run several updates
        for _ in range(20):
            local_state.update(0.1)
        
        pos = local_state.get_entity_position('entity-1')
        assert pos is not None
        # Should be very close to target
        assert pytest.approx(pos[0], abs=0.1) == 100.0
        assert pytest.approx(pos[1], abs=0.1) == 100.0


class TestLocalGameStateSyncWithServer:
    """Tests for LocalGameState sync_with_server functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        GameState.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_sync_with_dict(self):
        """Test syncing from serialized dictionary."""
        local_state = LocalGameState()
        
        server_data = {
            'entities': {
                'enemies': [
                    {'id': 'enemy-1', 'position': {'x': 10.0, 'y': 20.0}},
                    {'id': 'enemy-2', 'position': {'x': 30.0, 'y': 40.0}},
                ]
            }
        }
        
        local_state.sync_with_server(server_data)
        
        pos1 = local_state.get_entity_position('enemy-1')
        pos2 = local_state.get_entity_position('enemy-2')
        
        assert pos1 == (10.0, 20.0)
        assert pos2 == (30.0, 40.0)
    
    def test_sync_removes_stale_entities(self):
        """Test syncing removes entities not in server state."""
        local_state = LocalGameState()
        local_state.set_entity_position('old-enemy', 100.0, 100.0)
        
        server_data = {
            'entities': {
                'enemies': [
                    {'id': 'new-enemy', 'position': {'x': 10.0, 'y': 20.0}},
                ]
            }
        }
        
        local_state.sync_with_server(server_data)
        
        assert local_state.get_entity_position('old-enemy') is None
        assert local_state.get_entity_position('new-enemy') == (10.0, 20.0)
    
    def test_sync_with_game_state_object(self):
        """Test syncing from GameState object."""
        local_state = LocalGameState()
        game_state = GameState()
        
        # Create mock entities
        class MockEntity:
            def __init__(self, entity_id, x, y):
                self.id = entity_id
                self.position = type('Position', (), {'x': x, 'y': y})()
        
        entity = MockEntity('tower-1', 50.0, 60.0)
        game_state.add_entity('towers', entity)
        
        local_state.sync_with_server(game_state)
        
        pos = local_state.get_entity_position('tower-1')
        assert pos == (50.0, 60.0)
    
    def test_sync_updates_existing_positions(self):
        """Test syncing updates positions for existing entities."""
        local_state = LocalGameState()
        local_state.set_entity_position('entity-1', 0.0, 0.0)
        
        server_data = {
            'entities': {
                'enemies': [
                    {'id': 'entity-1', 'position': {'x': 100.0, 'y': 200.0}},
                ]
            }
        }
        
        local_state.sync_with_server(server_data)
        
        # Target should be updated
        pos_data = local_state.interpolated_entity_positions['entity-1']
        assert pos_data.target_x == 100.0
        assert pos_data.target_y == 200.0
    
    def test_sync_removes_stale_animations(self):
        """Test syncing removes animations for entities not in server state."""
        local_state = LocalGameState()
        animation = Animation(entity_id='old-enemy', animation_name='walk')
        local_state.add_animation(animation)
        
        server_data = {
            'entities': {
                'enemies': [
                    {'id': 'new-enemy', 'position': {'x': 10.0, 'y': 20.0}},
                ]
            }
        }
        
        local_state.sync_with_server(server_data)
        
        assert 'old-enemy' not in local_state.animations


class TestLocalGameStateClear:
    """Tests for LocalGameState clear functionality."""
    
    def test_clear_removes_all_state(self):
        """Test clear removes all particles, animations, and positions."""
        local_state = LocalGameState()
        
        # Add some state
        local_state.add_particle(Particle(x=1.0, y=2.0))
        local_state.add_animation(Animation(entity_id='e1', animation_name='walk'))
        local_state.set_entity_position('e1', 10.0, 20.0)
        
        local_state.clear()
        
        assert local_state.particles == []
        assert local_state.animations == {}
        assert local_state.interpolated_entity_positions == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
