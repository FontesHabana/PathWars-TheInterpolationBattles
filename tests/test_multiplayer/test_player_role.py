"""
Unit tests for PlayerRole.
"""

import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from multiplayer.player_role import PlayerRole


class TestPlayerRole:
    """Tests for PlayerRole enum."""
    
    def test_host_opponent_is_client(self):
        """Test that HOST's opponent is CLIENT."""
        assert PlayerRole.HOST.opponent() == PlayerRole.CLIENT
    
    def test_client_opponent_is_host(self):
        """Test that CLIENT's opponent is HOST."""
        assert PlayerRole.CLIENT.opponent() == PlayerRole.HOST
    
    def test_opponent_is_symmetric(self):
        """Test that opponent relationship is symmetric."""
        host = PlayerRole.HOST
        client = PlayerRole.CLIENT
        assert host.opponent().opponent() == host
        assert client.opponent().opponent() == client


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
