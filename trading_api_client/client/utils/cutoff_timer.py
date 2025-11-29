"""
CutoffTimer Module

Provides a timer mechanism to schedule automatic shutdown at a specified time.
"""

import datetime
import logging
import os
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class CutoffTimer:
    """
    Schedule a one-shot stop at a given HH:MM (24h).
    Call start() once after your app is initialized.
    When cutoff is reached, `on_cutoff` is called.
    """

    def __init__(self, end_hour: int, end_minute: int, on_cutoff: Optional[Callable] = None):
        """Initialize CutoffTimer.
        
        Args:
            end_hour: Hour (0-23) in 24-hour format
            end_minute: Minute (0-59)
            on_cutoff: Callback function to execute when cutoff is reached.
                      Defaults to exiting the process.
        """
        self.end_hour = end_hour
        self.end_minute = end_minute
        self._timer: Optional[threading.Timer] = None

        # Default action: exit process
        if on_cutoff is None:
            self.on_cutoff = self._default_on_cutoff
        else:
            self.on_cutoff = on_cutoff

    def _seconds_until_cutoff(self) -> float:
        """Calculate seconds remaining until cutoff time.
        
        Returns:
            float: Seconds until cutoff. 0 if cutoff time has passed.
        """
        now = datetime.datetime.now()
        target = now.replace(
            hour=self.end_hour,
            minute=self.end_minute,
            second=0,
            microsecond=0
        )
        if target <= now:
            # already past cutoff -> 0 sec
            return 0.0
        delta = target - now
        return delta.total_seconds()

    def _default_on_cutoff(self) -> None:
        """Default cutoff action: exit gracefully."""
        logger.info("[CUTOFF] Cutoff time reached, exiting gracefully.")
        logger.info("[CUTOFF] Terminating all threads and exiting process...")
        
        os._exit(0)  # Force immediate process termination (kills all threads)

    def _fire(self) -> None:
        """Execute the cutoff callback."""
        logger.info("[CUTOFF] Cutoff timer fired, executing callback...")
        self.on_cutoff()

    def start(self) -> None:
        """Start the cutoff timer.
        
        Schedules a timer that will trigger the cutoff callback
        at the specified time.
        """
        delay = self._seconds_until_cutoff()
        logger.info(f"[CUTOFF] Checking cutoff time: {self.end_hour:02d}:{self.end_minute:02d}")
        logger.info(f"[CUTOFF] Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"[CUTOFF] Seconds until cutoff: {delay:.0f}")
        
        if delay > 0:
            self._timer = threading.Timer(delay, self._fire)
            self._timer.daemon = False  # Important: must not be daemon so cutoff still fires
            self._timer.start()
            logger.info(f"[CUTOFF] Timer scheduled for {self.end_hour:02d}:{self.end_minute:02d} (in {delay:.0f} seconds)")
        else:
            logger.warning(f"[CUTOFF] Cutoff time {self.end_hour:02d}:{self.end_minute:02d} has already passed")

    def cancel(self) -> None:
        """Cancel the cutoff timer if it's running."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
            logger.info("[CUTOFF] Cutoff timer cancelled")
        else:
            logger.debug("[CUTOFF] No cutoff timer to cancel")   
    