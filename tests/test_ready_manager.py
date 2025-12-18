"""
Tests for ReadyManager module.

Tests ready state management, timer functionality, and observer pattern.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.ready_manager import ReadyManager, ReadyTrigger


class TestReadyManagerInitialization:
    """Tests for ReadyManager initialization."""

    def test_initial_state(self):
        """Test ReadyManager initializes with correct defaults."""
        manager = ReadyManager()
        
        assert manager.player_count == 1
        assert manager.ready_timeout == 60.0
        assert manager.is_active is False
        assert manager.ready_count == 0
        assert manager.all_ready is False
        assert manager.time_remaining == 0.0

    def test_custom_player_count(self):
        """Test ReadyManager with custom player count."""
        manager = ReadyManager(player_count=4)
        
        assert manager.player_count == 4

    def test_custom_timeout(self):
        """Test ReadyManager with custom timeout."""
        manager = ReadyManager(ready_timeout=120.0)
        
        assert manager.ready_timeout == 120.0

    def test_player_count_minimum_is_one(self):
        """Test that player count is clamped to minimum of 1."""
        manager = ReadyManager(player_count=0)
        assert manager.player_count == 1
        
        manager2 = ReadyManager(player_count=-5)
        assert manager2.player_count == 1

    def test_timeout_minimum_is_zero(self):
        """Test that timeout is clamped to minimum of 0."""
        manager = ReadyManager(ready_timeout=-10.0)
        assert manager.ready_timeout == 0.0


class TestReadyManagerStart:
    """Tests for ReadyManager start method."""

    def test_start_activates_manager(self):
        """Test that start() activates the manager."""
        manager = ReadyManager()
        manager.start()
        
        assert manager.is_active is True

    def test_start_clears_ready_players(self):
        """Test that start() clears ready player list."""
        manager = ReadyManager(player_count=2)
        manager.start()
        manager.set_ready(1)
        
        manager.start()  # Start again
        
        assert manager.ready_count == 0

    def test_start_initializes_timer(self):
        """Test that start() initializes the timer."""
        manager = ReadyManager(ready_timeout=30.0)
        manager.start()
        
        assert manager.time_remaining == 30.0


class TestReadyManagerStop:
    """Tests for ReadyManager stop method."""

    def test_stop_deactivates_manager(self):
        """Test that stop() deactivates the manager."""
        manager = ReadyManager()
        manager.start()
        manager.stop()
        
        assert manager.is_active is False

    def test_stop_clears_state(self):
        """Test that stop() clears ready players and timer."""
        manager = ReadyManager(player_count=2, ready_timeout=30.0)
        manager.start()
        manager.set_ready(1)
        
        manager.stop()
        
        assert manager.ready_count == 0
        assert manager.time_remaining == 0.0


class TestReadyManagerSetReady:
    """Tests for setting player ready state."""

    def test_set_ready_increases_count(self):
        """Test that set_ready increases ready count."""
        manager = ReadyManager(player_count=2)
        manager.start()
        
        manager.set_ready(1)
        
        assert manager.ready_count == 1
        assert manager.is_player_ready(1) is True

    def test_set_ready_returns_true_on_change(self):
        """Test that set_ready returns True when state changes."""
        manager = ReadyManager()
        manager.start()
        
        result = manager.set_ready(1)
        
        assert result is True

    def test_set_ready_returns_false_if_already_ready(self):
        """Test that set_ready returns False if already ready."""
        manager = ReadyManager()
        manager.start()
        manager.set_ready(1)
        
        result = manager.set_ready(1)
        
        assert result is False

    def test_set_ready_returns_false_if_not_active(self):
        """Test that set_ready returns False if manager not active."""
        manager = ReadyManager()
        
        result = manager.set_ready(1)
        
        assert result is False
        assert manager.ready_count == 0

    def test_is_player_ready(self):
        """Test is_player_ready method."""
        manager = ReadyManager(player_count=2)
        manager.start()
        
        assert manager.is_player_ready(1) is False
        
        manager.set_ready(1)
        
        assert manager.is_player_ready(1) is True
        assert manager.is_player_ready(2) is False


class TestReadyManagerSetUnready:
    """Tests for setting player unready state."""

    def test_set_unready_decreases_count(self):
        """Test that set_unready decreases ready count."""
        manager = ReadyManager(player_count=2)
        manager.start()
        manager.set_ready(1)
        manager.set_ready(2)
        
        manager.set_unready(1)
        
        assert manager.ready_count == 1
        assert manager.is_player_ready(1) is False
        assert manager.is_player_ready(2) is True

    def test_set_unready_returns_true_on_change(self):
        """Test that set_unready returns True when state changes."""
        manager = ReadyManager()
        manager.start()
        manager.set_ready(1)
        
        result = manager.set_unready(1)
        
        assert result is True

    def test_set_unready_returns_false_if_not_ready(self):
        """Test that set_unready returns False if not ready."""
        manager = ReadyManager()
        manager.start()
        
        result = manager.set_unready(1)
        
        assert result is False


class TestReadyManagerAllReady:
    """Tests for all_ready property and triggering."""

    def test_all_ready_single_player(self):
        """Test all_ready with single player."""
        manager = ReadyManager(player_count=1)
        manager.start()
        
        assert manager.all_ready is False
        
        manager.set_ready(1)
        
        assert manager.all_ready is True

    def test_all_ready_two_players(self):
        """Test all_ready with multiple players."""
        manager = ReadyManager(player_count=2)
        manager.start()
        
        manager.set_ready(1)
        assert manager.all_ready is False
        
        manager.set_ready(2)
        assert manager.all_ready is True

    def test_all_ready_triggers_callback(self):
        """Test that reaching all_ready triggers callback."""
        manager = ReadyManager(player_count=2)
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.start()
        manager.set_ready(1)
        manager.set_ready(2)
        
        assert len(triggered) == 1
        assert triggered[0] == ReadyTrigger.ALL_READY

    def test_callback_not_triggered_twice(self):
        """Test that callback is not triggered multiple times."""
        manager = ReadyManager(player_count=1)
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.start()
        manager.set_ready(1)
        
        # Try to set ready again (should not trigger)
        manager.set_ready(1)
        
        assert len(triggered) == 1


class TestReadyManagerTimer:
    """Tests for timer functionality."""

    def test_time_remaining_decreases(self):
        """Test that time_remaining decreases with update."""
        manager = ReadyManager(ready_timeout=30.0)
        manager.start()
        
        manager.update(1.0)
        
        assert manager.time_remaining == 29.0
        
        manager.update(5.0)
        
        assert manager.time_remaining == 24.0

    def test_timer_expiration_triggers_callback(self):
        """Test that timer expiration triggers callback."""
        manager = ReadyManager(ready_timeout=5.0)
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.start()
        
        manager.update(6.0)
        
        assert len(triggered) == 1
        assert triggered[0] == ReadyTrigger.TIMER_EXPIRED

    def test_timer_disabled_with_zero_timeout(self):
        """Test that timer with 0 timeout never expires."""
        manager = ReadyManager(ready_timeout=0.0)
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.start()
        
        manager.update(100.0)
        
        assert len(triggered) == 0
        assert manager.is_active is True


class TestReadyManagerForceReady:
    """Tests for force_ready functionality."""

    def test_force_ready_triggers_immediately(self):
        """Test that force_ready triggers callback immediately."""
        manager = ReadyManager(player_count=2)
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.start()
        
        manager.force_ready()
        
        assert len(triggered) == 1
        assert triggered[0] == ReadyTrigger.FORCED

    def test_force_ready_deactivates_manager(self):
        """Test that force_ready deactivates the manager."""
        manager = ReadyManager()
        manager.start()
        
        manager.force_ready()
        
        assert manager.is_active is False


class TestReadyManagerObservers:
    """Tests for observer pattern."""

    def test_subscribe_adds_callback(self):
        """Test that subscribe adds a callback."""
        manager = ReadyManager()
        
        def callback(trigger):
            pass
        
        manager.subscribe(callback)
        manager.start()
        manager.force_ready()
        
        # If subscribed correctly, this won't crash

    def test_unsubscribe_removes_callback(self):
        """Test that unsubscribe removes a callback."""
        manager = ReadyManager()
        
        triggered = []
        def callback(trigger):
            triggered.append(trigger)
        
        manager.subscribe(callback)
        manager.unsubscribe(callback)
        manager.start()
        manager.force_ready()
        
        assert len(triggered) == 0

    def test_multiple_observers(self):
        """Test multiple observers receive callbacks."""
        manager = ReadyManager()
        
        triggered1 = []
        triggered2 = []
        
        def callback1(trigger):
            triggered1.append(trigger)
        
        def callback2(trigger):
            triggered2.append(trigger)
        
        manager.subscribe(callback1)
        manager.subscribe(callback2)
        manager.start()
        manager.force_ready()
        
        assert len(triggered1) == 1
        assert len(triggered2) == 1


class TestReadyManagerReset:
    """Tests for reset functionality."""

    def test_reset_clears_all_state(self):
        """Test that reset clears all state."""
        manager = ReadyManager(player_count=2, ready_timeout=30.0)
        manager.start()
        manager.set_ready(1)
        
        manager.reset()
        
        assert manager.is_active is False
        assert manager.ready_count == 0
        assert manager.time_remaining == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
