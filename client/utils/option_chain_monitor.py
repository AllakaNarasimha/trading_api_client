"""
Option Chain Monitor - Core monitoring logic.
Manages polling threads and data collection from multiple symbols.
"""

import atexit
import datetime
import logging
import threading
from typing import Dict, List, Tuple, Optional, Any

from client.watchlist import PriceWatcher
from nslogger.option_chain_manager import OptionChainManager
from client.utils.config import Config
from client.utils.file_utils import FileUtils
from client.utils.health_check_monitor import HealthCheckMonitor

logger = logging.getLogger('option-chain')
config = Config()

class OptionChainMonitor:
    """Core class for option chain monitoring logic."""

    def __init__(self):
        """Initialize the monitor with default configuration."""
        # State variables
        self.monitor_running: bool = False
        self.stop_event: threading.Event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self.state_lock: threading.RLock = threading.RLock()

        # Current polling state - shared with thread
        # Format: {symbol: {'poll_seconds': [list], 'strikes': int}}
        self.current_symbols: Dict[str, Dict[str, Any]] = {}
        self.current_watchers: Dict[str, PriceWatcher] = {}
        self.current_managers: Dict[str, OptionChainManager] = {}
        self.number_of_strikes: int = config.DEFAULT_STRIKES
        
        # Health check configuration (in seconds)
        self.health_check_interval: int = getattr(config, 'HEALTH_CHECK_INTERVAL', 300)  # Default 5 minutes
        self.saved_symbol_config: Optional[Dict[str, Dict[str, Any]]] = None
        self.health_check_monitor: Optional[HealthCheckMonitor] = None
        atexit.register(self._cleanup_resources)
    
    @staticmethod
    def _sync_to_minute_boundary(stop_event: threading.Event) -> None:
        """
        Synchronize to the next minute boundary (when seconds = 0).
        If not already at minute 0, waits until the next minute boundary.
        
        Args:
            stop_event: threading.Event to check for early termination
        """
        current_time = datetime.datetime.now()
        if current_time.second != 0:
            # Calculate seconds until next minute (when second becomes 0)
            seconds_until_next_minute = 60 - current_time.second
            microseconds_into_second = current_time.microsecond
            total_wait_time = seconds_until_next_minute - (microseconds_into_second / 1000000.0)
            logger.info(f"Waiting {total_wait_time:.2f} seconds until next minute boundary (00 seconds)...")
            stop_event.wait(timeout=total_wait_time)
        else:
            logger.info("Already at minute boundary, starting immediately")

    def _start_polling_thread(self, symbol_config: Dict[str, Dict[str, Any]]) -> None:
        """
        Start the polling thread with the given symbol configuration.
        Used by the health check monitor to restart the polling thread.
        """
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=self.poll_option_chain,
            args=(symbol_config,),
            daemon=False,
            name="fetch_monitor"
        )
        self.monitor_thread.start()
        logger.info(f"[THREAD START] fetch_monitor thread started (ID: {self.monitor_thread.ident})")

    def _cleanup_resources(self) -> None:
        """Clean up resources (watchers, managers, database connections, live prices)."""
        logger.info("Cleaning up resources...")
        
        # Stop live price monitoring if active
        # self.stop_live_price_monitoring()
        
        with self.state_lock:
            # Close database connections if managers have cleanup methods
            for manager in self.current_managers.values():
                try:
                    if hasattr(manager, 'close'):
                        manager.close()
                except Exception as e:
                    logger.error(f"Error closing manager: {e}")
            
            self.current_watchers.clear()
            self.current_managers.clear()
            self.current_symbols.clear()
        logger.info("Resource cleanup complete")

    def _initialize_symbol_resources(self, symbol_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Initialize watchers and managers for all symbols in the configuration.
        Returns only successfully initialized symbols.

        Args:
            symbol_config: dict {symbol: {'poll_seconds': [list], 'strikes': int}}

        Returns:
            dict: successfully initialized symbols configuration
        """
        successful_symbols = {}
        for symbol in symbol_config:
            try:
                self.current_watchers[symbol] = PriceWatcher('option-chain')
                symbol_name = FileUtils.get_symbol_name(symbol)
                self.current_managers[symbol] = OptionChainManager(db_file=f"{symbol_name}.db")
                successful_symbols[symbol] = symbol_config[symbol]
            except Exception as e:
                logger.error(f"Failed to initialize {symbol}: {e}")
                self.current_watchers.pop(symbol, None)
                self.current_managers.pop(symbol, None)
        return successful_symbols

    def _setup_csv_export(self) -> Dict[str, str]:
        """
        Setup CSV export file paths for all symbols if enabled.

        Returns:
            dict: {symbol: file_path}
        """
        symbol_filenames = {}
        if getattr(config, 'csv_export_enabled', False):
            for sym in self.current_symbols:
                symbol_filenames[sym] = FileUtils.get_csv_file_path(sym, data_type='OPTION-CHAIN')
            logger.info(f"CSV export enabled for {len(symbol_filenames)} symbols")
        return symbol_filenames

    def _fetch_and_process_option_chain(self, symbol: str, symbol_strikes: int,
                                       symbol_filenames: Dict[str, str],
                                       csv_export_enabled: bool) -> bool:
        """
        Fetch option chain data for a symbol and save to database/CSV.

        Args:
            symbol: symbol to fetch
            symbol_strikes: number of strikes to fetch
            symbol_filenames: dict mapping symbols to CSV file paths
            csv_export_enabled: whether CSV export is enabled

        Returns:
            bool: True if fetch was successful, False if should skip symbol
        """
        try:
            option_chain = self.current_watchers[symbol].get_option_chain(symbol, symbol_strikes)
            
            if option_chain['s'] == 'error':
                logger.info(f"Error option chain for {symbol} with {option_chain['message']}")
                return False

            if not option_chain or 'data' not in option_chain:
                logger.warning(f"Error {symbol}: No data")
                return True

            data_count = len(option_chain['data'])
            logger.info(f"Ok {symbol}: {data_count} options (strikes: {symbol_strikes})")
            
            # Save to database
            self.current_managers[symbol].log_option_chain(option_chain['data'])
            
            # Save to CSV if enabled
            if csv_export_enabled and option_chain['data']:
                path = symbol_filenames[symbol]
                try:
                    success = FileUtils.save_dict_list_to_csv(option_chain['data'], path, mode='w')
                    if success:
                        logger.info(f"Saved {data_count} records to {path}")
                    else:
                        logger.warning(f"Failed to save CSV for {symbol}")
                except Exception as e:
                    logger.error(f"Failed to save CSV for {symbol}: {e}")
            
            return True

        except Exception as e:
            logger.error(f"Error {symbol}: {str(e)}")
            return True

    def _is_market_open(self) -> bool:
        """
        Check if market is open using the first available watcher.

        Returns:
            bool: True if market is open, False otherwise
        """
        if not self.current_watchers:
            return True
        first_watcher = next(iter(self.current_watchers.values()), None)
        return first_watcher.is_market_open() if first_watcher else True

    def _validate_and_convert_config(self, symbol_config: Optional[Dict[str, Dict[str, Any]]],
                                     default_strikes: Optional[int]) -> Tuple[Optional[Dict[str, Dict[str, Any]]], bool, str]:
        """
        Validate and convert symbol configuration to new format if needed.

        Args:
            symbol_config: symbol configuration dict or None
            default_strikes: default strikes to use

        Returns:
            tuple: (converted_config, is_valid, validation_message)
        """
        symbol_config = symbol_config or config.get_default_symbol_config()
        
        # Handle backward compatibility
        if symbol_config and isinstance(next(iter(symbol_config.values()), None), list):
            default_strikes = default_strikes or config.DEFAULT_STRIKES
            converted_config = {}
            for symbol, poll_secs in symbol_config.items():
                converted_config[symbol] = {"poll_seconds": poll_secs, "strikes": default_strikes}
            symbol_config = converted_config

        # Validate configuration
        is_valid, validation_msg = config.validate_symbol_config(symbol_config)
        return symbol_config, is_valid, validation_msg

    def poll_option_chain(self, symbol_config: Dict[str, Dict[str, Any]]) -> None:
        """
        Main polling function - runs in a separate thread.
        Fetches option chain data at symbol-specific intervals.
        Allows adding new symbols without restarting.

        Args:
            symbol_config: dict {symbol: {'poll_seconds': [list], 'strikes': int}}
        """
        logger.info(f"[THREAD STARTED] fetch_monitor thread is now running")
        
        # Initialize symbol resources
        self.current_symbols = symbol_config.copy()
        successful_symbols = self._initialize_symbol_resources(self.current_symbols)
        self.current_symbols = successful_symbols

        if not self.current_symbols:
            logger.error("No symbols successfully initialized")
            return

        logger.info(f"Polling thread started for: {list(self.current_symbols.keys())}")
        self.monitor_running = True
        last_second = None
        is_market_open = self._is_market_open()

        try:
            is_first_fetch_done = False
            self._sync_to_minute_boundary(self.stop_event)
            
            csv_export_enabled = getattr(config, 'csv_export_enabled', False)
            symbol_filenames = self._setup_csv_export()
            no_expiry_symbols = []

            while not self.stop_event.is_set():
                current_time = datetime.datetime.now()
                current_second = current_time.second

                if current_second != last_second:
                    with self.state_lock:
                        symbols_to_check = self.current_symbols.copy()

                    symbols_to_poll = [
                        symbol for symbol, config_data in symbols_to_check.items()
                        if current_second in config_data['poll_seconds']
                    ]
                    
                    if symbols_to_poll:
                        logger.debug(f"Polling {len(symbols_to_poll)} symbols at second {current_second}")
                        
                        for symbol in symbols_to_poll:
                            if symbol in no_expiry_symbols:
                                logger.info(f"Skipping {symbol} due to previous no expiry data")
                                continue
                            
                            symbol_strikes = symbols_to_check[symbol]['strikes']
                            success = self._fetch_and_process_option_chain(
                                symbol, symbol_strikes, symbol_filenames, csv_export_enabled
                            )
                            if not success:
                                no_expiry_symbols.append(symbol)
                            
                            is_first_fetch_done = True

                    last_second = current_second

                self.stop_event.wait(timeout=config.OPTION_CHAIN_FETCH_DURATION)
                if is_first_fetch_done and not is_market_open:
                    logger.info("Market is closed. Stopping monitor.")
                    break

        except Exception as e:
            logger.error(f"Polling thread error: {str(e)}", exc_info=True)

        finally:
            self.monitor_running = False
            self._cleanup_resources()
            logger.info(f"[THREAD STOPPED] fetch_monitor thread stopped gracefully")

    def start_monitoring(self, symbol_config: Optional[Dict[str, Dict[str, Any]]] = None, 
                        default_strikes: Optional[int] = None) -> Tuple[bool, str]:
        """Start monitoring with given configuration.

        Args:
            symbol_config: dict {symbol: {'poll_seconds': [list], 'strikes': int}} or None for defaults
            default_strikes: default strikes for symbols that don't specify strikes

        Returns:
            tuple: (success: bool, message: str)
        """
        if self.monitor_running:
            logger.info("Monitor already running - ignoring start request")
            return True, 'Monitor already running'

        try:
            symbol_config, is_valid, validation_msg = self._validate_and_convert_config(symbol_config, default_strikes)
            
            if not is_valid:
                logger.error(f"Invalid symbol config: {validation_msg}")
                return False, validation_msg
            
            self.number_of_strikes = default_strikes or config.DEFAULT_STRIKES
            self.stop_event.clear()
            self.current_symbols = symbol_config.copy()
            self.current_watchers = {}
            self.current_managers = {}

            # Start polling thread
            self.monitor_thread = threading.Thread(
                target=self.poll_option_chain,
                args=(symbol_config,),
                daemon=False,
                name="fetch_monitor"
            )
            self.monitor_thread.start()
            logger.info(f"[THREAD START] fetch_monitor thread started (ID: {self.monitor_thread.ident})")

            # Save config and start health check monitor
            self.saved_symbol_config = symbol_config.copy()
            self.health_check_monitor = HealthCheckMonitor(
                check_function=lambda: self.monitor_running and (self.monitor_thread.is_alive() if self.monitor_thread else False),
                restart_function=lambda: self._start_polling_thread(self.saved_symbol_config),
                interval=self.health_check_interval,
                name="option_chain_health_check"
            )
            self.health_check_monitor.start()

            return True, 'Monitor started'

        except Exception as e:
            logger.error(f"Start error: {str(e)}", exc_info=True)
            self.stop_event.set()
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
            self._cleanup_resources()
            return False, f"Failed to start: {str(e)}"

    def add_symbol(self, new_symbol: str, poll_secs: Optional[List[int]] = None, 
                  strikes: Optional[int] = None) -> Tuple[bool, str, Dict[str, Dict[str, Any]]]:
        """Add a new symbol to monitoring while running.

        Args:
            new_symbol: symbol name to add
            poll_secs: list of seconds to poll at, defaults to [0, 30]
            strikes: number of strikes to fetch, defaults to DEFAULT_STRIKES

        Returns:
            tuple: (success: bool, message: str, symbol_config: dict)
        """
        if not self.monitor_running:
            return False, 'Monitor not running', {}

        try:
            poll_secs = poll_secs or [0, 30]
            strikes = strikes or config.DEFAULT_STRIKES

            if not new_symbol or not new_symbol.strip():
                return False, 'Symbol not provided', {}
            
            temp_config = {new_symbol: {"poll_seconds": poll_secs, "strikes": strikes}}
            is_valid, validation_msg = config.validate_symbol_config(temp_config)
            if not is_valid:
                return False, validation_msg, {}

            with self.state_lock:
                if new_symbol in self.current_symbols:
                    logger.info(f"Symbol {new_symbol} already being monitored")
                    return True, f'Symbol {new_symbol} already being monitored', self.current_symbols
                
                if len(self.current_symbols) >= config.MAX_SYMBOLS:
                    return False, f'Maximum {config.MAX_SYMBOLS} symbols reached', self.current_symbols

                try:
                    self.current_watchers[new_symbol] = PriceWatcher('option-chain')
                    symbol_name = FileUtils.get_symbol_name(new_symbol)
                    self.current_managers[new_symbol] = OptionChainManager(db_file=f"{symbol_name}.db")
                    self.current_symbols[new_symbol] = {"poll_seconds": poll_secs, "strikes": strikes}
                except Exception as init_error:
                    self.current_watchers.pop(new_symbol, None)
                    self.current_managers.pop(new_symbol, None)
                    raise init_error

            logger.info(f"Symbol {new_symbol} added with poll_seconds={poll_secs}, strikes={strikes}")
            return True, f'Symbol {new_symbol} added', self.current_symbols

        except Exception as e:
            logger.error(f"Add symbol error: {str(e)}", exc_info=True)
            return False, f"Failed to add symbol: {str(e)}", {}

    def stop_monitoring(self) -> Tuple[bool, str]:
        """Stop the monitor.

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.monitor_running:
            return False, 'Monitor not running'

        try:
            logger.info("Stopping monitor...")
            self.stop_event.set()
            self.saved_symbol_config = None

            if self.monitor_thread:
                logger.info(f"[THREAD STOP] Waiting for fetch_monitor thread (ID: {self.monitor_thread.ident}) to stop...")
                self.monitor_thread.join(timeout=10)
                if self.monitor_thread.is_alive():
                    logger.warning(f"[THREAD TIMEOUT] fetch_monitor thread did not stop gracefully after 10s")
                else:
                    logger.info(f"[THREAD STOPPED] fetch_monitor thread stopped successfully")
            
            if self.health_check_monitor:
                self.health_check_monitor.stop()

            logger.info("Monitor stopped successfully")
            return True, 'Monitor stopped'

        except Exception as e:
            logger.error(f"Stop error: {str(e)}", exc_info=True)
            return False, f"Failed to stop: {str(e)}"

    def get_status(self) -> Dict[str, Any]:
        """Get current monitor status.

        Returns:
            dict: status information
        """
        with self.state_lock:
            return {
                'running': self.monitor_running,
                'symbols': list(self.current_symbols.keys()),
                'symbol_count': len(self.current_symbols),
                'symbol_config': self.current_symbols.copy(),
                'default_strikes': self.number_of_strikes,
                'thread_alive': self.monitor_thread.is_alive() if self.monitor_thread else False,
                'health_check_running': self.health_check_monitor.thread.is_alive() if self.health_check_monitor and self.health_check_monitor.thread else False,
                'health_check_interval': self.health_check_interval
            }
