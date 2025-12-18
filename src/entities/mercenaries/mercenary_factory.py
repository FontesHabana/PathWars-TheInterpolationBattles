"""
Factory for creating mercenary instances using the Factory Pattern.

This module provides a centralized factory for creating mercenary units,
validating purchases, and managing mercenary types.
"""

from entities.mercenaries.base_mercenary import BaseMercenary
from entities.mercenaries.mercenary_types import (
    MercenaryType,
    ReinforcedStudent,
    SpeedyVariableX,
    TankConstantPi,
)


class MercenaryFactory:
    """Factory for creating mercenary instances (Factory Pattern)."""
    
    # Mapping of mercenary types to their concrete classes
    _MERCENARY_CLASSES = {
        MercenaryType.REINFORCED_STUDENT: ReinforcedStudent,
        MercenaryType.SPEEDY_VARIABLE_X: SpeedyVariableX,
        MercenaryType.TANK_CONSTANT_PI: TankConstantPi,
    }
    
    @staticmethod
    def create_mercenary(
        mercenary_type: MercenaryType,
        owner_player_id: str,
        target_player_id: str
    ) -> BaseMercenary:
        """
        Create a mercenary of the specified type.
        
        Args:
            mercenary_type: Type of mercenary to create.
            owner_player_id: ID of player who owns/sent this mercenary.
            target_player_id: ID of player this mercenary attacks.
            
        Returns:
            New mercenary instance.
            
        Raises:
            ValueError: If mercenary type is unknown.
        """
        mercenary_class = MercenaryFactory._MERCENARY_CLASSES.get(mercenary_type)
        
        if mercenary_class is None:
            raise ValueError(f"Unknown mercenary type: {mercenary_type}")
        
        return mercenary_class(owner_player_id, target_player_id)
    
    @staticmethod
    def get_cost(mercenary_type: MercenaryType) -> int:
        """
        Get the cost of a mercenary type.
        
        Args:
            mercenary_type: Type of mercenary to get cost for.
            
        Returns:
            Cost in dollars.
            
        Raises:
            ValueError: If mercenary type is unknown.
        """
        mercenary_class = MercenaryFactory._MERCENARY_CLASSES.get(mercenary_type)
        
        if mercenary_class is None:
            raise ValueError(f"Unknown mercenary type: {mercenary_type}")
        
        # Access the class attribute directly instead of creating an instance
        return mercenary_class._stats.cost
    
    @staticmethod
    def get_available_types() -> list[MercenaryType]:
        """
        Get list of all available mercenary types.
        
        Returns:
            List of available mercenary types.
        """
        return list(MercenaryFactory._MERCENARY_CLASSES.keys())
    
    @staticmethod
    def validate_purchase(
        mercenary_type: MercenaryType,
        quantity: int,
        available_money: int
    ) -> bool:
        """
        Check if player can afford to purchase mercenaries.
        
        Args:
            mercenary_type: Type of mercenary to purchase.
            quantity: Number of mercenaries to purchase.
            available_money: Amount of money player has available.
            
        Returns:
            True if player can afford the purchase, False otherwise.
            
        Raises:
            ValueError: If mercenary type is unknown or quantity is invalid.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        cost = MercenaryFactory.get_cost(mercenary_type)
        total_cost = cost * quantity
        
        return available_money >= total_cost
