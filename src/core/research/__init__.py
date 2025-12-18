"""
Research system for PathWars - The Interpolation Battles.

This package provides the research and development system that allows
players to unlock new interpolation methods and curve control features.
"""

from .research_type import ResearchType, ResearchInfo, RESEARCH_INFO
from .research_manager import (
    ResearchManager,
    InsufficientFundsError,
    PrerequisiteNotMetError,
    AlreadyResearchedError
)

__all__ = [
    'ResearchType',
    'ResearchInfo',
    'RESEARCH_INFO',
    'ResearchManager',
    'InsufficientFundsError',
    'PrerequisiteNotMetError',
    'AlreadyResearchedError',
]
