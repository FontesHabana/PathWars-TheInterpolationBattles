"""
Autotiling System for PathWars - The Interpolation Battles.

This module provides automatic tile selection for rendering paths
based on the direction of connections.
"""

import pygame
from enum import Enum, auto
from typing import List, Set, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.renderer import Renderer


class PathDirection(Enum):
    """Directions of path connections."""
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()


class PathTileType(Enum):
    """Types of path tiles."""
    EMPTY = auto()
    STRAIGHT_H = auto()  # Horizontal
    STRAIGHT_V = auto()  # Vertical
    CURVE_NE = auto()    # North-East
    CURVE_NW = auto()    # North-West
    CURVE_SE = auto()    # South-East
    CURVE_SW = auto()    # South-West
    T_NORTH = auto()     # T hacia norte
    T_SOUTH = auto()     # T hacia sur
    T_EAST = auto()      # T hacia este
    T_WEST = auto()      # T hacia oeste
    CROSS = auto()       # Intersección


class PathTileSelector:
    """
    Selects the correct tile based on neighbor connections.
    """
    
    def __init__(self):
        """Initialize PathTileSelector."""
        pass
    
    def select_tile_type(self, connections: Set[PathDirection]) -> PathTileType:
        """
        Given a set of connected directions, return the appropriate tile type.
        
        Args:
            connections: Set of PathDirection values indicating connected neighbors.
            
        Returns:
            The appropriate PathTileType for the given connections.
        """
        conn_count = len(connections)
        
        if conn_count == 0:
            return PathTileType.EMPTY
        
        # Single connection - use straight tile pointing in that direction
        if conn_count == 1:
            direction = list(connections)[0]
            if direction in (PathDirection.NORTH, PathDirection.SOUTH):
                return PathTileType.STRAIGHT_V
            else:
                return PathTileType.STRAIGHT_H
        
        # Two connections
        if conn_count == 2:
            # Straight lines
            if PathDirection.NORTH in connections and PathDirection.SOUTH in connections:
                return PathTileType.STRAIGHT_V
            if PathDirection.EAST in connections and PathDirection.WEST in connections:
                return PathTileType.STRAIGHT_H
            
            # Curves
            if PathDirection.NORTH in connections and PathDirection.EAST in connections:
                return PathTileType.CURVE_NE
            if PathDirection.NORTH in connections and PathDirection.WEST in connections:
                return PathTileType.CURVE_NW
            if PathDirection.SOUTH in connections and PathDirection.EAST in connections:
                return PathTileType.CURVE_SE
            if PathDirection.SOUTH in connections and PathDirection.WEST in connections:
                return PathTileType.CURVE_SW
        
        # Three connections - T junctions
        if conn_count == 3:
            if PathDirection.NORTH not in connections:
                return PathTileType.T_SOUTH
            if PathDirection.SOUTH not in connections:
                return PathTileType.T_NORTH
            if PathDirection.EAST not in connections:
                return PathTileType.T_WEST
            if PathDirection.WEST not in connections:
                return PathTileType.T_EAST
        
        # Four connections - cross intersection
        if conn_count == 4:
            return PathTileType.CROSS
        
        # Fallback
        return PathTileType.EMPTY
    
    def get_tile_sprite(self, tile_type: PathTileType) -> Optional[pygame.Surface]:
        """
        Get the sprite for the given tile type.
        
        Args:
            tile_type: The type of tile to get.
            
        Returns:
            The sprite surface, or None if not found.
        """
        from graphics.assets import AssetManager
        
        # Map tile types to sprite names
        tile_map = {
            PathTileType.STRAIGHT_H: "path_h",
            PathTileType.STRAIGHT_V: "path_v",
            PathTileType.CURVE_NE: "path_ne",
            PathTileType.CURVE_NW: "path_nw",
            PathTileType.CURVE_SE: "path_se",
            PathTileType.CURVE_SW: "path_sw",
            # For T and CROSS, we'll use appropriate combinations or fallback
            PathTileType.T_NORTH: "path_h",  # Fallback
            PathTileType.T_SOUTH: "path_h",  # Fallback
            PathTileType.T_EAST: "path_v",   # Fallback
            PathTileType.T_WEST: "path_v",   # Fallback
            PathTileType.CROSS: "path_h",    # Fallback
        }
        
        sprite_name = tile_map.get(tile_type)
        if sprite_name:
            return AssetManager.get_sprite(sprite_name)
        return None


class PathRenderer:
    """
    Renders paths with autotiling.
    """
    
    def __init__(self, renderer: "Renderer"):
        """
        Initialize PathRenderer.
        
        Args:
            renderer: The main Renderer instance for coordinate conversion.
        """
        self._renderer = renderer
        self._tile_selector = PathTileSelector()
    
    def render_path(
        self,
        screen: pygame.Surface,
        path_points: List[Tuple[float, float]],
        resolution: int = 1
    ) -> None:
        """
        Render the path with autotiling.
        
        Analyzes path direction at each point and selects appropriate tiles.
        
        Args:
            screen: The pygame surface to draw on.
            path_points: List of (x, y) grid coordinates defining the path.
            resolution: Sample every Nth point (1 = every point).
        """
        if len(path_points) < 2:
            return
        
        # Sample points based on resolution
        sampled_points = path_points[::resolution]
        
        for i, point in enumerate(sampled_points):
            prev_point = sampled_points[i - 1] if i > 0 else None
            next_point = sampled_points[i + 1] if i < len(sampled_points) - 1 else None
            
            # Calculate connections
            connections = self._calculate_connections(prev_point, point, next_point)
            
            # Select tile type
            tile_type = self._tile_selector.select_tile_type(connections)
            
            # Get sprite
            sprite = self._tile_selector.get_tile_sprite(tile_type)
            
            if sprite:
                # Convert to isometric screen coordinates
                iso_pos = self._renderer.cart_to_iso(point[0], point[1])
                
                # Center the sprite on the tile
                sprite_rect = sprite.get_rect()
                sprite_rect.center = iso_pos
                
                screen.blit(sprite, sprite_rect)
    
    def _calculate_connections(
        self,
        prev_point: Optional[Tuple[float, float]],
        current_point: Tuple[float, float],
        next_point: Optional[Tuple[float, float]]
    ) -> Set[PathDirection]:
        """
        Calculate the directions of connections for a point on the path.
        
        Args:
            prev_point: Previous point in the path (or None).
            current_point: Current point to analyze.
            next_point: Next point in the path (or None).
            
        Returns:
            Set of PathDirection values indicating connected directions.
        """
        connections = set()
        
        cx, cy = current_point
        
        # Check connection to previous point
        if prev_point is not None:
            px, py = prev_point
            dx = cx - px
            dy = cy - py
            
            # Determine direction (using simple threshold)
            if abs(dy) > abs(dx):
                if dy > 0:
                    connections.add(PathDirection.NORTH)
                else:
                    connections.add(PathDirection.SOUTH)
            else:
                if dx > 0:
                    connections.add(PathDirection.WEST)
                else:
                    connections.add(PathDirection.EAST)
        
        # Check connection to next point
        if next_point is not None:
            nx, ny = next_point
            dx = nx - cx
            dy = ny - cy
            
            # Determine direction
            if abs(dy) > abs(dx):
                if dy > 0:
                    connections.add(PathDirection.SOUTH)
                else:
                    connections.add(PathDirection.NORTH)
            else:
                if dx > 0:
                    connections.add(PathDirection.EAST)
                else:
                    connections.add(PathDirection.WEST)
        
        return connections
