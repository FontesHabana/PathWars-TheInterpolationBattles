"""
Research type definitions and information for PathWars.

This module defines the available research types and their metadata,
including costs, prerequisites, and descriptions.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict


class ResearchType(Enum):
    """Types of research available in the game."""
    LAGRANGE_INTERPOLATION = auto()
    SPLINE_INTERPOLATION = auto()
    TANGENT_CONTROL = auto()


@dataclass(frozen=True)
class ResearchInfo:
    """Information about a research type."""
    research_type: ResearchType
    cost: int
    display_name: str
    description: str
    prerequisites: List[ResearchType]  # Research required before this one


# Define research info for each type
RESEARCH_INFO: Dict[ResearchType, ResearchInfo] = {
    ResearchType.LAGRANGE_INTERPOLATION: ResearchInfo(
        research_type=ResearchType.LAGRANGE_INTERPOLATION,
        cost=500,
        display_name="Lagrange Polynomial",
        description="Unlock Lagrange interpolation for smoother curves (warning: Runge's phenomenon at edges)",
        prerequisites=[]
    ),
    ResearchType.SPLINE_INTERPOLATION: ResearchInfo(
        research_type=ResearchType.SPLINE_INTERPOLATION,
        cost=1000,
        display_name="Cubic Spline",
        description="Unlock Cubic Spline interpolation for the smoothest curves",
        prerequisites=[ResearchType.LAGRANGE_INTERPOLATION]  # Requires Lagrange first
    ),
    ResearchType.TANGENT_CONTROL: ResearchInfo(
        research_type=ResearchType.TANGENT_CONTROL,
        cost=750,
        display_name="Tangent Control",
        description="Modify curve derivatives at control points for precise path control",
        prerequisites=[]
    ),
}
