"""
Status effects system for PathWars - The Interpolation Battles.

This module defines status effects that can be applied to enemies, including
stun and slow effects from various tower types.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from entities.enemy import Enemy


class EffectType(Enum):
    """Enumeration of effect types that can be applied to enemies."""
    STUN = auto()   # Prevents movement completely
    SLOW = auto()   # Reduces movement speed


@dataclass
class StatusEffect:
    """
    A status effect that can be applied to an enemy.

    Attributes:
        effect_type: The type of effect (STUN or SLOW).
        duration: Remaining duration in seconds.
        value: Effect-specific value (e.g., slow percentage as 0.0-1.0).
    """
    effect_type: EffectType
    duration: float
    value: float = 0.0


class EffectManager:
    """
    Manages status effects on enemies.

    Provides methods to apply effects to enemies and update effect durations
    each game tick.
    """

    def __init__(self) -> None:
        """Initialize the EffectManager."""
        pass

    def apply_effect(self, enemy: "Enemy", effect: StatusEffect) -> None:
        """
        Apply a status effect to an enemy.

        Args:
            enemy: The enemy to apply the effect to.
            effect: The status effect to apply.
        """
        enemy.apply_effect(effect)

    def update(self, dt: float, enemies: List["Enemy"]) -> None:
        """
        Update all status effects on enemies, expiring those that have ended.

        Args:
            dt: Delta time since last update in seconds.
            enemies: List of enemies to update effects on.
        """
        for enemy in enemies:
            enemy.update_effects(dt)
