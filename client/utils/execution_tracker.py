"""Execution tracker for managing one-time or periodic task execution.

Tracks when tasks were last executed to prevent duplicate runs.
Stores execution history and configuration in temp files.
Detects configuration changes and forces re-execution if needed.
"""

import os
import json
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from pathlib import Path


class ExecutionTracker:
    """Track execution of tasks and detect configuration changes."""
    
    TEMP_DIR = Path(os.path.expanduser("~")) / ".trading_api_client_temp"
    
    def __init__(self, task_name: str):
        """Initialize tracker for a specific task.
        
        Args:
            task_name: Name of the task (e.g., 'history_data_fetch')
        """
        self.task_name = task_name
        self.tracker_file = self.TEMP_DIR / f".{task_name}_last_run"
        self.logger = self._setup_logger()
        self._ensure_temp_dir()
        self.logger.info(f"Initialized ExecutionTracker for task: {task_name}")
        self.logger.info(f"Tracker file path: {self.tracker_file}")
    
    @classmethod
    def _ensure_temp_dir(cls):
        """Ensure temp directory exists."""
        cls.TEMP_DIR.mkdir(exist_ok=True, parents=True)
    
    def _setup_logger(self):
        """Setup logger for execution tracker."""
        logger_name = f"execution_tracker.{self.task_name}"
        logger = logging.getLogger(logger_name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        log_file = logs_dir / f"execution_tracker_{self.task_name}.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB, 5 backups
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _compute_config_hash(self, config_dict: dict) -> str:
        """Compute hash of configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary to hash
        
        Returns:
            str: SHA256 hash of the configuration
        """
        if not config_dict:
            return ""
        
        try:
            # Sort keys for consistent hashing
            config_str = json.dumps(config_dict, sort_keys=True, default=str)
            return hashlib.sha256(config_str.encode()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to compute config hash: {e}")
            return ""
    
    def record_execution(self, config: dict = None) -> None:
        """Record that a task was executed now.
        
        Args:
            config: Configuration dictionary to store with execution record
        """
        config_hash = self._compute_config_hash(config) if config else ""
        
        execution_data = {
            'task_name': self.task_name,
            'last_run': datetime.now().isoformat(),
            'timestamp': datetime.now().timestamp(),
            'config_hash': config_hash,
            'config': config if config else {}
        }
        
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(execution_data, f, indent=2)
            self.logger.info(f"Recorded execution for task: {self.task_name}")
        except Exception as e:
            self.logger.warning(f"Failed to record execution for {self.task_name}: {e}")
    
    def get_last_execution(self) -> dict:
        """Get last execution details.
        
        Returns:
            dict: Execution data with 'last_run', 'timestamp', and 'config_hash' keys, or empty dict if never run
        """

        if not self.tracker_file.exists():
            return {}
        
        try:
            with open(self.tracker_file, 'r') as f:
                data = json.load(f)
            self.logger.debug(f"Retrieved execution data for task: {self.task_name}")
            return data
        except Exception as e:
            self.logger.warning(f"Failed to read execution data for {self.task_name}: {e}")
            return {}
    
    def config_has_changed(self, current_config: dict) -> bool:
        """Check if configuration has changed since last execution.
        
        Args:
            current_config: Current configuration dictionary
        
        Returns:
            bool: True if config changed or never run before, False if config is same
        """
        execution = self.get_last_execution()
        if not execution:
            self.logger.info(f"No previous execution found for task: {self.task_name}")
            return True  # No previous execution, config is "new"
        
        try:
            stored_hash = execution.get('config_hash', '')
            current_hash = self._compute_config_hash(current_config)
            
            # If hashes are empty or don't match, config changed
            if not stored_hash or not current_hash:
                self.logger.info(f"Config hash missing or empty for task: {self.task_name}")
                return True
            
            changed = stored_hash != current_hash
            if changed:
                self.logger.info(f"Configuration changed for task: {self.task_name}")
            else:
                self.logger.debug(f"Configuration unchanged for task: {self.task_name}")
            
            return changed
        except Exception as e:
            self.logger.warning(f"Failed to check config change: {e}")
            return True  # On error, assume config changed to be safe
    
    def get_stored_config(self) -> dict:
        """Get the stored configuration from last execution.
        
        Returns:
            dict: Stored configuration, or empty dict if never run
        """
        execution = self.get_last_execution()
        return execution.get('config', {})
    
    def has_run_today(self) -> bool:
        """Check if task ran today.
        
        Returns:
            bool: True if task executed today, False otherwise
        """
        execution = self.get_last_execution()
        if not execution:
            return False
        
        try:
            last_run = datetime.fromisoformat(execution['last_run'])
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return last_run >= today
        except Exception as e:
            self.logger.warning(f"Failed to check execution date: {e}")
            return False
    
    def has_run_since(self, hours: int = 24) -> bool:
        """Check if task ran within the last N hours.
        
        Args:
            hours: Number of hours to check (default: 24)
        
        Returns:
            bool: True if task ran within the time period, False otherwise
        """
        execution = self.get_last_execution()
        if not execution:
            return False
        
        try:
            last_run = datetime.fromisoformat(execution['last_run'])
            cutoff = datetime.now() - timedelta(hours=hours)
            return last_run >= cutoff
        except Exception as e:
            self.logger.warning(f"Failed to check execution time: {e}")
            return False
    
    def should_run(self, check_today: bool = True, current_config: dict = None) -> bool:
        """Determine if task should run.
        
        Priority: Config change > Today check
        - If config changed: return True (force run)
        - If config same: check if already ran today
        
        Args:
            check_today: If True, check if already ran today. If False, check 24-hour window.
            current_config: Current configuration to check against stored config
        
        Returns:
            bool: True if task should run, False if already executed
        """
        # Check if config changed first (highest priority)
        if current_config and self.config_has_changed(current_config):
            self.logger.info(f"Task {self.task_name} should run due to config change")
            return True
        
        # Then check if already ran today
        if check_today:
            already_ran = self.has_run_today()
            should_run = not already_ran
            if should_run:
                self.logger.info(f"Task {self.task_name} should run (not run today)")
            else:
                self.logger.info(f"Task {self.task_name} should not run (already run today)")
            return should_run
        else:
            already_ran = self.has_run_since(hours=24)
            should_run = not already_ran
            if should_run:
                self.logger.info(f"Task {self.task_name} should run (not run in last 24 hours)")
            else:
                self.logger.info(f"Task {self.task_name} should not run (already run in last 24 hours)")
            return should_run
    
    def clear_history(self) -> None:
        """Clear execution history."""
        try:
            if self.tracker_file.exists():
                self.tracker_file.unlink()
                self.logger.info(f"Cleared execution history for task: {self.task_name}")
        except Exception as e:
            self.logger.warning(f"Failed to clear history for {self.task_name}: {e}")
    
    def get_days_since_execution(self) -> int:
        """Get number of days since last execution.
        
        Returns:
            int: Days since last execution, or -1 if never run
        """
        execution = self.get_last_execution()
        if not execution:
            return -1
        
        try:
            last_run = datetime.fromisoformat(execution['last_run'])
            days_diff = (datetime.now() - last_run).days
            return days_diff
        except Exception as e:
            self.logger.warning(f"Failed to calculate days since execution: {e}")
            return -1
