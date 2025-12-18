"""
Player Role Module.

Defines player roles in a multiplayer duel (HOST or CLIENT).
"""

from enum import Enum, auto


class PlayerRole(Enum):
    """
    Enumeration of player roles in a multiplayer duel.
    
    Attributes:
        HOST: The player hosting the game.
        CLIENT: The player joining the game.
    """
    HOST = auto()
    CLIENT = auto()
    
    def opponent(self) -> 'PlayerRole':
        """
        Get the opposing player role.
        
        Returns:
            The opposite role (HOST returns CLIENT, CLIENT returns HOST).
        """
        if self == PlayerRole.HOST:
            return PlayerRole.CLIENT
        return PlayerRole.HOST
