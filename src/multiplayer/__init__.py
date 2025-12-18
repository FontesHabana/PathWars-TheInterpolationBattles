"""
Multiplayer module for 1v1 duel functionality.

Provides components for hosting/joining games, state synchronization,
and split-screen rendering.
"""

from .player_role import PlayerRole
from .sync_engine import SyncEngine, SyncMessage, SyncMessageType
from .duel_session import DuelSession, DuelPhase, DuelPlayer
from .dual_view import DualView

__all__ = [
    'PlayerRole',
    'SyncEngine',
    'SyncMessage',
    'SyncMessageType',
    'DuelSession',
    'DuelPhase',
    'DuelPlayer',
    'DualView',
]
