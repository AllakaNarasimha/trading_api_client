"""
Watchdog class for monitoring operations and key updates.
Restarts program on timeouts or idle periods based on retry config.
"""

import threading
import time
import logging
from typing import Any, Optional, Dict

from .program_manager import ProgramManager
from .config import Config


class Watchdog:
    """
    Watchdog that monitors operations and key updates, restarting program on timeouts or idle periods.
    """

    def __init__(self, logger: Optional[logging.Logger] = None, test_mode: bool = False):
        self.logger = logger or logging.getLogger(__name__)
        self.program_manager = ProgramManager(logger=self.logger)
        self.config = Config()

        # Key monitoring state
        self.key_last_updates: Dict[str, float] = {}
        self.idle_monitor_timer: Optional[threading.Timer] = None
        self.is_monitoring_idle = False
        
        # Test mode flag
        self.test_mode = test_mode
        self.restart_triggered = False

        self.logger.info("Watchdog initialized")

    def update_key(self, key: str) -> None:
        """Update the last update timestamp for a key."""
        self.key_last_updates[key] = time.time()
        self.logger.debug(f"Updated key '{key}'")

    def start_idle_monitoring(self) -> None:
        """Start monitoring for idle keys that exceed the timeout period."""
        if self.is_monitoring_idle:
            return

        self.is_monitoring_idle = True
        self.logger.info(f"Starting idle monitoring (timeout: {self.config.RETRY_IDLE_TIMEOUT}s)")

        def check_idle():
            if not self.is_monitoring_idle:
                return

            current_time = time.time()
            stale_keys = [(k, current_time - t) for k, t in self.key_last_updates.items()
                         if current_time - t > self.config.RETRY_IDLE_TIMEOUT]

            if stale_keys:
                self.logger.error(f"IDLE TIMEOUT: {len(stale_keys)} key(s) stale")
                for key, age in stale_keys:
                    self.logger.error(f"  '{key}': {age:.1f}s old")
                self.is_monitoring_idle = False
                if self.test_mode:
                    self.restart_triggered = True
                else:
                    self.program_manager.restart_current_program(delay=2)
            else:
                self.idle_monitor_timer = threading.Timer(self.config.RETRY_IDLE_TIMEOUT / 4, check_idle)
                self.idle_monitor_timer.daemon = True
                self.idle_monitor_timer.start()

        self.idle_monitor_timer = threading.Timer(self.config.RETRY_IDLE_TIMEOUT / 4, check_idle)
        self.idle_monitor_timer.daemon = True
        self.idle_monitor_timer.start()

    def stop_idle_monitoring(self) -> None:
        """Stop idle monitoring."""
        if self.idle_monitor_timer and self.idle_monitor_timer.is_alive():
            self.idle_monitor_timer.cancel()
        self.is_monitoring_idle = False
        self.logger.info("Idle monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current watchdog status."""
        current_time = time.time()
        key_status = {
            k: {
                'age': current_time - t,
                'stale': current_time - t > self.config.RETRY_IDLE_TIMEOUT
            } for k, t in self.key_last_updates.items()
        }

        return {
            'is_monitoring_idle': self.is_monitoring_idle,
            'keys': key_status,
            'idle_timeout': self.config.RETRY_IDLE_TIMEOUT
        }

    def cleanup(self):
        """Clean up watchdog resources."""
        self.stop_idle_monitoring()
        self.logger.info("Watchdog cleanup complete")