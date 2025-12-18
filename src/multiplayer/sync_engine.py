"""
Sync Engine Module.

Handles state synchronization between players in a multiplayer duel.
Synchronizes curve states, tower placements, and game events.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

from network.manager import NetworkManager
from network.protocol import Message, MessageType
from core.curve_state import CurveState

logger = logging.getLogger(__name__)


class SyncMessageType(Enum):
    """
    Enumeration of synchronization message types.
    
    These are sent as subtypes within GAME_STATE messages.
    """
    CURVE_UPDATE = auto()
    CURVE_POINT_ADD = auto()
    CURVE_POINT_MOVE = auto()
    CURVE_POINT_REMOVE = auto()
    CURVE_METHOD_CHANGE = auto()
    TOWER_PLACE = auto()
    TOWER_REMOVE = auto()
    PHASE_CHANGE = auto()
    READY_STATE = auto()
    GAME_EVENT = auto()
    FULL_SYNC = auto()


@dataclass
class SyncMessage:
    """
    Synchronization message for game state updates.
    
    Attributes:
        sync_type: The type of synchronization message.
        data: The data payload for the sync message.
        sequence: Sequence number for ordering.
    """
    sync_type: SyncMessageType
    data: Dict[str, Any] = field(default_factory=dict)
    sequence: int = 0
    
    def to_payload(self) -> Dict[str, Any]:
        """
        Convert SyncMessage to a dictionary payload.
        
        Returns:
            Dictionary representation for network transmission.
        """
        return {
            'sync_type': self.sync_type.name,
            'data': self.data,
            'sequence': self.sequence,
        }
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'SyncMessage':
        """
        Create a SyncMessage from a dictionary payload.
        
        Args:
            payload: Dictionary containing sync message data.
            
        Returns:
            A new SyncMessage instance.
            
        Raises:
            KeyError: If required fields are missing.
            ValueError: If sync_type is invalid.
        """
        return cls(
            sync_type=SyncMessageType[payload['sync_type']],
            data=payload.get('data', {}),
            sequence=payload.get('sequence', 0),
        )


class SyncEngine:
    """
    Synchronization engine for multiplayer game state.
    
    Manages synchronization of curve states, tower placements, and game events
    between players using the NetworkManager.
    
    Attributes:
        network_manager: The NetworkManager instance for sending/receiving messages.
    """
    
    def __init__(self, network_manager: NetworkManager) -> None:
        """
        Initialize the SyncEngine.
        
        Args:
            network_manager: NetworkManager instance for communication.
        """
        self._network_manager = network_manager
        self._sequence_number = 0
        self._observers: Dict[SyncMessageType, List[Callable[[SyncMessage], None]]] = {}
        
        # Subscribe to network messages
        self._network_manager.subscribe(MessageType.GAME_STATE, self._on_network_message)
    
    def subscribe(self, sync_type: SyncMessageType, callback: Callable[[SyncMessage], None]) -> None:
        """
        Subscribe to receive sync messages of a specific type.
        
        Args:
            sync_type: The type of sync message to subscribe to.
            callback: Function to call when a message of this type arrives.
        """
        if sync_type not in self._observers:
            self._observers[sync_type] = []
        self._observers[sync_type].append(callback)
    
    def unsubscribe(self, sync_type: SyncMessageType, callback: Callable[[SyncMessage], None]) -> None:
        """
        Unsubscribe from receiving sync messages of a specific type.
        
        Args:
            sync_type: The type of sync message to unsubscribe from.
            callback: The callback function to remove.
        """
        if sync_type in self._observers:
            try:
                self._observers[sync_type].remove(callback)
            except ValueError:
                pass
    
    def _notify_observers(self, sync_msg: SyncMessage) -> None:
        """
        Notify all observers subscribed to this sync message type.
        
        Args:
            sync_msg: The sync message that was received.
        """
        if sync_msg.sync_type in self._observers:
            for callback in self._observers[sync_msg.sync_type]:
                try:
                    callback(sync_msg)
                except Exception as e:
                    logger.error(f"Error in sync callback: {e}")
    
    def _on_network_message(self, message: Message) -> None:
        """
        Handle incoming network messages.
        
        Args:
            message: The network message received.
        """
        try:
            sync_msg = SyncMessage.from_payload(message.payload)
            self._notify_observers(sync_msg)
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing sync message: {e}")
    
    def _send_sync(self, sync_msg: SyncMessage) -> bool:
        """
        Send a synchronization message.
        
        Args:
            sync_msg: The sync message to send.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg.sequence = self._sequence_number
        self._sequence_number += 1
        
        message = Message(
            msg_type=MessageType.GAME_STATE,
            payload=sync_msg.to_payload()
        )
        
        return self._network_manager.send(message)
    
    def sync_full_curve(self, curve_state: CurveState) -> bool:
        """
        Send a full curve state synchronization.
        
        Args:
            curve_state: The curve state to synchronize.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.FULL_SYNC,
            data={
                'control_points': curve_state.control_points,
                'interpolation_method': curve_state.interpolation_method,
            }
        )
        return self._send_sync(sync_msg)
    
    def sync_point_added(self, x: float, y: float) -> bool:
        """
        Synchronize addition of a control point.
        
        Args:
            x: X coordinate of the new point.
            y: Y coordinate of the new point.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.CURVE_POINT_ADD,
            data={'x': x, 'y': y}
        )
        return self._send_sync(sync_msg)
    
    def sync_point_moved(self, index: int, x: float, y: float) -> bool:
        """
        Synchronize movement of a control point.
        
        Args:
            index: Index of the point that was moved.
            x: New X coordinate.
            y: New Y coordinate.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.CURVE_POINT_MOVE,
            data={'index': index, 'x': x, 'y': y}
        )
        return self._send_sync(sync_msg)
    
    def sync_point_removed(self, index: int) -> bool:
        """
        Synchronize removal of a control point.
        
        Args:
            index: Index of the point that was removed.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.CURVE_POINT_REMOVE,
            data={'index': index}
        )
        return self._send_sync(sync_msg)
    
    def sync_method_changed(self, method: str) -> bool:
        """
        Synchronize change of interpolation method.
        
        Args:
            method: The new interpolation method.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.CURVE_METHOD_CHANGE,
            data={'method': method}
        )
        return self._send_sync(sync_msg)
    
    def sync_tower_placed(self, tower_type: str, x: int, y: int) -> bool:
        """
        Synchronize tower placement.
        
        Args:
            tower_type: Type of tower placed.
            x: Grid X coordinate.
            y: Grid Y coordinate.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.TOWER_PLACE,
            data={'tower_type': tower_type, 'x': x, 'y': y}
        )
        return self._send_sync(sync_msg)
    
    def sync_tower_removed(self, x: int, y: int) -> bool:
        """
        Synchronize tower removal.
        
        Args:
            x: Grid X coordinate.
            y: Grid Y coordinate.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.TOWER_REMOVE,
            data={'x': x, 'y': y}
        )
        return self._send_sync(sync_msg)
    
    def sync_phase_change(self, phase: str) -> bool:
        """
        Synchronize game phase change.
        
        Args:
            phase: The new game phase name.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.PHASE_CHANGE,
            data={'phase': phase}
        )
        return self._send_sync(sync_msg)
    
    def sync_game_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Synchronize a game event.
        
        Args:
            event_type: Type of the game event.
            event_data: Data associated with the event.
            
        Returns:
            True if sent successfully, False otherwise.
        """
        sync_msg = SyncMessage(
            sync_type=SyncMessageType.GAME_EVENT,
            data={'event_type': event_type, 'event_data': event_data}
        )
        return self._send_sync(sync_msg)
