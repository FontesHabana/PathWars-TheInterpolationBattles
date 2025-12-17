"""
Main Entry Point for PathWars - The Interpolation Battles.

Initializes Pygame, GameState, Network, and runs the main loop.
"""

import sys
import pygame
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from core.game_state import GameState, GamePhase
from core.grid import Grid
from core.input_handler import InputHandler
from core.combat_manager import CombatManager
from core.wave_manager import WaveManager
from graphics.renderer import Renderer
from graphics.assets import AssetManager
from entities.factory import EntityFactory
from entities.enemy import EnemyType, Enemy
from ui.manager import UIManager


def main() -> None:
    logger.info("Starting PathWars...")
    
    # 1. Initialize Pygame
    pygame.init()
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PathWars: The Interpolation Duel")
    clock = pygame.time.Clock()

    # 2. Initialize Core Systems
    game_state = GameState() # Singleton
    grid = Grid(width=20, height=20, cell_size=32)
    renderer = Renderer(screen, grid)
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT, game_state)
    input_handler = InputHandler(game_state, grid, renderer)
    
    # Initialize Wave Manager
    wave_manager = WaveManager()
    current_wave_number = 0  # Track which wave we're on (0 = not started)
    
    # Default enemy path in GRID COORDINATES (0-19 range, matching grid size)
    # Enemies will be rendered in isometric projection by Renderer.cart_to_iso()
    default_path = [
        (0.0, 10.0),     # Start from left edge, middle row
        (5.0, 10.0),     # Move right
        (5.0, 5.0),      # Turn up
        (10.0, 5.0),     # Move right
        (10.0, 15.0),    # Turn down
        (15.0, 15.0),    # Move right
        (15.0, 10.0),    # Turn up
        (19.0, 10.0),    # End at right edge
    ]

    
    # Wave event callbacks
    def on_wave_start(wave_num: int) -> None:
        logger.info(f"Wave {wave_num} started!")
    
    def on_wave_complete(wave_num: int) -> None:
        logger.info(f"Wave {wave_num} complete!")
    
    wave_manager.subscribe_wave_start(on_wave_start)
    wave_manager.subscribe_wave_complete(on_wave_complete)
    
    # Link UI Manager to Input Handler for tower selection sync
    input_handler.ui_manager = ui_manager

    # Initialize Combat Manager
    combat_manager = CombatManager()
    game_over = False

    # Combat event handlers
    def on_enemy_killed(enemy: Enemy, reward: int) -> None:
        """Handle enemy death: add money reward."""
        game_state.add_money(reward)
        logger.info(f"Enemy killed! Reward: ${reward}")

    def on_base_damaged(enemy: Enemy) -> None:
        """Handle base damage: deduct life and check game over."""
        nonlocal game_over
        lives_remain = game_state.lose_life()
        logger.info(f"Base damaged! Lives remaining: {game_state.lives}")
        if not lives_remain:
            game_over = True
            logger.info("GAME OVER!")

    combat_manager.on_enemy_killed(on_enemy_killed)
    combat_manager.on_base_damaged(on_base_damaged)

    # 3. Main Loop
    running = True
    while running and not game_over:
        dt = clock.tick(60) / 1000.0 # Delta time in seconds
        
        # Input - UI gets priority
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            # UI handles event first
            if ui_manager.handle_event(event):
                continue  # Event consumed by UI
                
            # Game world handles event
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                input_handler._handle_left_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                input_handler._handle_keydown(event.key)
            
        # Sync tower selection from UI to input handler
        input_handler.selected_tower_type = ui_manager.selected_tower_type
            
        # Update
        entities = game_state.entities_collection
        
        # Update Enemies
        for enemy in entities.get('enemies', []):
            enemy.update(dt)

        # Update Combat (handles tower attacks, enemy deaths, base damage)
        combat_manager.update(dt, game_state)
        # Update Towers (Always update cooldowns)
        for tower in entities.get('towers', []):
            tower.update(dt)
        
        # Update Wave Manager during BATTLE phase
        if game_state.current_phase == GamePhase.BATTLE:
            # Start wave if not active
            if not wave_manager.is_active:
                current_wave_number += 1
                if current_wave_number <= wave_manager.total_waves:
                    wave_manager.start_wave(current_wave_number, default_path)
            
            # Update wave manager and spawn enemies
            new_enemies = wave_manager.update(dt)
            for enemy in new_enemies:
                game_state.add_entity('enemies', enemy)
            
            # Update all enemies
            for enemy in game_state.entities_collection.get('enemies', []):
                enemy.update(dt)
            
            # Check for wave completion
            if wave_manager.is_wave_complete():
                # Check if there are more waves
                if not wave_manager.has_more_waves():
                    # All waves complete - transition to RESULT phase
                    game_state.change_phase(GamePhase.RESULT)
            
        # Draw
        renderer.render(game_state, combat_manager)
        ui_manager.draw(screen)
        pygame.display.flip()
        
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
