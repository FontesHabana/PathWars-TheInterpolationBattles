"""Core module for PathWars."""
from core.game_state import GameState, GamePhase
from core.local_game_state import LocalGameState, Particle, Animation, InterpolatedPosition
from core.curve_state import CurveState, CurveLockedError
from core.grid import Grid
from core.ready_manager import ReadyManager, ReadyTrigger
from core.phase_state import (
    GamePhaseState,
    PhaseType,
    PreparationPhaseState,
    PathModificationPhaseState,
    BuildingPhaseState,
    CombatPhaseState,
    RoundEndPhaseState,
    InvalidPhaseActionError,
    create_phase_state,
)
from core.phase_manager import (
    PhaseManager,
    InvalidPhaseTransitionError,
    ControlPointConstraintError,
)

__all__ = [
    "GameState",
    "GamePhase",
    "LocalGameState",
    "Particle",
    "Animation",
    "InterpolatedPosition",
    "CurveState",
    "CurveLockedError",
    "Grid",
    "ReadyManager",
    "ReadyTrigger",
    # Phase System
    "GamePhaseState",
    "PhaseType",
    "PreparationPhaseState",
    "PathModificationPhaseState",
    "BuildingPhaseState",
    "CombatPhaseState",
    "RoundEndPhaseState",
    "InvalidPhaseActionError",
    "create_phase_state",
    "PhaseManager",
    "InvalidPhaseTransitionError",
    "ControlPointConstraintError",
]
