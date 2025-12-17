# Agent Prompts - Phase 9-11 Parallel Development

These prompts are designed with **clear file ownership** to minimize merge conflicts.

---

## FILE OWNERSHIP MAP (Avoid Conflicts!)

| Agent | Creates | Modifies |
|-------|---------|----------|
| 🔴 Game Feedback | `src/ui/wave_banner.py`, `src/ui/result_screen.py` | `src/ui/__init__.py` (add imports only) |
| 🟢 Tower Effects | `src/core/effects.py` | `src/entities/tower.py`, `src/entities/enemy.py` |
| 🔵 Curve Integration | - | `src/main.py` (lines 45-75 only) |

---

## 🔴 AGENT A: Wave Transition & Game Feedback

```
You are implementing **Wave Transition & Game Feedback** for "PathWars: The Interpolation Duel".

### YOUR TASK
Add visual feedback when waves complete and create Victory/Game Over screens.

### GIT WORKFLOW
1. `git checkout main && git pull`
2. `git checkout -b feature/game-feedback`
3. Work, commit frequently
4. `pytest tests/` before merge

### CRITICAL INSTRUCTIONS
- Type Hints, Docstrings (Google style), PEP 8
- Unit tests in `tests/` for all new code
- **FILE OWNERSHIP**: Only create NEW files, minimize edits to existing files

### FILES TO CREATE

1. **`src/ui/wave_banner.py`** (NEW)
   - Class `WaveBanner(screen_width, screen_height)`
   - `show(message, duration=2.0)` - displays banner
   - `update(dt)` - countdown timer
   - `draw(screen)` - render centered banner

2. **`src/ui/result_screen.py`** (NEW)
   - Class `ResultScreen(screen_width, screen_height)`
   - `show_victory(stats)` / `show_game_over(stats)`
   - `handle_event(event) -> str` returns 'restart' or 'quit'
   - `draw(screen)` - full screen with buttons

3. **`src/ui/__init__.py`** (MODIFY - add imports only)
   - Add: `from ui.wave_banner import WaveBanner`
   - Add: `from ui.result_screen import ResultScreen`

4. **`tests/test_wave_banner.py`** (NEW)
   - Test show/hide logic
   - Test timer countdown

### ACCEPTANCE CRITERIA
- [ ] WaveBanner appears centered on screen
- [ ] Banner auto-hides after duration
- [ ] ResultScreen shows Victory or Game Over
- [ ] ResultScreen has Play Again / Quit buttons
- [ ] All tests pass
```

---

## 🟢 AGENT B: Tower Special Effects

```
You are implementing **Tower Special Effects** for "PathWars: The Interpolation Duel".

### YOUR TASK
Add unique abilities: DEAN stuns, PHYSICS does AoE, STATISTICS slows enemies.

### GIT WORKFLOW
1. `git checkout main && git pull`
2. `git checkout -b feature/tower-effects`
3. Work, commit frequently
4. `pytest tests/` before merge

### CRITICAL INSTRUCTIONS
- Type Hints, Docstrings (Google style), PEP 8
- Unit tests in `tests/` for all new code
- **FILE OWNERSHIP**: Focus on entities/ and create effects.py

### FILES TO CREATE/MODIFY

1. **`src/core/effects.py`** (NEW)
   - `EffectType` enum: STUN, SLOW
   - `StatusEffect` dataclass: effect_type, duration, value
   - `EffectManager.apply_effect(enemy, effect)`
   - `EffectManager.update(dt, enemies)` - expire effects

2. **`src/entities/enemy.py`** (MODIFY)
   - Add `_active_effects: List[StatusEffect]`
   - Add `apply_effect()`, `update_effects()`, `is_stunned()`
   - In `update()`: skip movement if stunned, apply slow

3. **`src/entities/tower.py`** (MODIFY)
   - Add to stats: `stun_duration`, `splash_radius`, `slow_amount`
   - In `attack()`: apply effects based on tower type

4. **`tests/test_effects.py`** (NEW)
   - Test stun prevents movement
   - Test slow reduces speed
   - Test effects expire after duration

### ACCEPTANCE CRITERIA
- [ ] DEAN stuns enemies for 1 second
- [ ] PHYSICS damages enemies within splash radius
- [ ] STATISTICS slows enemies by 50% for 2 seconds
- [ ] Effects expire correctly
- [ ] All tests pass
```

---

## 🔵 AGENT C: Curve Editor Integration

```
You are implementing **Curve Editor Integration** for "PathWars: The Interpolation Duel".

### YOUR TASK
Connect the existing CurveEditor to the main game loop so players can design enemy paths.

### GIT WORKFLOW
1. `git checkout main && git pull`
2. `git checkout -b feature/curve-integration`
3. Work, commit frequently
4. `pytest tests/` before merge

### CRITICAL INSTRUCTIONS
- Type Hints, Docstrings (Google style), PEP 8
- **FILE OWNERSHIP**: Only modify main.py lines 45-75 (curve section)

### EXISTING CODE (do NOT recreate)
- `src/core/curve_state.py` - CurveState class
- `src/ui/curve_editor.py` - CurveEditorUI

### FILES TO MODIFY

1. **`src/main.py`** (MODIFY lines 45-75 ONLY)
   Replace `default_path = [...]` with:
   ```python
   from ui.curve_editor import CurveEditorUI
   from core.curve_state import CurveState
   
   curve_state = CurveState()
   curve_state.add_point(0, 10)
   curve_state.add_point(5, 10)
   curve_state.add_point(10, 5)
   curve_state.add_point(15, 15)
   curve_state.add_point(19, 10)
   
   curve_editor = CurveEditorUI(SCREEN_WIDTH, SCREEN_HEIGHT, curve_state)
   ```

2. **In main loop PLANNING phase:**
   - Handle `curve_editor.handle_event(event)`
   - Draw curve preview and control points

3. **When starting BATTLE:**
   - Use `curve_state.get_interpolated_path(100)` as enemy path

### ⚠️ COORDINATE SYSTEM NOTE
CurveEditor uses SCREEN pixels, enemies need GRID coords (0-19).
Convert: `grid_x = screen_x / tile_width`

### ACCEPTANCE CRITERIA
- [ ] CurveEditor visible only in PLANNING phase
- [ ] Control points can be added/dragged
- [ ] Curve preview shows on screen
- [ ] Enemies follow the custom curve during BATTLE
- [ ] Switching interpolation method changes curve shape
```

---

## 📋 EXECUTION ORDER

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   AGENT A       │   │   AGENT B       │   │   AGENT C       │
│ Game Feedback   │   │ Tower Effects   │   │ Curve Integ.    │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┴─────────────────────┘
                               │
                               ▼
                       USER merges all
```

After all 3 complete, merge in order:
1. `git merge feature/game-feedback`
2. `git merge feature/tower-effects`
3. `git merge feature/curve-integration`