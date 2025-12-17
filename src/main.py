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
from ui.manager import UIManager

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
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT, game_state)
    input_handler = InputHandler(game_state, grid, renderer)
    
    # Link UI Manager to Input Handler for tower selection sync
    input_handler.ui_manager = ui_manager

    # 3. Main Loop
    running = True
    while running:
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
        
        # Update Towers (Always update cooldowns)
        for tower in entities.get('towers', []):
            tower.update(dt)
            
        # Draw
        renderer.render(game_state)
        ui_manager.draw(screen)
        pygame.display.flip()
        
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
