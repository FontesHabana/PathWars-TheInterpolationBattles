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
from graphics.renderer import Renderer
from graphics.assets import AssetManager
from entities.factory import EntityFactory
from entities.enemy import EnemyType

def main():
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
    input_handler = InputHandler(game_state, grid, renderer)
    
    # Debug: Spawn a dummy text wave
    path = [(0,0), (5,5), (10,5), (15,10), (19,19)]
    enemies = EntityFactory.create_enemy_wave(EnemyType.STUDENT, path, count=0) # Start empty

    # 3. Main Loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0 # Delta time in seconds
        
        # Input
        if not input_handler.handle_input():
            running = False
            
        # Update
        # Update entities logic
        entities = game_state.entities_collection
        
        # Only update enemies during BATTLE phase or for testing
        if game_state.current_phase == GamePhase.BATTLE:
            # Simple wave spawner for debug
            # In real game, this is handled by a WaveManager
            pass 

        # Update Towers (Always update cooldowns)
        for tower in entities.get('towers', []):
            tower.update(dt)
            # Find targets and attack
            # target = tower.find_target(entities.get('enemies', []))
            # if target: tower.attack(target)
            
        # Draw
        renderer.render(game_state)
        
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
