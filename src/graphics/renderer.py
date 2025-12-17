"""
Renderer module for PathWars - The Interpolation Battles.

Handles isometric projection and drawing of the game state to the screen.
"""

import math
import pygame
from typing import List, Optional, Tuple, TYPE_CHECKING

from core.grid import Grid
from core.game_state import GameState, GamePhase
from entities.base import EntityType
from entities.tower import Tower, TowerType
from entities.enemy import Enemy, EnemyType
from graphics.assets import AssetManager

if TYPE_CHECKING:
    from core.combat_manager import CombatManager


class Renderer:
    """
    Handles all rendering operations for the game.

    Provides isometric projection and drawing of:
    - Grid tiles
    - Game entities (towers and enemies)
    - HUD (money, lives, phase)
    - Attack visualizations (lines from tower to target on attack)

    Attributes:
        screen: The pygame surface to render to.
        grid: The game grid for coordinate conversion.
        offset_x: X offset for centering the grid.
        offset_y: Y offset (top margin).
        tile_width: Width of isometric tiles.
        tile_height: Height of isometric tiles.
    """

    # Sprite vertical offsets for drawing
    TOWER_OFFSET_Y = 20
    ENEMY_OFFSET_Y = 15
    ATTACK_FLASH_RADIUS = 6
    ATTACK_FLASH_WIDTH = 2

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
        draw_pos = (pos[0], pos[1] - self.TOWER_OFFSET_Y)
        pygame.draw.circle(self.screen, color, draw_pos, 15)
        
        # Base
        pygame.draw.circle(self.screen, (100, 100, 100), pos, 10, 1)

    def _draw_enemy(self, enemy, pos: Tuple[int, int]):
        """Helper to draw an enemy."""
        color_key = "enemy_student"
        if enemy.enemy_type == EnemyType.VARIABLE_X: color_key = "enemy_variable_x"
        
        color = AssetManager.get_color(color_key)
        
        # Draw small circle
        draw_pos = (pos[0], pos[1] - self.ENEMY_OFFSET_Y)
        pygame.draw.circle(self.screen, color, draw_pos, 8)
        
        # Health bar
        hp_pct = enemy.health / enemy.max_health
        bar_width = 20
        bar_height = 4
        bar_pos = (pos[0] - bar_width // 2, pos[1] - 30)
        
        pygame.draw.rect(self.screen, (255, 0, 0), (*bar_pos, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (*bar_pos, int(bar_width * hp_pct), bar_height))

    def draw_curve(
        self,
        path: List[Tuple[float, float]],
        color: Tuple[int, int, int] = (255, 100, 100),
        width: int = 2,
    ) -> None:
        """
        Draw the interpolated path in grid coordinates (converted to isometric).

        Renders the path on the screen by converting grid coordinates
        to isometric screen coordinates.

        Args:
            path: List of (x, y) tuples representing grid coordinates.
            color: RGB tuple for the line color. Default is light red.
            width: Line width in pixels. Default is 2.
        """
        if len(path) < 2:
            return

        # Convert all points to isometric screen coordinates
        screen_points = [self.cart_to_iso(p[0], p[1]) for p in path]

        # Draw connected line segments
        pygame.draw.lines(self.screen, color, False, screen_points, width)

    def draw_curve_screen(
        self,
        path: List[Tuple[float, float]],
        color: Tuple[int, int, int] = (255, 100, 100),
        width: int = 2,
    ) -> None:
        """
        Draw the interpolated path in screen coordinates (no conversion).

        Renders the path directly using screen pixel coordinates.

        Args:
            path: List of (x, y) tuples representing screen coordinates.
            color: RGB tuple for the line color. Default is light red.
            width: Line width in pixels. Default is 2.
        """
        if len(path) < 2:
            return

        # Use path coordinates directly as screen coordinates
        screen_points = [(int(p[0]), int(p[1])) for p in path]

        # Draw connected line segments
        pygame.draw.lines(self.screen, color, False, screen_points, width)

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

    def draw_attacks(self, active_attacks: List[Tuple[Tower, Enemy]]) -> None:
        """
        Draw attack visualizations (lines from tower to target).

        Args:
            active_attacks: List of (tower, enemy) tuples representing active attacks.
        """
        attack_color = (255, 255, 0)  # Yellow for attack lines
        flash_color = (255, 200, 0)   # Orange for impact flash

        for tower, enemy in active_attacks:
            # Get screen positions for tower and enemy
            tower_pos = self.cart_to_iso(tower.position.x, tower.position.y)
            enemy_pos = self.cart_to_iso(enemy.position.x, enemy.position.y)

            # Offset positions to match where sprites are drawn
            tower_draw_pos = (tower_pos[0], tower_pos[1] - self.TOWER_OFFSET_Y)
            enemy_draw_pos = (enemy_pos[0], enemy_pos[1] - self.ENEMY_OFFSET_Y)

            # Draw attack line
            pygame.draw.line(self.screen, attack_color, tower_draw_pos, enemy_draw_pos, 2)

            # Draw a small flash/impact circle at enemy position
            pygame.draw.circle(
                self.screen,
                flash_color,
                enemy_draw_pos,
                self.ATTACK_FLASH_RADIUS,
                self.ATTACK_FLASH_WIDTH
            )

    def render(
        self,
        game_state: GameState,
        combat_manager: Optional["CombatManager"] = None
    ) -> None:
        """
        Main render call.

        Args:
            game_state: The current game state to render.
            combat_manager: Optional combat manager for attack visualization.
        """
        self.screen.fill(AssetManager.get_color("background"))
        
        self.draw_grid()
        self.draw_entities(game_state)

        # Draw attack visualizations if combat manager is provided
        if combat_manager is not None:
            self.draw_attacks(combat_manager.active_attacks)

        self.draw_hud(game_state)
        # NOTE: pygame.display.flip() is called by main.py after all UI is drawn

