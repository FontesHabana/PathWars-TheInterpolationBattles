"""
Protocol module for network communication.

This module defines message structures and serialization logic for the network layer.
Following SOLID principles, the protocol layer is separated from the transport layer.
"""

import json
import pickle
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(Enum):
    """Enumeration of message types for protocol identification."""
    HANDSHAKE = "handshake"
    ROUTE_DATA = "route_data"
    GAME_STATE = "game_state"
    TOWER_PLACEMENT = "tower_placement"
    DISCONNECT = "disconnect"
    ACK = "ack"


@dataclass
class Message:
    """
    Generic message structure for network communication.

    Attributes:
        msg_type: Type of the message from MessageType enum.
        payload: Dictionary containing the message data.
        sender_id: Optional identifier of the sender.
    """
    msg_type: MessageType
    payload: Dict[str, Any]
    sender_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary format.

        Returns:
            Dictionary representation of the message.
        """
        return {
            'msg_type': self.msg_type.value,
            'payload': self.payload,
            'sender_id': self.sender_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create Message from dictionary.

        Args:
            data: Dictionary containing message data.

        Returns:
            Message instance.
        """
        return cls(
            msg_type=MessageType(data['msg_type']),
            payload=data['payload'],
            sender_id=data.get('sender_id')
        )


class Serializer:
    """
    Handles message serialization and deserialization.

    Supports both JSON and Pickle formats. JSON is preferred for
    interoperability, while Pickle can handle more complex Python objects.
    """

    @staticmethod
    def serialize_json(message: Message) -> bytes:
        """
        Serialize message to JSON format.

        Args:
            message: Message instance to serialize.

        Returns:
            JSON-encoded bytes with length prefix.
        """
        msg_dict = message.to_dict()
        json_str = json.dumps(msg_dict)
        json_bytes = json_str.encode('utf-8')
        # Prefix with 4-byte length header
        length = len(json_bytes)
        return length.to_bytes(4, byteorder='big') + json_bytes

    @staticmethod
    def deserialize_json(data: bytes) -> Message:
        """
        Deserialize JSON-encoded message.

        Args:
            data: JSON-encoded bytes (without length prefix).

        Returns:
            Message instance.
        """
        json_str = data.decode('utf-8')
        msg_dict = json.loads(json_str)
        return Message.from_dict(msg_dict)

    @staticmethod
    def serialize_pickle(message: Message) -> bytes:
        """
        Serialize message using Pickle format.

        Args:
            message: Message instance to serialize.

        Returns:
            Pickle-encoded bytes with length prefix.
        """
        pickled = pickle.dumps(message)
        length = len(pickled)
        return length.to_bytes(4, byteorder='big') + pickled

    @staticmethod
    def deserialize_pickle(data: bytes) -> Message:
        """
        Deserialize Pickle-encoded message.

        Args:
            data: Pickle-encoded bytes (without length prefix).

        Returns:
            Message instance.
        """
        return pickle.loads(data)

    @staticmethod
    def serialize(message: Message, use_json: bool = True) -> bytes:
        """
        Serialize message using specified format.

        Args:
            message: Message instance to serialize.
            use_json: If True, use JSON; otherwise use Pickle.

        Returns:
            Serialized bytes with length prefix.
        """
        if use_json:
            return Serializer.serialize_json(message)
        else:
            return Serializer.serialize_pickle(message)

    @staticmethod
    def deserialize(data: bytes, use_json: bool = True) -> Message:
        """
        Deserialize message from specified format.

        Args:
            data: Serialized bytes (without length prefix).
            use_json: If True, expect JSON; otherwise expect Pickle.

        Returns:
            Message instance.
        """
        if use_json:
            return Serializer.deserialize_json(data)
        else:
            return Serializer.deserialize_pickle(data)
