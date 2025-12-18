"""
Local Game State module for managing client-side visual state.

This module provides LocalGameState which handles visual-only data
separate from the authoritative server game state. It manages particles,
animations, and interpolated entity positions for smooth rendering.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Particle:
    """
    Represents a visual particle effect.
    
    Attributes:
        x: X position of the particle.
        y: Y position of the particle.
        vx: X velocity of the particle.
        vy: Y velocity of the particle.
        lifetime: Remaining lifetime in seconds.
        max_lifetime: Maximum lifetime in seconds (used for calculating alpha/fade).
        color: RGB color tuple.
        size: Size of the particle.
    """
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    lifetime: float = 1.0
    max_lifetime: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    size: float = 2.0
    
    @property
    def alpha(self) -> float:
        """
        Calculate alpha value based on remaining lifetime.
        
        Returns:
            Alpha value between 0.0 and 1.0 based on remaining lifetime.
        """
        if self.max_lifetime <= 0:
            return 1.0
        return max(0.0, min(1.0, self.lifetime / self.max_lifetime))


@dataclass
class Animation:
    """
    Represents an animation state.
    
    Attributes:
        entity_id: ID of the entity this animation belongs to.
        animation_name: Name of the animation.
        current_frame: Current frame index.
        frame_time: Time spent on current frame.
        frame_duration: Duration of each frame in seconds.
        total_frames: Total number of frames in the animation.
        looping: Whether the animation loops.
    """
    entity_id: str
    animation_name: str
    current_frame: int = 0
    frame_time: float = 0.0
    frame_duration: float = 0.1
    total_frames: int = 1
    looping: bool = True


@dataclass
class InterpolatedPosition:
    """
    Represents an interpolated entity position for smooth rendering.
    
    Attributes:
        entity_id: ID of the entity.
        current_x: Current interpolated X position.
        current_y: Current interpolated Y position.
        target_x: Target X position from server.
        target_y: Target Y position from server.
        interpolation_speed: Speed of interpolation (0-1 per second).
    """
    entity_id: str
    current_x: float
    current_y: float
    target_x: float
    target_y: float
    interpolation_speed: float = 10.0


class LocalGameState:
    """
    Client-side game state for visual presentation.
    
    This class manages visual-only data including particles, animations,
    and interpolated entity positions. It works alongside the authoritative
    GameState to provide smooth client-side rendering.
    
    Unlike GameState which uses the Singleton pattern for authoritative
    game logic, LocalGameState can be instantiated per client view.
    
    Attributes:
        particles: List of active particle effects.
        animations: Dictionary of active animations by entity ID.
        interpolated_entity_positions: Dictionary of interpolated positions by entity ID.
    """
    
    def __init__(self) -> None:
        """Initialize the local game state."""
        self._particles: List[Particle] = []
        self._animations: Dict[str, Animation] = {}
        self._interpolated_positions: Dict[str, InterpolatedPosition] = {}
    
    @property
    def particles(self) -> List[Particle]:
        """Return the list of active particles."""
        return self._particles
    
    @property
    def animations(self) -> Dict[str, Animation]:
        """Return the dictionary of active animations."""
        return self._animations
    
    @property
    def interpolated_entity_positions(self) -> Dict[str, InterpolatedPosition]:
        """Return the dictionary of interpolated entity positions."""
        return self._interpolated_positions
    
    def add_particle(self, particle: Particle) -> None:
        """
        Add a particle effect.
        
        Args:
            particle: The particle to add.
        """
        self._particles.append(particle)
    
    def add_animation(self, animation: Animation) -> None:
        """
        Add or update an animation for an entity.
        
        Args:
            animation: The animation to add.
        """
        self._animations[animation.entity_id] = animation
    
    def remove_animation(self, entity_id: str) -> bool:
        """
        Remove an animation for an entity.
        
        Args:
            entity_id: The ID of the entity whose animation to remove.
            
        Returns:
            True if an animation was removed, False otherwise.
        """
        if entity_id in self._animations:
            del self._animations[entity_id]
            return True
        return False
    
    def set_entity_position(
        self, 
        entity_id: str, 
        x: float, 
        y: float,
        interpolation_speed: float = 10.0
    ) -> None:
        """
        Set the target position for an entity.
        
        If the entity doesn't have an interpolated position yet,
        it will be created at the target position (no interpolation).
        
        Args:
            entity_id: The ID of the entity.
            x: Target X position.
            y: Target Y position.
            interpolation_speed: Speed of interpolation.
        """
        if entity_id in self._interpolated_positions:
            # Update target position for existing entity
            pos = self._interpolated_positions[entity_id]
            pos.target_x = x
            pos.target_y = y
            pos.interpolation_speed = interpolation_speed
        else:
            # Create new interpolated position at target (no initial interpolation)
            self._interpolated_positions[entity_id] = InterpolatedPosition(
                entity_id=entity_id,
                current_x=x,
                current_y=y,
                target_x=x,
                target_y=y,
                interpolation_speed=interpolation_speed,
            )
    
    def get_entity_position(self, entity_id: str) -> Optional[Tuple[float, float]]:
        """
        Get the current interpolated position for an entity.
        
        Args:
            entity_id: The ID of the entity.
            
        Returns:
            Tuple of (x, y) if entity exists, None otherwise.
        """
        if entity_id in self._interpolated_positions:
            pos = self._interpolated_positions[entity_id]
            return (pos.current_x, pos.current_y)
        return None
    
    def remove_entity_position(self, entity_id: str) -> bool:
        """
        Remove an entity's interpolated position.
        
        Args:
            entity_id: The ID of the entity.
            
        Returns:
            True if position was removed, False otherwise.
        """
        if entity_id in self._interpolated_positions:
            del self._interpolated_positions[entity_id]
            return True
        return False
    
    def update(self, dt: float) -> None:
        """
        Update local visual state.
        
        Handles particle physics, animation frame advancement,
        and position interpolation.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        self._update_particles(dt)
        self._update_animations(dt)
        self._update_interpolated_positions(dt)
    
    def _update_particles(self, dt: float) -> None:
        """
        Update particle physics and remove dead particles.
        
        Args:
            dt: Delta time in seconds.
        """
        alive_particles: List[Particle] = []
        
        for particle in self._particles:
            # Update lifetime
            particle.lifetime -= dt
            
            if particle.lifetime > 0:
                # Update position based on velocity
                particle.x += particle.vx * dt
                particle.y += particle.vy * dt
                alive_particles.append(particle)
        
        self._particles = alive_particles
    
    def _update_animations(self, dt: float) -> None:
        """
        Update animation frames.
        
        Args:
            dt: Delta time in seconds.
        """
        finished_animations: List[str] = []
        
        for entity_id, animation in self._animations.items():
            animation.frame_time += dt
            
            # Check if we need to advance to next frame
            while animation.frame_time >= animation.frame_duration:
                animation.frame_time -= animation.frame_duration
                animation.current_frame += 1
                
                # Handle frame wrapping
                if animation.current_frame >= animation.total_frames:
                    if animation.looping:
                        animation.current_frame = 0
                    else:
                        animation.current_frame = animation.total_frames - 1
                        finished_animations.append(entity_id)
                        break
        
        # Remove non-looping finished animations
        for entity_id in finished_animations:
            del self._animations[entity_id]
    
    def _update_interpolated_positions(self, dt: float) -> None:
        """
        Update interpolated entity positions using linear interpolation.
        
        Uses basic linear interpolation (lerp) to smoothly move
        entities from current position towards target position.
        
        Args:
            dt: Delta time in seconds.
        """
        for pos in self._interpolated_positions.values():
            # Calculate interpolation factor
            # interpolation_speed is units of "full interpolation" per second
            t = min(1.0, pos.interpolation_speed * dt)
            
            # Linear interpolation: current = current + t * (target - current)
            pos.current_x = pos.current_x + t * (pos.target_x - pos.current_x)
            pos.current_y = pos.current_y + t * (pos.target_y - pos.current_y)
    
    def sync_with_server(self, server_state: Any) -> None:
        """
        Reconcile local state with authoritative server state.
        
        Updates entity target positions from server state while
        maintaining smooth interpolation. Removes entities that
        no longer exist in server state.
        
        Args:
            server_state: The authoritative GameState from the server.
                         Expected to have an entities_collection property
                         or be a dict from GameState.to_dict().
        """
        # Handle both GameState object and serialized dict
        if isinstance(server_state, dict):
            entities_data = server_state.get('entities', {})
            self._sync_from_dict(entities_data)
        else:
            # Assume it's a GameState object
            if hasattr(server_state, 'entities_collection'):
                self._sync_from_game_state(server_state)
    
    def _sync_from_dict(self, entities_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Sync from serialized entities dictionary.
        
        Args:
            entities_data: Dictionary of entity type to list of entity data.
        """
        server_entity_ids: set = set()
        
        for entity_type, entities in entities_data.items():
            for entity_data in entities:
                entity_id = entity_data.get('id')
                position = entity_data.get('position')
                
                if entity_id and position:
                    server_entity_ids.add(entity_id)
                    x = position.get('x', 0.0)
                    y = position.get('y', 0.0)
                    self.set_entity_position(entity_id, x, y)
        
        # Remove entities that are no longer on the server
        self._remove_stale_entities(server_entity_ids)
    
    def _sync_from_game_state(self, server_state: Any) -> None:
        """
        Sync from GameState object.
        
        Args:
            server_state: GameState object with entities_collection.
        """
        server_entity_ids: set = set()
        entities_collection = server_state.entities_collection
        
        for entity_type, entities in entities_collection.items():
            for entity in entities:
                if hasattr(entity, 'id') and hasattr(entity, 'position'):
                    entity_id = entity.id
                    server_entity_ids.add(entity_id)
                    
                    pos = entity.position
                    if hasattr(pos, 'x') and hasattr(pos, 'y'):
                        self.set_entity_position(entity_id, pos.x, pos.y)
        
        # Remove entities that are no longer on the server
        self._remove_stale_entities(server_entity_ids)
    
    def _remove_stale_entities(self, server_entity_ids: set) -> None:
        """
        Remove entities that are no longer present in server state.
        
        Args:
            server_entity_ids: Set of entity IDs that exist on the server.
        """
        # Find and remove stale interpolated positions
        stale_positions = [
            entity_id for entity_id in self._interpolated_positions
            if entity_id not in server_entity_ids
        ]
        for entity_id in stale_positions:
            del self._interpolated_positions[entity_id]
        
        # Find and remove stale animations
        stale_animations = [
            entity_id for entity_id in self._animations
            if entity_id not in server_entity_ids
        ]
        for entity_id in stale_animations:
            del self._animations[entity_id]
    
    def clear(self) -> None:
        """
        Clear all local state.
        
        Removes all particles, animations, and interpolated positions.
        """
        self._particles.clear()
        self._animations.clear()
        self._interpolated_positions.clear()
