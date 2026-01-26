"""
Health Check Monitor - Generic monitoring logic for restarting processes.
Can be used to monitor any thread or process and restart it if it stops.
"""

import logging
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)

class HealthCheckMonitor:
    """
    Generic health check monitor that periodically checks if a process is running
    and restarts it if not. Designed to be reusable across different monitoring scenarios.
    """

    def __init__(self, check_function: Callable[[], bool], restart_function: Callable[[], None],
                 interval: int = 300, name: str = "health_check"):
        """
        Initialize the health check monitor.

        Args:
            check_function: Callable that returns True if the monitored process is running
            restart_function: Callable to restart the monitored process
            interval: Time in seconds between health checks (default 5 minutes)
            name: Name for logging purposes
        """
        self.check_function = check_function
        self.restart_function = restart_function
        self.interval = interval
        self.name = name

        self.thread: threading.Thread = None
        self.stop_event = threading.Event()

    def start(self) -> None:
        """Start the health check monitoring thread."""
        if self.thread and self.thread.is_alive():
            logger.info(f"{self.name} monitor already running")
            return

        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._monitor_loop,
            daemon=False,
            name=self.name
        )
        self.thread.start()
        logger.info(f"[THREAD START] {self.name} monitor started (ID: {self.thread.ident}, interval: {self.interval}s)")

    def stop(self) -> None:
        """Stop the health check monitoring thread."""
        if not self.thread or not self.thread.is_alive():
            logger.info(f"{self.name} monitor not running")
            return

        logger.info(f"[THREAD STOP] Stopping {self.name} monitor...")
        self.stop_event.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            logger.warning(f"[THREAD TIMEOUT] {self.name} monitor did not stop gracefully after 5s")
        else:
            logger.info(f"[THREAD STOPPED] {self.name} monitor stopped successfully")

    def _monitor_loop(self) -> None:
        """Main monitoring loop that runs in a separate thread."""
        logger.info(f"{self.name} monitor thread is now running")

        while not self.stop_event.is_set():
            try:
                # Wait for the configured interval
                if self.stop_event.wait(timeout=self.interval):
                    # Stop event was set, exit gracefully
                    break

                # Check if the monitored process is still running
                if not self.check_function():
                    logger.warning(f"{self.name}: Monitored process stopped unexpectedly! Restarting...")
                    try:
                        self.restart_function()
                        logger.info(f"{self.name}: Process restarted successfully")
                    except Exception as restart_error:
                        logger.error(f"{self.name}: Failed to restart process: {restart_error}", exc_info=True)
                else:
                    logger.debug(f"{self.name}: Process is running normally")

            except Exception as e:
                logger.error(f"{self.name}: Health check error: {e}", exc_info=True)

        logger.info(f"[THREAD STOPPED] {self.name} monitor thread stopped gracefully")