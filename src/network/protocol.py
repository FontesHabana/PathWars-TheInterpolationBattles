"""
Network Protocol Module.

Defines message structures and serialization for network communication.
Uses dataclasses for type safety and implements a Serializer class to abstract
the underlying serialization logic.
"""

import json
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class MessageType(Enum):
    """
    Enumeration of message types for network communication.
    """
    CONNECT = auto()
    DISCONNECT = auto()
    GAME_STATE = auto()
    PLAYER_ACTION = auto()
    CHAT = auto()
    PING = auto()
    PONG = auto()
    ERROR = auto()


@dataclass
class Message:
    """
    Generic message class for network communication.

    Attributes:
        msg_type: The type of message being sent.
        payload: The data payload of the message.
        sender_id: Optional identifier of the message sender.
        timestamp: Optional timestamp for the message.
    """
    msg_type: MessageType
    payload: Dict[str, Any] = field(default_factory=dict)
    sender_id: Optional[str] = None
    timestamp: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary representation.

        Returns:
            Dictionary containing all message fields.
        """
        return {
            "msg_type": self.msg_type.name,
            "payload": self.payload,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """
        Create a Message instance from a dictionary.

        Args:
            data: Dictionary containing message fields.

        Returns:
            A new Message instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If msg_type is invalid.
        """
        return cls(
            msg_type=MessageType[data["msg_type"]],
            payload=data.get("payload", {}),
            sender_id=data.get("sender_id"),
            timestamp=data.get("timestamp"),
        )


class BaseSerializer(ABC):
    """
    Abstract base class for message serialization.

    Defines the interface for serializing and deserializing messages.
    """

    @abstractmethod
    def serialize(self, message: Message) -> bytes:
        """
        Serialize a message to bytes.

        Args:
            message: The message to serialize.

        Returns:
            Byte representation of the message.
        """
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Message:
        """
        Deserialize bytes to a message.

        Args:
            data: The bytes to deserialize.

        Returns:
            A Message instance.
        """
        pass


class Serializer(BaseSerializer):
    """
    JSON-based message serializer with length-prefix framing.

    Uses a 4-byte big-endian integer prefix to indicate message length,
    followed by JSON-encoded message data.
    """

    HEADER_SIZE = 4  # 4 bytes for message length (big-endian)

    def serialize(self, message: Message) -> bytes:
        """
        Serialize a message to bytes with length prefix.

        Args:
            message: The message to serialize.

        Returns:
            Byte representation with 4-byte length prefix followed by JSON data.
        """
        json_data = json.dumps(message.to_dict()).encode("utf-8")
        length_prefix = struct.pack(">I", len(json_data))
        return length_prefix + json_data

    def deserialize(self, data: bytes) -> Message:
        """
        Deserialize bytes to a message (expects raw JSON data without prefix).

        Args:
            data: The JSON bytes to deserialize (without length prefix).

        Returns:
            A Message instance.

        Raises:
            json.JSONDecodeError: If data is not valid JSON.
            KeyError: If required message fields are missing.
            ValueError: If message type is invalid.
        """
        json_data = json.loads(data.decode("utf-8"))
        return Message.from_dict(json_data)

    def read_header(self, data: bytes) -> int:
        """
        Read the message length from header bytes.

        Args:
            data: 4-byte header data.

        Returns:
            The message length.

        Raises:
            struct.error: If data is not exactly 4 bytes.
        """
        return struct.unpack(">I", data)[0]
