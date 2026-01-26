#!/usr/bin/env python3
"""
Comprehensive test script for Watchdog functionality.
Tests both operation timeout and idle monitoring features.
"""

import time
import sys
import os
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from client.utils.watchdog import Watchdog

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def test_idle_monitoring():
    """Test idle monitoring functionality."""
    logger.info("=" * 60)
    logger.info("TESTING IDLE MONITORING FUNCTIONALITY")
    logger.info("=" * 60)

    # Check if this is an idle restart
    if len(sys.argv) > 1 and sys.argv[1] == "--idle-restart":
        logger.info("SUCCESS: Program restarted by idle monitoring!")
        return True

    # Create watchdog with short idle timeout for testing
    watchdog = Watchdog(logger=logger, test_mode=True)
    watchdog.config.RETRY_IDLE_TIMEOUT = 8.0  # Short timeout for testing
    logger.info(f"Set idle timeout to {watchdog.config.RETRY_IDLE_TIMEOUT}s for testing")

    # Update keys and start monitoring
    logger.info("Updating keys and starting idle monitoring...")
    watchdog.update_key("price_data")
    watchdog.update_key("order_book")

    # Start idle monitoring
    watchdog.start_idle_monitoring()
    logger.info("Idle monitoring started")

    # Wait for idle timeout (should trigger restart flag after 8 seconds)
    logger.info("Waiting for idle timeout to trigger restart flag...")
    time.sleep(10)  # Wait longer than idle timeout

    # Check if restart was triggered
    if watchdog.restart_triggered:
        logger.info("SUCCESS: Idle monitoring triggered restart flag!")
        return True
    else:
        logger.error("FAIL: Idle monitoring did not trigger restart flag!")
        return False


def test_success_cases():
    """Test successful key monitoring functionality."""
    logger.info("=" * 60)
    logger.info("TESTING SUCCESS CASES")
    logger.info("=" * 60)

    watchdog = Watchdog(logger=logger, test_mode=True)

    try:
        # Test key updates
        watchdog.update_key("test_key")
        watchdog.update_key("price_data")
        status = watchdog.get_status()
        logger.info(f"SUCCESS: Key monitoring works - {len(status['keys'])} keys tracked")
        
        # Verify status structure
        assert 'is_monitoring_idle' in status
        assert 'keys' in status
        assert 'idle_timeout' in status
        logger.info("SUCCESS: Status structure is correct")

        return True
    except Exception as e:
        logger.error(f"FAIL: Success test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting watchdog tests...")

    # Run tests
    success_count = 0
    total_tests = 0

    # Test idle monitoring
    total_tests += 1
    if test_idle_monitoring():
        success_count += 1

    # Test success cases
    total_tests += 1
    if test_success_cases():
        success_count += 1

    logger.info("=" * 60)
    logger.info(f"TEST RESULTS: {success_count}/{total_tests} tests passed")
    logger.info("=" * 60)

    if success_count == total_tests:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Some tests failed!")
        sys.exit(1)