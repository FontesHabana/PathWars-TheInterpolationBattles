"""
Example usage of the Network Core System.

This script demonstrates how to use the NetworkManager for host/client communication.
Run two instances of this script - one as host, one as client.
"""

import sys
import time
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from network import NetworkManager, Message, MessageType


def run_host():
    """Example host implementation."""
    print("=== Starting as HOST ===")

    nm = NetworkManager()

    # Register observer for incoming messages
    def on_route_data(msg: Message):
        print(f"Received route data: {msg.payload}")
        # Send acknowledgment
        ack = Message(
            msg_type=MessageType.ACK,
            payload={'status': 'received', 'timestamp': time.time()}
        )
        nm.send(ack)

    nm.register_observer(MessageType.ROUTE_DATA, on_route_data)

    # Start host (use '0.0.0.0' for LAN access, or '127.0.0.1' for localhost only)
    print("Starting host on 127.0.0.1:5555...")
    if nm.start_host(port=5555, bind_address='127.0.0.1'):
        print("Client connected!")

        # Send a handshake message
        handshake = Message(
            msg_type=MessageType.HANDSHAKE,
            payload={'player_name': 'Host Player', 'version': '1.0'}
        )
        nm.send(handshake)

        # Keep alive for 10 seconds
        print("Host running... (will close in 10 seconds)")
        time.sleep(10)

        nm.close()
        print("Host closed")
    else:
        print("Failed to start host")


def run_client():
    """Example client implementation."""
    print("=== Starting as CLIENT ===")

    nm = NetworkManager()

    # Register observer for incoming messages
    def on_handshake(msg: Message):
        print(f"Received handshake: {msg.payload}")

    def on_ack(msg: Message):
        print(f"Received acknowledgment: {msg.payload}")

    nm.register_observer(MessageType.HANDSHAKE, on_handshake)
    nm.register_observer(MessageType.ACK, on_ack)

    # Connect to host
    print("Connecting to host at 127.0.0.1:5555...")
    if nm.connect_to_host('127.0.0.1', port=5555):
        print("Connected to host!")

        # Wait a bit for handshake
        time.sleep(1)

        # Send route data
        route_msg = Message(
            msg_type=MessageType.ROUTE_DATA,
            payload={
                'points': [[0, 0], [5, 5], [10, 10]],
                'method': 'cubic_spline'
            }
        )
        nm.send(route_msg)
        print("Sent route data")

        # Keep alive for 8 seconds
        print("Client running... (will close in 8 seconds)")
        time.sleep(8)

        nm.close()
        print("Client closed")
    else:
        print("Failed to connect to host")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        run_client()
    else:
        print("Usage:")
        print("  Host:   python network_example.py")
        print("  Client: python network_example.py client")
        print()
        if len(sys.argv) == 1:
            run_host()
