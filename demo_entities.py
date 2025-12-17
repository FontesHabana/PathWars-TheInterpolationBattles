#!/usr/bin/env python
"""
Demonstration script showing the game entities in action.

This script demonstrates how to use the PathWars entities system:
1. Creating interpolated paths
2. Spawning enemies that follow paths
3. Placing towers that attack enemies
4. Running a simple game loop simulation
"""

import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from math_engine.interpolator import Interpolator
from entities import EntityFactory, EnemyType, TowerType, Vector2


def main():
    print("=" * 60)
    print("PathWars: Game Entities Demo")
    print("=" * 60)
    
    # Step 1: Create a curved path using interpolation
    print("\n1. Creating an interpolated path...")
    control_points = [
        (0, 0),      # Start
        (50, 100),   # First turn
        (150, 120),  # Peak
        (200, 50),   # Descent
        (250, 50)    # End
    ]
    
    # Use cubic spline for smooth movement
    path = Interpolator.cubic_spline_interpolate(control_points, num_points=250)
    print(f"   ✓ Generated smooth path with {len(path)} points")
    
    # Step 2: Create a wave of enemies
    print("\n2. Spawning enemy wave...")
    wave_enemies = EntityFactory.create_wave(wave_number=1, path=path)
    print(f"   ✓ Wave 1 spawned with {len(wave_enemies)} enemies:")
    
    enemy_types = {}
    for enemy in wave_enemies:
        enemy_types[enemy.enemy_type.value] = enemy_types.get(enemy.enemy_type.value, 0) + 1
    
    for enemy_type, count in enemy_types.items():
        print(f"     - {count}x {enemy_type}")
    
    # Step 3: Place defensive towers
    print("\n3. Placing defensive towers...")
    towers = [
        EntityFactory.create_tower(TowerType.CALCULO, (50, 100)),
        EntityFactory.create_tower(TowerType.FISICA, (150, 120)),
        EntityFactory.create_tower(TowerType.DECANO, (200, 50)),
    ]
    
    for tower in towers:
        print(f"   ✓ {tower.tower_type.value} placed at ({tower.position.x:.0f}, {tower.position.y:.0f})")
        print(f"     Range: {tower.range:.0f}, Damage: {tower.damage:.0f}, Speed: {tower.attack_speed:.1f} atk/s")
    
    # Step 4: Run simulation
    print("\n4. Running battle simulation...")
    print("-" * 60)
    
    dt = 0.016  # 60 FPS
    simulation_time = 10.0
    steps = int(simulation_time / dt)
    
    report_interval = 2.0  # Report every 2 seconds
    next_report = 2.0
    
    for step in range(steps):
        current_time = step * dt
        
        # Update enemies
        for enemy in wave_enemies:
            enemy.update(dt)
        
        # Update towers
        for tower in towers:
            tower.update(dt)
            
            if tower.can_attack():
                target = tower.find_target(wave_enemies)
                if target:
                    tower.attack(target)
        
        # Periodic reporting
        if current_time >= next_report:
            alive = sum(1 for e in wave_enemies if e.is_alive())
            dead = sum(1 for e in wave_enemies if not e.is_alive() and not e.has_reached_end())
            escaped = sum(1 for e in wave_enemies if e.has_reached_end())
            
            print(f"T={current_time:.1f}s | Alive: {alive} | Defeated: {dead} | Escaped: {escaped}")
            next_report += report_interval
    
    # Final statistics
    print("-" * 60)
    print("\n5. Battle Results:")
    
    total = len(wave_enemies)
    defeated = sum(1 for e in wave_enemies if not e.is_alive() and not e.has_reached_end())
    escaped = sum(1 for e in wave_enemies if e.has_reached_end())
    
    print(f"   Total Enemies: {total}")
    print(f"   Defeated: {defeated} ({defeated/total*100:.1f}%)")
    print(f"   Escaped: {escaped} ({escaped/total*100:.1f}%)")
    
    # Tower statistics
    print("\n6. Tower Performance:")
    for i, tower in enumerate(towers, 1):
        theoretical_attacks = simulation_time * tower.attack_speed
        print(f"   Tower {i} ({tower.tower_type.value}):")
        print(f"     Max Attacks: {theoretical_attacks:.0f}")
        print(f"     Potential Damage: {theoretical_attacks * tower.damage:.0f}")
    
    print("\n" + "=" * 60)
    print("Demo complete! All systems working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    main()
