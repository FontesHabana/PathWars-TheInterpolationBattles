"""
Interpolation Strategy Registry

Manages registration and access to interpolation strategies.
Implements a singleton pattern to ensure consistent strategy access throughout the application.
"""

from typing import Dict, List, Set, Optional
from .interpolation_strategy import InterpolationStrategy
from .strategies import LinearInterpolation, LagrangeInterpolation, SplineInterpolation


class InterpolationRegistry:
    """
    Singleton registry for interpolation strategies.
    
    Manages all available interpolation strategies and provides methods to
    retrieve strategies by name and check unlock status.
    """
    
    _instance: Optional['InterpolationRegistry'] = None
    _strategies: Dict[str, InterpolationStrategy] = {}
    
    def __new__(cls) -> 'InterpolationRegistry':
        """Ensure only one instance of the registry exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_strategies()
        return cls._instance
    
    def _initialize_strategies(self) -> None:
        """Initialize and register all available strategies."""
        # Register all built-in strategies
        strategies = [
            LinearInterpolation(),
            LagrangeInterpolation(),
            SplineInterpolation(),
        ]
        
        for strategy in strategies:
            self._strategies[strategy.name] = strategy
    
    def get_strategy(self, name: str) -> InterpolationStrategy:
        """
        Get an interpolation strategy by name.
        
        Args:
            name: The name of the interpolation strategy.
                Valid values: 'linear', 'lagrange', 'spline'.
        
        Returns:
            The interpolation strategy instance.
            
        Raises:
            KeyError: If the strategy name is not registered.
        """
        if name not in self._strategies:
            raise KeyError(
                f"Unknown interpolation strategy: '{name}'. "
                f"Available strategies: {list(self._strategies.keys())}"
            )
        return self._strategies[name]
    
    def get_available_strategies(self) -> List[str]:
        """
        Get list of all available strategy names.
        
        Returns:
            List of strategy names that can be used with get_strategy().
        """
        return list(self._strategies.keys())
    
    def is_unlocked(self, name: str, unlocked_methods: Set[str]) -> bool:
        """
        Check if a strategy is unlocked for use.
        
        A strategy is unlocked if:
        - It doesn't require research, OR
        - Its name is in the unlocked_methods set
        
        Args:
            name: The name of the interpolation strategy to check.
            unlocked_methods: Set of method names that have been unlocked through research.
        
        Returns:
            True if the strategy can be used, False otherwise.
            
        Raises:
            KeyError: If the strategy name is not registered.
        """
        strategy = self.get_strategy(name)
        
        # Strategy is unlocked if it doesn't require research OR it's in the unlocked set
        return not strategy.requires_research or name in unlocked_methods
    
    def register_strategy(self, strategy: InterpolationStrategy) -> None:
        """
        Register a custom interpolation strategy.
        
        Allows extending the system with custom interpolation methods.
        
        Args:
            strategy: The interpolation strategy to register.
            
        Raises:
            ValueError: If a strategy with the same name is already registered.
        """
        if strategy.name in self._strategies:
            raise ValueError(
                f"Strategy '{strategy.name}' is already registered. "
                f"Use a different name or unregister the existing strategy first."
            )
        self._strategies[strategy.name] = strategy
    
    def unregister_strategy(self, name: str) -> None:
        """
        Unregister an interpolation strategy.
        
        Args:
            name: The name of the strategy to unregister.
            
        Raises:
            KeyError: If the strategy name is not registered.
        """
        if name not in self._strategies:
            raise KeyError(f"Strategy '{name}' is not registered")
        del self._strategies[name]


# Convenience function to get the singleton instance
def get_registry() -> InterpolationRegistry:
    """
    Get the singleton interpolation registry instance.
    
    Returns:
        The InterpolationRegistry singleton instance.
    """
    return InterpolationRegistry()
