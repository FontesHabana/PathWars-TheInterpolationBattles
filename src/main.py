"""
Main Entry Point for PathWars - The Interpolation Battles.

Initializes Pygame, GameState, Network, and runs the main loop.
"""

import sys
import pygame
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from core.game_state import GameState, GamePhase
from core.grid import Grid
from core.input_handler import InputHandler
from core.combat_manager import CombatManager
from core.wave_manager import WaveManager
from core.effects import EffectManager
from graphics.renderer import Renderer
from graphics.assets import AssetManager
from entities.factory import EntityFactory
from entities.enemy import EnemyType, Enemy
from ui.manager import UIManager
from ui.curve_editor import CurveEditorUI
from ui.wave_banner import WaveBanner
from ui.result_screen import ResultScreen
from core.curve_state import CurveState

# Constants
CURVE_COLOR = (255, 100, 100)


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
    game_state = GameState()
    grid = Grid(width=20, height=20, cell_size=32)
    renderer = Renderer(screen, grid)
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT, game_state)
    input_handler = InputHandler(game_state, grid, renderer)
    
    # Initialize Wave Manager
    wave_manager = WaveManager()
    current_wave_number = 0

    # Initialize Curve Editor
    curve_state = CurveState()
    # Initial state: Only 2 points (Start and End) as per rules
    curve_state.add_point(0.0, 10.0)
    curve_state.add_point(19.0, 10.0)
    curve_editor = CurveEditorUI(SCREEN_WIDTH, SCREEN_HEIGHT, renderer, curve_state)


    def get_enemy_path() -> List[Tuple[float, float]]:
        """Get enemy path from curve editor."""
        return curve_state.get_interpolated_path(100)

    # Initialize UI Feedback Components
    wave_banner = WaveBanner(SCREEN_WIDTH, SCREEN_HEIGHT)
    result_screen = ResultScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Initialize Effect Manager
    effect_manager = EffectManager()
    
    # Game stats for result screen
    game_stats = {
        "Waves Survived": 0,
        "Enemies Killed": 0,
        "Money Earned": 0,
    }

    # Wave event callbacks
    def on_wave_start(wave_num: int) -> None:
        logger.info(f"Wave {wave_num} started!")
        wave_banner.show(f"Wave {wave_num} Starting!", duration=2.0)
    
    def on_wave_complete(wave_num: int) -> None:
        logger.info(f"Wave {wave_num} complete!")
        game_stats["Waves Survived"] = wave_num
        wave_banner.show(f"Wave {wave_num} Complete!", duration=2.0)
    
    wave_manager.subscribe_wave_start(on_wave_start)
    wave_manager.subscribe_wave_complete(on_wave_complete)
    
    # Link UI Manager to Input Handler
    input_handler.ui_manager = ui_manager

    # Connect tower selection callback
    def on_tower_selected(tower):
        """Callback when a tower is selected."""
        ui_manager.select_tower(tower)
    
    input_handler.on_tower_selected = on_tower_selected

    # Initialize Combat Manager
    combat_manager = CombatManager()
    game_over = False
    victory = False

    # Combat event handlers
    def on_enemy_killed(enemy: Enemy, reward: int) -> None:
        game_state.add_money(reward)
        game_stats["Enemies Killed"] += 1
        game_stats["Money Earned"] += reward
        logger.info(f"Enemy killed! Reward: ${reward}")

    def on_base_damaged(enemy: Enemy) -> None:
        nonlocal game_over
        lives_remain = game_state.lose_life()
        logger.info(f"Base damaged! Lives remaining: {game_state.lives}")
        if not lives_remain:
            game_over = True
            logger.info("GAME OVER!")
            result_screen.show_game_over(game_stats)

    combat_manager.on_enemy_killed(on_enemy_killed)
    combat_manager.on_base_damaged(on_base_damaged)

    # 3. Main Loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle result screen events first (if visible)
        if result_screen.visible:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                action = result_screen.handle_event(event)
                if action == "quit":
                    running = False
                elif action == "restart":
                    # Reset game state
                    game_state.reset()
                    wave_manager.reset()
                    grid.clear()
                    current_wave_number = 0
                    game_over = False
                    victory = False
                    game_stats = {"Waves Survived": 0, "Enemies Killed": 0, "Money Earned": 0}
                    result_screen.hide()
            
            # Draw result screen
            renderer.render(game_state, combat_manager)
            result_screen.draw(screen)
            pygame.display.flip()
            continue
        
        # Normal game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            # UI handles event first
            if ui_manager.handle_event(event):
                continue

            # During PLANNING phase, let curve editor handle events
            if game_state.current_phase == GamePhase.PLANNING:
                if curve_editor.handle_event(event):
                    continue
                
            # Game world handles event
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                input_handler._handle_left_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                input_handler._handle_keydown(event.key)
            
        # Sync tower selection
        input_handler.selected_tower_type = ui_manager.selected_tower_type
            
        # Update
        entities = game_state.entities_collection
        
        # Update Enemies
        for enemy in entities.get('enemies', []):
            enemy.update(dt)

        # Update Effects on enemies
        effect_manager.update(dt, entities.get('enemies', []))

        # Update Combat
        combat_manager.update(dt, game_state)
        
        # Update Towers
        for tower in entities.get('towers', []):
            tower.update(dt)
        
        # Update Wave Manager during BATTLE phase
        if game_state.current_phase == GamePhase.BATTLE:
            if not wave_manager.is_active:
                current_wave_number += 1
                if current_wave_number <= wave_manager.total_waves:
                    wave_manager.start_wave(current_wave_number, get_enemy_path())
            
            new_enemies = wave_manager.update(dt)
            for enemy in new_enemies:
                game_state.add_entity('enemies', enemy)
            
            for enemy in game_state.entities_collection.get('enemies', []):
                enemy.update(dt)
            
            # Check for wave completion and victory
            if wave_manager.is_wave_complete():
                if not wave_manager.has_more_waves():
                    victory = True
                    game_state.change_phase(GamePhase.RESULT)
                    result_screen.show_victory(game_stats)
        
        # Update wave banner
        wave_banner.update(dt)
            
        # Draw everything
        renderer.render(game_state, combat_manager)

        # Draw curve editor during PLANNING phase
        if game_state.current_phase == GamePhase.PLANNING:
            path = curve_state.get_interpolated_path(100)
            if len(path) >= 2:
                renderer.draw_curve(path, color=CURVE_COLOR, width=2)
            curve_editor.draw(screen)
            curve_editor.draw_control_points(screen)

        # Draw UI
        ui_manager.draw(screen)
        
        # Draw wave banner on top
        wave_banner.draw(screen)
        
        # Single flip at the end
        pygame.display.flip()
        
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
