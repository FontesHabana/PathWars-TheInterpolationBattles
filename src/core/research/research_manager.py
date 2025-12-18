"""
Research manager for tracking and validating research unlocks.

This module provides the ResearchManager class which handles research
purchases, prerequisite validation, and serialization for network sync.
"""

from typing import Set, List
import logging

from .research_type import ResearchType, RESEARCH_INFO

logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    """Raised when player cannot afford research."""
    pass


class PrerequisiteNotMetError(Exception):
    """Raised when research prerequisites are not met."""
    pass


class AlreadyResearchedError(Exception):
    """Raised when trying to research something already unlocked."""
    pass


class ResearchManager:
    """
    Manages research unlocks for a player.
    
    Tracks which research has been unlocked and validates new research purchases.
    
    Key Methods:
        unlock(research_type, available_money): Unlock a research if prerequisites
            and cost requirements are met.
        is_unlocked(research_type): Check if a research is already unlocked.
        can_unlock(research_type): Check if prerequisites are met (doesn't check cost).
        get_available_research(): Get list of research that can be unlocked.
        get_interpolation_methods(): Get set of unlocked interpolation method names.
        
    Raises:
        AlreadyResearchedError: When trying to unlock already researched item.
        PrerequisiteNotMetError: When prerequisites are not met.
        InsufficientFundsError: When player cannot afford the research.
        
    Example:
        >>> manager = ResearchManager("player1")
        >>> cost = manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        >>> methods = manager.get_interpolation_methods()  # {'linear', 'lagrange'}
    """
    
    def __init__(self, player_id: str) -> None:
        self._player_id = player_id
        self._unlocked: Set[ResearchType] = set()
        
    @property
    def player_id(self) -> str:
        return self._player_id
    
    @property
    def unlocked_research(self) -> Set[ResearchType]:
        """Return copy of unlocked research set."""
        return set(self._unlocked)
    
    def is_unlocked(self, research_type: ResearchType) -> bool:
        """Check if research is unlocked."""
        return research_type in self._unlocked
    
    def can_unlock(self, research_type: ResearchType) -> bool:
        """
        Check if research can be unlocked (prerequisites met).
        Does not check cost.
        """
        if research_type in self._unlocked:
            return False
        
        info = RESEARCH_INFO.get(research_type)
        if info is None:
            return False
        
        # Check prerequisites
        for prereq in info.prerequisites:
            if prereq not in self._unlocked:
                return False
        
        return True
    
    def get_cost(self, research_type: ResearchType) -> int:
        """Get cost of research."""
        info = RESEARCH_INFO.get(research_type)
        return info.cost if info else 0
    
    def unlock(self, research_type: ResearchType, available_money: int) -> int:
        """
        Attempt to unlock research.
        
        Args:
            research_type: Research to unlock.
            available_money: Player's current money.
            
        Returns:
            Cost of the research (to be deducted from player's money).
            
        Raises:
            AlreadyResearchedError: If already unlocked.
            PrerequisiteNotMetError: If prerequisites not met.
            InsufficientFundsError: If cannot afford.
        """
        if research_type in self._unlocked:
            raise AlreadyResearchedError(f"{research_type.name} is already researched")
        
        info = RESEARCH_INFO.get(research_type)
        if info is None:
            raise ValueError(f"Unknown research type: {research_type}")
        
        # Check prerequisites
        for prereq in info.prerequisites:
            if prereq not in self._unlocked:
                prereq_info = RESEARCH_INFO.get(prereq)
                prereq_name = prereq_info.display_name if prereq_info else prereq.name
                raise PrerequisiteNotMetError(
                    f"Must unlock '{prereq_name}' before '{info.display_name}'"
                )
        
        # Check cost
        if available_money < info.cost:
            raise InsufficientFundsError(
                f"Need {info.cost}$, have {available_money}$"
            )
        
        self._unlocked.add(research_type)
        logger.info(f"Player {self._player_id} unlocked {research_type.name}")
        return info.cost
    
    def get_available_research(self) -> List[ResearchType]:
        """Get list of research that can be unlocked (prerequisites met)."""
        available = []
        for rt in ResearchType:
            if self.can_unlock(rt):
                available.append(rt)
        return available
    
    def get_interpolation_methods(self) -> Set[str]:
        """
        Get set of interpolation method names unlocked.
        Always includes 'linear'.
        """
        methods = {'linear'}
        
        if ResearchType.LAGRANGE_INTERPOLATION in self._unlocked:
            methods.add('lagrange')
        
        if ResearchType.SPLINE_INTERPOLATION in self._unlocked:
            methods.add('spline')
        
        return methods
    
    def reset(self) -> None:
        """Reset all research (for new game)."""
        self._unlocked.clear()
    
    def to_dict(self) -> dict:
        """Serialize for network sync."""
        return {
            'player_id': self._player_id,
            'unlocked': [rt.name for rt in self._unlocked]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResearchManager':
        """Deserialize from network sync."""
        manager = cls(data['player_id'])
        for rt_name in data.get('unlocked', []):
            try:
                rt = ResearchType[rt_name]
                manager._unlocked.add(rt)
            except KeyError:
                pass
        return manager
