# Tasks.md - Parallel Development Plan

This document outlines independent feature modules to be developed asynchronously by different agents.
**CRITICAL INSTRUCTIONS FOR ALL AGENTS:**
1.  **Git Flow:** ALWAYS create a new branch from `main` before starting. NEVER push directly to `main` without testing.
2.  **Code Quality:** Use Type Hints (`typing`), Docstrings (Google/NumPy style), and follow PEP 8.
3.  **Testing:** Every feature MUST have accompanying unit tests in `tests/`. No code is accepted without green tests.
4.  **Documentation:** Keep this file updated. Mark tasks as `[x]` when done.

> 📖 See [QuickReference.md](QuickReference.md) for game configuration parameters.

---

# ✅ COMPLETED PHASES

## 1. Network Core System ✅
## 2. Game Entities Logic ✅
## 3. Game State & Grid System ✅
## 4. Visual Engine & Main Loop ✅
## 5. UI & Interaction Layer (Partial) ✅
## 6. Curve Editor System ✅
## 7. Wave Manager & Spawner ✅
## 8. Combat System ✅

---

# 🚧 PENDING PHASES

---

## 9. Wave Transition & Game Feedback 🔀
**Branch Name:** `feature/game-feedback`
**Context:** Improve player feedback when waves change and game ends.

### Implementation Steps
1.  [ ] **Wave Transition Notification:**
    -   Show "Wave X Complete!" banner when wave ends.
    -   Brief pause (1-2 seconds) before next wave starts.
    -   Sound effect (optional).
2.  [ ] **Wave Counter UI:**
    -   Display "Wave 3/5" in HUD.
    -   Animate wave number change.
3.  [ ] **Result Screen:**
    -   Show "VICTORY" screen when all 5 waves cleared.
    -   Show "GAME OVER" screen when lives reach 0.
    -   Display stats: enemies killed, waves survived, money earned.
    -   "Play Again" and "Quit" buttons.
4.  [ ] **Unit Tests:** Test wave transition events fire correctly.

---

## 10. Tower Special Effects 🔀
**Branch Name:** `feature/tower-effects`
**Context:** Implement unique abilities for each tower type as per GDD.

### Implementation Steps
1.  [ ] **DEAN - Stun Effect:**
    -   When enemy enters range, apply "stun" (pause movement for X seconds).
    -   Add `stunned_duration` to `Enemy` class.
    -   Visual: Show "speech bubble" or freeze animation.
2.  [ ] **PHYSICS - AoE Damage:**
    -   On attack, damage all enemies within `splash_radius` of target.
    -   Add `splash_radius` to Tower stats.
    -   Visual: Show explosion circle.
3.  [ ] **STATISTICS - Slow Effect:**
    -   On attack, reduce enemy speed by X% for Y seconds.
    -   Add `slow_amount`, `slow_duration` to effect system.
    -   Visual: Show "confusion" particles.
4.  [ ] **Unit Tests:** Test each effect applies correctly.

---

## 11. Curve Editor Integration 🔀
**Branch Name:** `feature/curve-integration`
**Context:** Connect existing CurveEditor UI to the main game loop.

### Implementation Steps
1.  [ ] **Show CurveEditor during PLANNING phase only.**
2.  [ ] **Use `curve_state.get_interpolated_path()` as the enemy path.**
3.  [ ] **Draw the curve preview in Renderer.**
4.  [ ] **Add "Confirm Path" button to lock in the curve.**

---

## 12. Multiplayer Integration (Sequential)
**Branch Name:** `feature/multiplayer-integration`
**Context:** Connect NetworkManager to sync game state between players.
**Dependencies:** ⚠️ Requires Phases 9-11 complete.

### Implementation Steps
1.  [ ] **Lobby/Connection UI:** Host/Join buttons.
2.  [ ] **Message Types:** `CURVE_DATA`, `TOWER_PLACED`, `PHASE_CHANGE`.
3.  [ ] **State Synchronization:** Send curve data on PLANNING end.
4.  [ ] **Testing:** Two-client local testing.

---

## 13. Polish & Asset Integration (Sequential)
**Branch Name:** `feature/polish`
**Context:** Replace placeholder graphics with actual sprites, add sound effects.
**Dependencies:** All gameplay features complete.

### Implementation Steps
1.  [ ] **Generate/Import Sprites:** Use prompts from GDD.md section 4.
2.  [ ] **Sound Effects:** Attack sounds, phase change sounds.
3.  [ ] **Menu & Game Over Screens:** Main menu, Victory/Defeat screens.

---

# 📋 PARALLEL EXECUTION SUMMARY

| Branch | Task | Can Run In Parallel With |
|--------|------|--------------------------|
| `feature/game-feedback` | Wave Feedback + Result Screen | Tower Effects, Curve Integration |
| `feature/tower-effects` | Tower Effects | Game Feedback, Curve Integration |
| `feature/curve-integration` | Curve Integration | Game Feedback, Tower Effects |
| `feature/multiplayer-integration` | Multiplayer | ❌ Must wait |
| `feature/polish` | Polish | ❌ Must wait for all |
