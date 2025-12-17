# Tasks.md - Project Roadmap

This document tracks the progress and future phases of "PathWars: The Interpolation Duel".

---

# ✅ COMPLETED PHASES

## 1. Network Core System ✅
- [x] Basic TCP Sockets with Observer pattern in `src/network/manager.py`.
## 2. Game Entities Logic ✅
## 3. Game State & Grid System ✅
## 4. Visual Engine & Main Loop ✅
## 5. UI & Interaction Layer ✅
## 6. Curve Editor System ✅
## 7. Wave Manager & Spawner ✅
## 8. Combat System ✅
## 9. Wave Transition & Game Feedback ✅
## 10. Tower Special Effects ✅
## 11. Curve Editor Integration ✅
-   [x] Integrated in `main.py`
-   [x] Added smooth interpolation with chordal parameterization.
-   [x] Enforced X-sorting (Mathematical Function property).
-   [x] Restricted to Grid: Control points are now clamped to grid cells.
## 12. Wire Up Game Feedback Components ✅
## 13. Wire Up Tower Effects ✅

---

# 🚧 UPCOMING PHASES

## 14. Multiplayer Integration (1v1 Dueling) 🚀 PRIORITY
**Context:** Connect the existing socket layer to gameplay for 1v1 duels as per GDD.
- [ ] **Main Menu**: Add "Host" / "Join" screen.
- [ ] **Dual View**: Client sees their base on one side, Host on the other (or mirrored views).
- [ ] **Asymmetric Pathing**: 
    - [ ] Player A edits the path for the enemies attacking Player B.
    - [ ] Player B edits the path for the enemies attacking Player A.
- [ ] **Sync Engine**: Real-time synchronization of `CurveState` and Tower placements.

## 15. Curve Mechanics & Planning Phase
**Context:** Enforce rules for point placement and game flow.
- [ ] **Start Config**: Initialize match with only 2 points (Start/End).
- [ ] **Planning Phase Lockdown**: Control points can ONLY be added/moved during the `PLANNING` phase (between waves).
- [ ] **Wave Start Trigger**: Wave only starts when both players are "Ready" or timer expires.

## 16. Asset Integration (Sprites & Particles)
**Context:** Visual overhaul from prototypes to final assets.
- [ ] **Professor Sprites**: Dean, Calculus, Physics, Statistics.
- [ ] **Enemy Sprites**: Student, Variable X.
- [ ] **Visual Effects**: Particle systems for attacks (math symbols).

## 17. Tower Upgrade System (Mastery -> Doctorate)
- [ ] UI: Add "Upgrade" button.
- [ ] Logic: Increase Damage/Range/Cooldown.

## 18. Audio & Sound FX System
- [ ] Background Music: Synthwave/Lo-fi academic.
- [ ] SFX: Shots, deaths, UI clicks.

---

# 📋 CURRENT FOCUS
- **Connecting Sockets to Gameplay**: Turning the single-player prototype into the 1v1 duel described in the GDD.
