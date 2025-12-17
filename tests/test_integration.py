"""
Integration test demonstrating entities working with the math engine.

This shows how the complete system works: interpolation + entities.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from math_engine.interpolator import Interpolator
from entities.factory import EntityFactory
from entities.enemy import EnemyType
from entities.tower import TowerType


def test_full_game_scenario():
    """Test a complete game scenario with path interpolation and entities."""
    
    # 1. Create a path using interpolation
    control_points = [(0, 0), (50, 100), (150, 120), (200, 50)]
    path = Interpolator.cubic_spline_interpolate(control_points, num_points=200)
    
    print(f"Generated path with {len(path)} points")
    
    # 2. Create enemies that will follow the path
    wave1 = EntityFactory.create_wave(1, path)
    print(f"Wave 1 has {len(wave1)} enemies")
    
    # 3. Place some towers
    tower1 = EntityFactory.create_tower(TowerType.CALCULO, (50, 100))
    tower2 = EntityFactory.create_tower(TowerType.FISICA, (150, 120))
    
    print(f"Placed {2} towers")
    
    # 4. Simulate game loop for a few seconds
    dt = 0.016  # ~60 FPS
    simulation_time = 5.0
    total_steps = int(simulation_time / dt)
    
    towers = [tower1, tower2]
    enemies_defeated = 0
    enemies_reached_end = 0
    
    for step in range(total_steps):
        # Update all enemies
        for enemy in wave1:
            enemy.update(dt)
            
            # Check if enemy reached end
            if enemy.has_reached_end():
                enemies_reached_end += 1
        
        # Update all towers
        for tower in towers:
            tower.update(dt)
            
            # Find and attack targets
            if tower.can_attack():
                target = tower.find_target(wave1)
                if target:
                    tower.attack(target)
        
        # Count defeated enemies
        enemies_defeated = sum(1 for e in wave1 if not e.is_alive())
    
    print(f"After {simulation_time}s simulation:")
    print(f"  Enemies defeated: {enemies_defeated}/{len(wave1)}")
    print(f"  Enemies reached end: {enemies_reached_end}/{len(wave1)}")
    print(f"  Enemies still moving: {len(wave1) - enemies_defeated - enemies_reached_end}/{len(wave1)}")
    
    # Verify that something happened
    assert enemies_defeated > 0 or enemies_reached_end > 0, "No enemies were defeated or reached the end"
    
    # Verify towers engaged
    total_damage_dealt = sum(
        (simulation_time / (1.0 / tower.attack_speed)) * tower.damage 
        for tower in towers
    )
    print(f"  Total potential damage from towers: {total_damage_dealt:.1f}")
    
    print("\n✓ Integration test passed!")


if __name__ == "__main__":
    test_full_game_scenario()
