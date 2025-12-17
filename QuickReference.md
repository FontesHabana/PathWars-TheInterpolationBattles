# Quick Reference - PathWars Configuration

This document shows where to modify common game parameters.

---

## 💰 Initial Money
**File:** `src/core/game_state.py` line 55
```python
self._money: int = 100  # Change this value
```

---

## 🛣️ Enemy Path (Default)
**File:** `src/main.py` lines 49-60
```python
default_path = [
    (0.0, 10.0),     # Start (grid coords, not pixels!)
    (5.0, 10.0),     # Waypoint 1
    (5.0, 5.0),      # Waypoint 2
    ...
    (19.0, 10.0),    # End
]
```
> **Note:** Coordinates are GRID cells (0-19), not screen pixels.

---

## 🏰 Tower Costs
**File:** `src/core/input_handler.py` lines 17-22
```python
TOWER_COSTS = {
    TowerType.DEAN: 50,
    TowerType.CALCULUS: 75,
    TowerType.PHYSICS: 100,
    TowerType.STATISTICS: 60,
}
```

---

## 🗼 Tower Stats (Damage, Range, Cooldown)
**File:** `src/entities/tower.py` lines 38-59
```python
_TOWER_STATS = {
    TowerType.DEAN: {"damage": 10, "attack_range": 2.0, "cooldown": 1.5},
    TowerType.CALCULUS: {"damage": 25, "attack_range": 5.0, "cooldown": 0.5},
    TowerType.PHYSICS: {"damage": 50, "attack_range": 4.0, "cooldown": 2.0},
    TowerType.STATISTICS: {"damage": 0, "attack_range": 3.5, "cooldown": 1.0},
}
```

---

## 👾 Enemy Stats (Health, Speed)
**File:** `src/entities/enemy.py` lines 37-40
```python
_ENEMY_STATS = {
    EnemyType.STUDENT: {"health": 100, "speed": 1.0},
    EnemyType.VARIABLE_X: {"health": 50, "speed": 2.0},
}
```

---

## 🌊 Wave Definitions
**File:** `src/core/wave_data.py`
- `get_predefined_waves()` returns the 5 wave configurations
- Each wave has `enemy_configs`, `spawn_interval`

---

## 🎨 Curve Editor
**Files:**
- `src/core/curve_state.py` - Data model for control points
- `src/ui/curve_editor.py` - Visual UI for editing

**Usage:**
```python
curve_state.add_point(x, y)
curve_state.set_method('spline')  # 'linear', 'lagrange', 'spline'
path = curve_state.get_interpolated_path(100)
```
