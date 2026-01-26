import os
import sys
import subprocess
import time

from .utils.historical_data_fetcher import HistoricalDataFetcher
from .utils.execution_tracker import ExecutionTracker
from .utils.config import Config
from .utils.logger_manager import LoggerManager

class HistoryDataFetchController:
    # ============================================================================
    # Global Configuration Instance
    # ============================================================================

    config = Config()
    def __init__(self):
        self.config = Config()         
        self.cutoff_timer = None
        self._fetch_history_data_called = False
        self.logger = LoggerManager.setup_logging("history")
        self.history_data_fetcher = HistoricalDataFetcher()
        # Initialize execution tracker for historical data fetch
        self.execution_tracker = ExecutionTracker('history')

    def setup_logging(self, name: str = "history"):
        """Deprecated: Use LoggerManager.setup_logging() instead."""
        return LoggerManager.setup_logging(name)
    
    def _fetch_history_data(self):
        """Fetch live data after 5 second delay."""
        if not self._fetch_history_data_called:
            self._fetch_history_data_called = True
            try:
                self.logger.info("Waiting 5 seconds before fetching history data...")
                time.sleep(5)
                self.logger.info("Fetching history data...")
                self.history_data_fetcher.fetch_historical_data()
                self.logger.info("History data fetch completed")
                
                # Only update tracker config AFTER successful fetch
                history_config = {
                    'enabled': self.config.HISTORICAL_DATA_ENABLED,
                    'backdays': self.config.HISTORICAL_BACKDAYS,
                    'duration': self.config.HISTORICAL_DURATION,
                    'csv_export_enabled': self.config.HISTORICAL_CSV_EXPORT_ENABLED,
                    'symbols': self.config.HISTORICAL_SYMBOLS
                }
                self.execution_tracker.record_execution(config=history_config)
                self.logger.info("Execution tracker updated with new config")
                
                # Process will continue running after completion
                self.logger.info("Historical data fetch process completed successfully - keeping process alive")
            except Exception as e:
                self.logger.error(f"Error fetching history data: {e}", exc_info=True)

    
    def authorize_broker(self) -> bool:
        from .auth import get_auth_manager
        auth_manager = get_auth_manager()
        if auth_manager.is_authenticated:
            self.logger.info("Broker authorization successful")
            return True
        return False
    
    def _restart_app(self) -> None:
        """Restart the application using run_monitor.bat from config.dir after 10 second delay."""
        self.logger.info("Initiating app restart with 10 second delay...")
        try:
            # Get project root directory and read config.dir
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_dir_file = os.path.join(project_root, 'config.dir')
            
            configured_dir = project_root  # Default to project root
            if os.path.exists(config_dir_file):
                with open(config_dir_file, 'r') as f:
                    configured_dir = f.read().strip()
                self.logger.info(f"Read configured directory from config.dir: {configured_dir}")
            
            run_monitor_bat = os.path.join(configured_dir, 'run_monitor.bat')
            
            self.logger.info(f"Will restart using: {run_monitor_bat}")
            self.logger.info("Waiting 10 seconds before restart...")
            
            # Wait 10 seconds to allow graceful shutdown
            time.sleep(10)
            
            # Kill any existing Python processes
            self.logger.info("Killing existing Python processes...")
            subprocess.Popen('taskkill /f /im pythonw.exe /t 2>nul', shell=True)
            subprocess.Popen('taskkill /f /im python.exe /t 2>nul', shell=True)
            time.sleep(2)
            
            # Launch run_monitor.bat
            self.logger.info(f"Launching: {run_monitor_bat}")
            subprocess.Popen([run_monitor_bat], shell=True, cwd=configured_dir)
            
            # Exit current process
            self.logger.info("Exiting current process...")
            os._exit(0)
        except Exception as e:
            self.logger.error(f"Failed to restart app: {e}", exc_info=True)
        
    def run(self) -> None: 
        # Authorize broker before starting
        while self.authorize_broker() == False:
            time.sleep(5)
            self.logger.info("Retrying broker authorization...")    
        self.logger.info("Broker authorized successfully")
        
        try:
            # Build current history config
            history_config = {
                'enabled': self.config.HISTORICAL_DATA_ENABLED,
                'backdays': self.config.HISTORICAL_BACKDAYS,
                'duration': self.config.HISTORICAL_DURATION,
                'csv_export_enabled': self.config.HISTORICAL_CSV_EXPORT_ENABLED,
                'symbols': self.config.HISTORICAL_SYMBOLS
            }
            
            # Check if config changed or first time running
            if self.execution_tracker.config_has_changed(history_config):
                self.logger.info("Historical data config has changed. Re-running fetch...")
                self._fetch_history_data()
            # If config same, check if already ran today
            elif self.execution_tracker.has_run_today():
                last_run = self.execution_tracker.get_last_execution().get('last_run', 'Unknown')
                self.logger.info(f"Historical data already fetched today with same config. Skipping. (Last run: {last_run})")
            else:
                self.logger.info("Running historical data fetch (not run today)...")
                self._fetch_history_data()
        except Exception as e:
            self.logger.error(f"Error Auto-start error: {e}", exc_info=True)     

if __name__ == "__main__":
    app = HistoryDataFetchController()
    app.run()       
    sys.exit(0)