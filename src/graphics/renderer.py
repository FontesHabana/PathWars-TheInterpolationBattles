"""
Renderer module for PathWars - The Interpolation Battles.

Handles isometric projection and drawing of the game state to the screen.
"""

import math
import pygame
from typing import Tuple, List

from core.grid import Grid
from core.game_state import GameState, GamePhase
from entities.base import EntityType
from entities.tower import TowerType
from entities.enemy import EnemyType
from graphics.assets import AssetManager

class Renderer:
    """
    Handles all rendering operations.
    """

    def __init__(self, screen: pygame.Surface, grid: Grid):
        self.screen = screen
        self.grid = grid
        
        # Isometric transformation parameters
        # Center the grid on the screen
        self.offset_x = screen.get_width() // 2
        self.offset_y = 100 # Top margin
        
        # Scale factor for isometric tiles
        self.tile_width = grid.cell_size
        self.tile_height = grid.cell_size // 2

    def cart_to_iso(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert Cartesian coordinates (grid cells) to Isometric screen coordinates.
        
        Args:
            x, y: Cartesian coordinates (can be float for smooth movement)
            
        Returns:
            (screen_x, screen_y) tuple
        """
        iso_x = (x - y) * self.tile_width // 2 + self.offset_x
        iso_y = (x + y) * self.tile_height // 2 + self.offset_y
        return int(iso_x), int(iso_y)

    def iso_to_cart(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """
        Convert Isometric screen coordinates to Cartesian grid coordinates.
        
        Used for picking (mouse clicks).
        """
        # Inverse of cart_to_iso
        # iso_x = (x - y) * W/2 + OX
        # iso_y = (x + y) * H/2 + OY
        
        adj_x = screen_x - self.offset_x
        adj_y = screen_y - self.offset_y
        
        # Solve for x and y
        # y = (adj_y / (H/2) - adj_x / (W/2)) / 2
        # x = adj_y / (H/2) - y
        
        y = (adj_y / (self.tile_height / 2) - adj_x / (self.tile_width / 2)) / 2
        x = (adj_y / (self.tile_height / 2) + adj_x / (self.tile_width / 2)) / 2
        
        return int(x), int(y)

    def draw_grid(self):
        """Draw the isometric grid floor."""
        color = AssetManager.get_color("grid_line")
        
        # Draw horizontal lines (along x axis)
        for y in range(self.grid.height + 1):
            start = self.cart_to_iso(0, y)
            end = self.cart_to_iso(self.grid.width, y)
            pygame.draw.line(self.screen, color, start, end, 1)

        # Draw vertical lines (along y axis)
        for x in range(self.grid.width + 1):
            start = self.cart_to_iso(x, 0)
            end = self.cart_to_iso(x, self.grid.height)
            pygame.draw.line(self.screen, color, start, end, 1)

    def draw_entities(self, game_state: GameState):
        """Draw all entities in the game state."""
        entities = game_state.entities_collection
        
        # Sort entities by Y position (painter's algorithm) roughly
        # For true isometric depth sorting, we need (x + y)
        all_entities = []
        for t in entities.get('towers', []):
            all_entities.append(t)
        for e in entities.get('enemies', []):
            all_entities.append(e)
            
        all_entities.sort(key=lambda e: e.position.x + e.position.y)
        
        for entity in all_entities:
            screen_pos = self.cart_to_iso(entity.position.x, entity.position.y)
            
            if entity.entity_type == EntityType.TOWER:
                self._draw_tower(entity, screen_pos)
            elif entity.entity_type == EntityType.ENEMY:
                self._draw_enemy(entity, screen_pos)

    def _draw_tower(self, tower, pos: Tuple[int, int]):
        """Helper to draw a tower."""
        color_key = "tower_dean" # Default
        if tower.tower_type == TowerType.CALCULUS: color_key = "tower_calculus"
        elif tower.tower_type == TowerType.PHYSICS: color_key = "tower_physics"
        elif tower.tower_type == TowerType.STATISTICS: color_key = "tower_statistics"
        
        color = AssetManager.get_color(color_key)
        
        # Draw a simple circle or polygon for now
        # Offset slightly up so it stands ON the tile
        draw_pos = (pos[0], pos[1] - 20)
        pygame.draw.circle(self.screen, color, draw_pos, 15)
        
        # Base
        pygame.draw.circle(self.screen, (100, 100, 100), pos, 10, 1)

    def _draw_enemy(self, enemy, pos: Tuple[int, int]):
        """Helper to draw an enemy."""
        color_key = "enemy_student"
        if enemy.enemy_type == EnemyType.VARIABLE_X: color_key = "enemy_variable_x"
        
        color = AssetManager.get_color(color_key)
        
        # Draw small circle
        draw_pos = (pos[0], pos[1] - 15)
        pygame.draw.circle(self.screen, color, draw_pos, 8)
        
        # Health bar
        hp_pct = enemy.health / enemy.max_health
        bar_width = 20
        bar_height = 4
        bar_pos = (pos[0] - bar_width // 2, pos[1] - 30)
        
        pygame.draw.rect(self.screen, (255, 0, 0), (*bar_pos, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (*bar_pos, int(bar_width * hp_pct), bar_height))

    def draw_hud(self, game_state: GameState):
        """Draw the Heads Up Display."""
        font = AssetManager.get_font(24)
        text_color = AssetManager.get_color("text")
        
        # Money
        money_surf = font.render(f"Funds: ${game_state.money}", True, text_color)
        self.screen.blit(money_surf, (20, 20))
        
        # Lives
        lives_surf = font.render(f"Lives: {game_state.lives}", True, text_color)
        self.screen.blit(lives_surf, (20, 50))
        
        # Phase
        phase_surf = font.render(f"Phase: {game_state.current_phase.name}", True, text_color)
        self.screen.blit(phase_surf, (20, 80))

    def render(self, game_state: GameState):
        """Main render call."""
        self.screen.fill(AssetManager.get_color("background"))
        
        self.draw_grid()
        self.draw_entities(game_state)
        self.draw_hud(game_state)
        
        pygame.display.flip()
