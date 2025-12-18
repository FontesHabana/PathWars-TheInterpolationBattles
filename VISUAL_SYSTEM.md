# Visual System Documentation

## Overview
This document describes the visual system implementation for PathWars - The Interpolation Battles, including sprites, animations, autotiling, and particle effects.

## Architecture

### Asset Management (`src/graphics/assets.py`)

The `AssetManager` class provides centralized asset loading and caching:

**Key Features:**
- Sprite loading with automatic caching
- Spritesheet support for animations
- Automatic placeholder generation for missing assets
- Preloading of all configured assets at startup

**Usage:**
```python
# Preload all assets at startup (done in main.py)
AssetManager.preload_all()

# Get a loaded sprite
sprite = AssetManager.get_sprite("dean_idle")

# Load a custom sprite
sprite = AssetManager.load_sprite("my_sprite", "path/to/image.png", (64, 64))

# Load a spritesheet
frames = AssetManager.load_spritesheet("walk_anim", "path/to/sheet.png", 32, 32, 8)
```

### Placeholder Generation (`src/graphics/placeholder_generator.py`)

When asset files are missing, the system automatically generates distinctive placeholder sprites:

**Tower Placeholders:**
- Dean (Tank): Blue Square
- Calculus (Ranged): Green Triangle  
- Physics (AoE): Orange Pentagon
- Statistics (Support): Purple Star

**Enemy Placeholders:**
- Student: Red Circle
- Variable X: Yellow Diamond

**Tile Placeholders:**
- Path tiles: Brown rectangles with directional indicators
- Grid cells: Gray borders

### Animation System (`src/graphics/animation.py`)

Frame-based animation system with multiple states:

**Components:**
- `AnimationState`: Enum of animation states (IDLE, WALK, ATTACK, DIE)
- `SpriteAnimator`: Manages single animation with frame timing
- `AnimatedSprite`: Manages multiple animation states

**Usage:**
```python
# Create an animator with frames
frames = [frame1, frame2, frame3]
animator = SpriteAnimator(frames, fps=10.0, loop=True)

# Create an animated sprite with multiple states
sprite = AnimatedSprite()
sprite.add_animation(AnimationState.IDLE, idle_animator)
sprite.add_animation(AnimationState.WALK, walk_animator)

# Update and render
sprite.update(dt)
current_frame = sprite.get_current_frame()
```

### Autotiling System (`src/graphics/autotiler.py`)

Intelligent tile selection for path rendering based on neighbor connections:

**Components:**
- `PathDirection`: Cardinal directions (NORTH, SOUTH, EAST, WEST)
- `PathTileType`: Types of path tiles (straight, curves, T-junctions, cross)
- `PathTileSelector`: Selects appropriate tile based on connections
- `PathRenderer`: Renders paths with automatic tile selection

**Tile Selection Logic:**
- Analyzes path direction at each point
- Determines connections to neighbors
- Selects appropriate tile (straight, curve, junction)

**Usage:**
```python
# Create path renderer
path_renderer = PathRenderer(renderer)

# Render a path with autotiling
path_points = [(0, 0), (5, 0), (5, 5), (10, 5)]
path_renderer.render_path(screen, path_points)
```

### Particle Effects (`src/graphics/effects.py`)

Particle system for visual feedback:

**Components:**
- `ParticleType`: Types of effects (EXPLOSION, IMPACT, SPARKLE)
- `Particle`: Individual particle with physics
- `ParticleEmitter`: Emits and manages particles
- `VisualEffectManager`: Manages all active effects

**Features:**
- Particle physics (velocity, gravity)
- Lifetime management
- Alpha fading
- Multiple effect types

**Usage:**
```python
# Create effect manager
effect_manager = VisualEffectManager()

# Spawn effects
effect_manager.spawn_explosion((5.0, 5.0), size="medium")
effect_manager.spawn_impact((10.0, 10.0))

# Update and render (in game loop)
effect_manager.update(dt)
effect_manager.draw(screen, renderer.cart_to_iso)
```

## Entity Integration

### Towers (`src/entities/tower.py`)

