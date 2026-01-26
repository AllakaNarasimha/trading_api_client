#!/usr/bin/env python3
"""
Option Chain Monitor - Simple API Version

Simple REST API to control option chain monitoring.
Easy to understand and maintain.

Module Organization:
- client.utils.config: Configuration management
- client.utils.monitor: Option chain monitoring logic
- client.utils.api: Flask REST API
- client.utils.cutoff_timer: Scheduled shutdown capability
"""

import os
import sys
import subprocess
import logging
import signal
import threading
import time
from logging.handlers import RotatingFileHandler

# Add current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(__file__))

# Import client package (SSL configuration is applied automatically via client.__init__)
from client.history_data_fetch_controller import HistoryDataFetchController
from client.live_data_fetch_controller import LiveDataFetchController
from client.utils.historical_data_fetcher import HistoricalDataFetcher
from client.utils.live_price_fetcher import LivePriceFetcher
from client.utils.config import Config
from client.utils.option_chain_monitor import OptionChainMonitor
from client.utils.option_chain_api import OptionChainAPI
from client.utils.cutoff_timer import CutoffTimer
from client.utils.execution_tracker import ExecutionTracker


class OptionChainMonitorApp:
    def __init__(self):
        self.config = Config()
        self.option_chain_monitor = OptionChainMonitor()
        self.historical_data_fetcher = HistoricalDataFetcher()
        self.live_price_fetcher = LivePriceFetcher()
        self.api = OptionChainAPI(self.option_chain_monitor)
        self.cutoff_timer = None
        self._fetch_historical_data_called = False
        self._fetch_live_data_called = False
        self._fetch_option_chain_data_called = False
        # Initialize execution tracker for historical data fetch
        self.history_execution_tracker = ExecutionTracker('history')

    def setup_logging(self, name: str = "app"):
        """Setup logging configuration."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = self.config.get_log_file_path(script_dir, name)
        logging_settings = self.config.get_logging_settings()

        # Setup logger
        logger = logging.getLogger(name)
        logger.setLevel(logging_settings['level'])

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=logging_settings['max_bytes'],
            backupCount=logging_settings['backup_count']
        )
        file_formatter = logging.Formatter(
            logging_settings['format'],
            datefmt=logging_settings['date_format']
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging_settings['level'])
        console_formatter = logging.Formatter(logging_settings['format'])
        console.setFormatter(console_formatter)
        logger.addHandler(console)

        return logger

    def _fetch_historical_data_delayed(self):
        """Fetch historical data after 5 second delay."""
        if not self._fetch_historical_data_called:
            # Build current history config
            history_config = {
                'enabled': self.config.HISTORICAL_DATA_ENABLED,
                'backdays': self.config.HISTORICAL_BACKDAYS,
                'duration': self.config.HISTORICAL_DURATION,
                'csv_export_enabled': self.config.HISTORICAL_CSV_EXPORT_ENABLED,
                'symbols': self.config.HISTORICAL_SYMBOLS
            }            
            self.logger.info(f"execution tracker file: {self.history_execution_tracker.tracker_file}")
 
            # Check if config changed or first time running
            if self.history_execution_tracker.config_has_changed(history_config):
                self.logger.info("Historical data config has changed. Re-running fetch...")
            # If config same, check if already ran today
            elif self.history_execution_tracker.has_run_today():
                last_run = self.history_execution_tracker.get_last_execution().get('last_run', 'Unknown')
                self.logger.info(f"Historical data already fetched today with same config. Skipping. (Last run: {last_run})")
                return
            
            self._fetch_historical_data_called = True
            def _actual_fetch():
                try:
                    self.logger.info("Waiting 5 seconds before fetching historical data...")
                    time.sleep(5)
                    self.logger.info("Fetching historical data...")
                    self.historical_data_fetcher.fetch_historical_data()
                    self.logger.info("Historical data fetch completed")
                    
                    # Only update tracker config AFTER successful fetch
                    history_config = {
                        'enabled': self.config.HISTORICAL_DATA_ENABLED,
                        'backdays': self.config.HISTORICAL_BACKDAYS,
                        'duration': self.config.HISTORICAL_DURATION,
                        'csv_export_enabled': self.config.HISTORICAL_CSV_EXPORT_ENABLED,
                        'symbols': self.config.HISTORICAL_SYMBOLS
                    }
                    self.history_execution_tracker.record_execution(config=history_config)
                    self.logger.info(f"Execution tracker updated with new config, config_file: {self.history_execution_tracker.tracker_file}")
                    
                    # Restart app after successful history data fetch
                    self.logger.info("Restarting app after history data fetch...")
                    time.sleep(2)  # Give time for logs to flush
                    self._restart_app()
                except Exception as e:
                    self.logger.error(f"Error fetching historical data: {e}", exc_info=True)
            
            fetch_thread = threading.Thread(target=_actual_fetch, daemon=True)
            fetch_thread.start()
            fetch_thread.join(timeout=60)

    def _fetch_live_data(self):
        """Fetch live data after 5 second delay."""
        if not self._fetch_live_data_called:
            self._fetch_live_data_called = True
            def _actual_fetch():
                try:
                    self.logger.info("Waiting 10 seconds before fetching live data...")
                    time.sleep(5)
                    self.logger.info("Fetching live data...")
                    self.live_price_fetcher.subscribe_to_live_prices()
                    self.logger.info("Live data fetch completed")
                except Exception as e:
                    self.logger.error(f"Error fetching live data: {e}", exc_info=True)
            
            live_data_fetching_thread = threading.Thread(target=_actual_fetch, daemon=True)
            live_data_fetching_thread.start()
            live_data_fetching_thread.join(timeout=10)

    def _fetch_option_chain_data(self):
        """Fetch live data after 5 second delay."""
        if not self._fetch_option_chain_data_called:
            self._fetch_option_chain_data_called = True
            def _actual_fetch():
                try:
                    self.logger.info("Waiting 5 seconds before fetching option chain data...")
                    time.sleep(5)
                    self.logger.info("Fetching option chain data...")
                    self.option_chain_monitor.start_monitoring()
                    self.logger.info("Option chain data fetch completed")
                except Exception as e:
                    self.logger.error(f"Error fetching option chain data: {e}", exc_info=True)
            
            live_data_fetching_thread = threading.Thread(target=_actual_fetch, daemon=True)
            live_data_fetching_thread.start()
            live_data_fetching_thread.join(timeout=120)

    def shutdown_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        try:
            if self.option_chain_monitor.monitor_running:
                self.option_chain_monitor.stop_event.set()
                if self.option_chain_monitor.monitor_thread:
                    self.option_chain_monitor.monitor_thread.join(timeout=10)
            self.option_chain_monitor._cleanup_resources()
            
            # Fetch historical data on shutdown if not already done
            self._fetch_historical_data_delayed()
            
            self.logger.info("Shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
        finally:
            os._exit(0)

    def authorize_broker(self) -> bool:
        from client.auth import get_auth_manager
        auth_manager = get_auth_manager()
        if auth_manager.is_authenticated:
            self.logger.info("Broker authorization successful")
            return True
        return False
    
    def _restart_app(self) -> None:
        """Restart the application using run_monitor.bat from config.dir after 10 second delay."""
        self.logger.info("Initiating app restart with 10 second delay...")
        try:
            # Read config.dir to get the configured directory
            project_root = os.path.dirname(os.path.abspath(__file__))
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
        """Start the API server and optionally auto-start monitoring."""
        
        self.logger = self.setup_logging("app")

        # Signal handlers are registered in the main thread

        self.logger.info("="*60)
        self.logger.info("Option Chain Monitor API - Starting")
        self.logger.info("="*60)
        self.logger.info(f"Log file: {self.config.get_log_file_path(os.path.dirname(os.path.abspath(__file__)))}")
        self.logger.info(f"API Host: {self.config.API_HOST}:{self.config.API_PORT}")
        self.logger.info(f"Max symbols: {self.config.MAX_SYMBOLS}")
        self.logger.info(f"Default strikes: {self.config.DEFAULT_STRIKES}")
        # self.logger.info(f"Default symbol config:")
        # for symbol, config_data in self.config.get_default_symbol_config().items():
        #     self.logger.info(f"  {symbol}: poll at seconds {config_data['poll_seconds']}, strikes: {config_data['strikes']}")
        # self.logger.info(f"Auto-start enabled: {self.config.AUTO_START}")
        # self.logger.info(f"Cutoff timer enabled: {self.config.CUTOFF_ENABLED}")
        if self.config.CUTOFF_ENABLED:
            self.logger.info(f"Cutoff time: {self.config.CUTOFF_HOUR:02d}:{self.config.CUTOFF_MINUTE:02d}")
        self.logger.info("="*60)

        # Initialize cutoff timer if enabled
        if self.config.CUTOFF_ENABLED:
            self.logger.info(f"Initializing cutoff timer for {self.config.CUTOFF_HOUR:02d}:{self.config.CUTOFF_MINUTE:02d}")
            try:
                self.cutoff_timer = CutoffTimer(self.config.CUTOFF_HOUR, self.config.CUTOFF_MINUTE)
                self.cutoff_timer.start()
                self.logger.info("Ok Cutoff timer started")
            except Exception as e:
                self.logger.error(f"Error Failed to start cutoff timer: {e}", exc_info=True)

        # Fetch historical data only once
        # if self.config.HISTORICAL_DATA_ENABLED:
        #     self._fetch_historical_data_delayed()
        # Auto-start monitoring if enabled
        if self.config.AUTO_START:
            self.logger.info("Auto-starting monitor...")
            try:  
                # Initiate live data fetch if enabled
                # if self.config.LIVE_DATA_ENABLED:
                #      self._fetch_live_data()      

                # Start option chain monitoring      
                self._fetch_option_chain_data()            
            except Exception as e:
                self.logger.error(f"Error Auto-start error: {e}", exc_info=True)

        self.logger.info("API endpoints available:")
        self.logger.info(f"  GET  http://localhost:{self.config.API_PORT}/api/health")
        self.logger.info(f"  GET  http://localhost:{self.config.API_PORT}/api/status")
        self.logger.info(f"  POST http://localhost:{self.config.API_PORT}/api/start")
        self.logger.info(f"  POST http://localhost:{self.config.API_PORT}/api/add-symbol")
        self.logger.info(f"  POST http://localhost:{self.config.API_PORT}/api/stop")
        self.logger.info("="*60)

        # Start Flask API server
        try:
            self.api.run(host=self.config.API_HOST, port=self.config.API_PORT, debug=False, threaded=True, use_reloader=False)
        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}", exc_info=True)
            self.shutdown_handler(signal.SIGTERM, None)


def start_application_threads():
    """Start the application threads: app, fetcher, and history fetcher."""
    app = OptionChainMonitorApp()
    
    # Setup logging first
    app.logger = app.setup_logging("main")
    
    # Authorize broker before starting threads
    while not app.authorize_broker():
        time.sleep(5)
        app.logger.info("Retrying broker authorization...")
    app.logger.info("Broker authorized successfully")
    
    # Register signal handlers in the main thread
    signal.signal(signal.SIGINT, app.shutdown_handler)
    signal.signal(signal.SIGTERM, app.shutdown_handler)
    
    def run_app():
        app.run()

    def run_live_fetcher():
        livePriceFetcher = LiveDataFetchController()
        livePriceFetcher.run()
    
    def run_history_fetcher():
        historyDataFetcher = HistoryDataFetchController()
        historyDataFetcher.run()
    

    # Start both in separate threads
    app_thread = threading.Thread(target=run_app, daemon=False)
    live_fetcher_thread = threading.Thread(target=run_live_fetcher, daemon=True)

    history_config = {
            'enabled': app.config.HISTORICAL_DATA_ENABLED,
            'backdays': app.config.HISTORICAL_BACKDAYS,
            'duration': app.config.HISTORICAL_DURATION,
            'csv_export_enabled': app.config.HISTORICAL_CSV_EXPORT_ENABLED,
            'symbols': app.config.HISTORICAL_SYMBOLS
        }    
    
    if app.config.HISTORICAL_DATA_ENABLED and app.history_execution_tracker.config_has_changed(history_config):
        app.logger.info("Starting historical data fetcher thread")
        history_fetcher_thread = threading.Thread(target=run_history_fetcher, daemon=True)
        history_fetcher_thread.start()
    else:
        app.logger.info("Skipping historical data fetcher thread (either disabled or already fetched today with same config)")

    app_thread.start()
    # live_fetcher_thread.start()
    

    # Wait for the app thread (which runs the server)
    app_thread.join()


if __name__ == "__main__":
    start_application_threads()


def main():
    """Entry point for the application."""
    start_application_threads()