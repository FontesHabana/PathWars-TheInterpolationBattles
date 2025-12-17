# Network Core System

This module implements the TCP socket-based networking layer for PathWars multiplayer communication.

## Features

- **TCP Socket Communication**: Reliable host/client connections
- **Observer Pattern**: Event-driven message handling
- **Non-blocking I/O**: Uses `selectors` and threading for efficient message receiving
- **Multiple Serialization Formats**: Support for both JSON (interoperable) and Pickle (Python-native)
- **Type-Safe Messages**: Dataclass-based message structures with type hints
- **Secure by Default**: Binds to localhost (127.0.0.1) by default

## Architecture

The network module follows SOLID principles with clear separation of concerns:

```
network/
├── protocol.py    # Message structures and serialization (Protocol Layer)
├── manager.py     # Connection handling and I/O (Transport Layer)
└── __init__.py    # Package exports
```

### Protocol Layer (`protocol.py`)

- **MessageType**: Enum defining message types (handshake, route_data, game_state, etc.)
- **Message**: Dataclass for type-safe message structures
- **Serializer**: Handles JSON/Pickle serialization with length-prefixed framing

### Transport Layer (`manager.py`)

- **NetworkManager**: Manages TCP socket connections
  - Singleton pattern ensures single connection per process
  - Observer pattern for event callbacks
  - Non-blocking receives in background thread
  - Automatic message framing and deserialization

## Usage

### Basic Host/Client Setup

```python
from network import NetworkManager, Message, MessageType

# Host (Server)
host = NetworkManager()

# Register observer for incoming messages
def on_message(msg: Message):
    print(f"Received: {msg.payload}")

host.register_observer(MessageType.ROUTE_DATA, on_message)

# Start listening (defaults to localhost for security)
host.start_host(port=5555, bind_address='127.0.0.1')

# Send a message
msg = Message(
    msg_type=MessageType.GAME_STATE,
    payload={'hp': 100, 'money': 500}
)
host.send(msg)

# Client
client = NetworkManager()
client.register_observer(MessageType.GAME_STATE, on_message)
client.connect_to_host('127.0.0.1', port=5555)
```

### Message Types

The protocol defines the following message types:

- `HANDSHAKE`: Initial connection greeting
- `ROUTE_DATA`: Path interpolation data (control points, method)
- `GAME_STATE`: Game state synchronization (HP, money, phase)
- `TOWER_PLACEMENT`: Tower construction events
- `DISCONNECT`: Clean disconnection
- `ACK`: Acknowledgments

### Security Considerations

**Important**: The default `bind_address` is `127.0.0.1` (localhost only) for security.

For LAN multiplayer, explicitly set `bind_address='0.0.0.0'`:

```python
# Allow connections from any network interface (LAN/WAN)
host.start_host(port=5555, bind_address='0.0.0.0')
```

⚠️ **Warning**: Binding to `0.0.0.0` exposes the server to all network interfaces. Only use this in trusted LAN environments.

## Example

See `examples/network_example.py` for a complete working example:

```bash
# Terminal 1 - Host
python examples/network_example.py

# Terminal 2 - Client
python examples/network_example.py client
```

## Testing

The module includes comprehensive unit tests:

```bash
# Run network tests only
pytest tests/test_network.py -v

# Run all tests
pytest tests/ -v
```

Test coverage includes:
- Protocol serialization/deserialization
- NetworkManager with mocked sockets
- Full integration tests with real sockets
- Bidirectional communication

## Design Patterns

### Observer Pattern
The NetworkManager uses the Observer pattern to decouple network I/O from game logic:

```python
# Register callbacks for specific message types
nm.register_observer(MessageType.TOWER_PLACEMENT, on_tower_placed)
nm.register_observer(MessageType.ROUTE_DATA, on_route_received)
```

### Singleton Pattern
NetworkManager implements the Singleton pattern to prevent multiple network connections:

```python
nm1 = NetworkManager()
nm2 = NetworkManager()
assert nm1 is nm2  # Same instance
```

## API Reference

### NetworkManager

#### Methods

- `start_host(port=5555, bind_address='127.0.0.1') -> bool`
  - Start as host and listen for connections
  - Returns True if successful

- `connect_to_host(ip, port=5555, timeout=10) -> bool`
  - Connect to a host as client
  - Returns True if successful

- `send(message: Message) -> bool`
  - Send a message to the connected peer
  - Returns True if successful

- `close()`
  - Close connection and cleanup resources

- `register_observer(msg_type: MessageType, callback: Callable)`
  - Register a callback for a specific message type

- `unregister_observer(msg_type: MessageType)`
  - Remove a callback for a message type

- `is_connected() -> bool`
  - Check if currently connected

- `get_role() -> Optional[str]`
  - Get current role ('host' or 'client')

### Message

#### Attributes

- `msg_type: MessageType` - Type of message
- `payload: Dict[str, Any]` - Message data
- `sender_id: Optional[str]` - Sender identifier

#### Methods

- `to_dict() -> Dict` - Convert to dictionary
- `from_dict(data: Dict) -> Message` - Create from dictionary

### Serializer

#### Methods

- `serialize(message: Message, use_json=True) -> bytes`
  - Serialize message with length prefix

- `deserialize(data: bytes, use_json=True) -> Message`
  - Deserialize message (without length prefix)

## Performance Considerations

- Non-blocking I/O using `selectors` module
- Background thread for receives (no blocking on game loop)
- Length-prefixed framing prevents partial message reads
- Efficient JSON serialization for most messages
- Pickle available for complex Python objects if needed

## Future Enhancements

Potential improvements for future versions:

- Message compression for large payloads
- Encryption support (TLS/SSL)
- Message acknowledgment and retry logic
- Connection timeout and automatic reconnection
- Rate limiting and flood protection
- Multiple client support (broadcast messages)