Towers now have sprite name properties:

```python
tower = Tower(position, TowerType.CALCULUS)
sprite_name = tower.sprite_name  # Returns "calculus_idle"
sprite = AssetManager.get_sprite(sprite_name)
```

### Enemies (`src/entities/enemy.py`)

Enemies now have sprite names and animation state:

```python
enemy = Enemy(position, EnemyType.STUDENT, path)
sprite_name = enemy.sprite_name  # Returns "student_walk"
sprite = AssetManager.get_sprite(sprite_name)
```

## Renderer Integration (`src/graphics/renderer.py`)

The renderer now uses sprites when available:

**Drawing Methods:**
- `_draw_tower_sprite()`: Renders tower using sprite
- `_draw_tower_placeholder()`: Fallback to geometric placeholder
- `_draw_enemy_sprite()`: Renders enemy using sprite
- `_draw_enemy_placeholder()`: Fallback to geometric placeholder

**Automatic Fallback:**
If a sprite is not available, the renderer automatically falls back to placeholder rendering.

## Asset Configuration

Assets are configured in `ASSET_CONFIG` dictionary in `assets.py`:

```python
ASSET_CONFIG = {
    "towers": {
        "dean_idle": {"path": "assets/sprites/towers/dean_idle.png", "size": (64, 64)},
        # ... more towers
    },
    "enemies": {
        "student_walk": {"path": "assets/sprites/enemies/student_walk.png", "size": (32, 32)},
        # ... more enemies
    },
    "tiles": {
        "path_h": {"path": "assets/sprites/tiles/path_straight_h.png", "size": (32, 32)},
        # ... more tiles
    },
}
```

## Directory Structure

```
assets/
├── sprites/
│   ├── towers/
│   │   ├── dean_idle.png
│   │   ├── calculus_idle.png
│   │   ├── physics_idle.png
│   │   └── statistics_idle.png
│   ├── enemies/
│   │   ├── student_walk.png
│   │   └── variable_x_walk.png
│   ├── tiles/
│   │   ├── grid_cell.png
│   │   ├── path_straight_h.png
│   │   ├── path_straight_v.png
│   │   ├── path_curve_ne.png
│   │   ├── path_curve_nw.png
│   │   ├── path_curve_se.png
│   │   └── path_curve_sw.png
│   └── effects/
│       ├── explosion.png (optional spritesheet)
│       └── impact.png (optional)
```

## Testing

All visual systems have comprehensive test coverage:

- `tests/test_animation.py`: Animation system tests (13 tests)
- `tests/test_autotiler.py`: Autotiling logic tests (15 tests)
- `tests/test_visual_effects.py`: Particle effects tests (14 tests)
- `tests/test_asset_manager.py`: Asset loading tests (14 tests)

**Run tests:**
```bash
python -m pytest tests/test_animation.py -v
python -m pytest tests/test_autotiler.py -v
python -m pytest tests/test_visual_effects.py -v
python -m pytest tests/test_asset_manager.py -v
```

## Graceful Degradation

The system is designed to work without any asset files:

1. **Missing Sprites**: Automatically generates geometric placeholders
2. **Logging**: Warns when assets are missing but continues
3. **Fallback Rendering**: Renderer falls back to placeholder drawing
4. **No Crashes**: Game runs fully functional with all placeholders

## Performance Considerations

- **Caching**: All loaded sprites are cached in memory
- **Single Load**: Assets loaded once at startup via `preload_all()`
- **Efficient Rendering**: Sprites blitted directly, no per-frame generation
- **Particle Cleanup**: Dead particles automatically removed

## Future Enhancements

Possible future improvements:

1. **Spritesheet Animations**: Use actual spritesheets for enemy animations
2. **Path Autotiling in Renderer**: Integrate PathRenderer into main render loop
3. **Visual Effect Integration**: Hook up effects to game events (tower attacks, enemy deaths)
4. **Rotation**: Rotate sprites based on movement direction
5. **Asset Hot-Reloading**: Reload assets without restarting game
6. **Custom Fonts**: Load and use custom font files
