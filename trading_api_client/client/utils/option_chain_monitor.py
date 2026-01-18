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
from client.utils.historical_data_fetcher import HistoricalDataFetcher
from client.utils.live_price_fetcher import LivePriceFetcher

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
        self.health_check_thread: Optional[threading.Thread] = None
        self.health_check_stop_event: threading.Event = threading.Event()
        self.state_lock: threading.RLock = threading.RLock()

        # Current polling state - shared with thread
        # Format: {symbol: {'poll_seconds': [list], 'strikes': int}}
        self.current_symbols: Dict[str, Dict[str, Any]] = {}
        self.current_watchers: Dict[str, PriceWatcher] = {}
        self.current_managers: Dict[str, OptionChainManager] = {}
        self.number_of_strikes: int = config.DEFAULT_STRIKES
        
        # Live price fetcher (optional, for real-time price streaming)
        self.live_price_fetcher: Optional[LivePriceFetcher] = None
        
        # Health check configuration (in seconds)
        self.health_check_interval: int = getattr(config, 'HEALTH_CHECK_INTERVAL', 300)  # Default 5 minutes
        self.saved_symbol_config: Optional[Dict[str, Dict[str, Any]]] = None
        
        # Register cleanup on exit
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

    def health_check_monitor(self) -> None:
        """
        Monitor thread that checks if the polling thread is still running.
        If polling thread has stopped, restart it automatically.
        Runs at configured interval (default 5 minutes).
        """
        logger.info(f"[THREAD STARTED] health_check_monitor thread is now running (interval: {self.health_check_interval}s)")
        
        while not self.health_check_stop_event.is_set():
            try:
                # Wait for the configured interval
                if self.health_check_stop_event.wait(timeout=self.health_check_interval):
                    # Stop event was set, exit gracefully
                    break
                
                # Check if polling thread is still alive
                with self.state_lock:
                    is_running = self.monitor_running
                    thread_alive = self.monitor_thread and self.monitor_thread.is_alive()
                    saved_config = self.saved_symbol_config
                
                if not is_running and not thread_alive and saved_config:
                    logger.warning("Polling thread stopped unexpectedly! Restarting...")
                    try:
                        # Restart the polling thread
                        self.stop_event.clear()
                        self.monitor_thread = threading.Thread(
                            target=self.poll_option_chain,
                            args=(saved_config,),
                            daemon=False,
                            name="fetch_monitor"
                        )
                        self.monitor_thread.start()
                        logger.info(f"[THREAD RESTART] fetch_monitor restarted successfully (ID: {self.monitor_thread.ident})")
                    except Exception as restart_error:
                        logger.error(f"Failed to restart polling thread: {restart_error}", exc_info=True)
                elif is_running and thread_alive:
                    logger.info(f"[HEALTH CHECK] fetch_monitor thread is running (ID: {self.monitor_thread.ident})")
                
            except Exception as e:
                logger.error(f"Health check error: {e}", exc_info=True)
        
        logger.info(f"[THREAD STOPPED] health_check_monitor thread stopped gracefully")

    def _ensure_watchers_initialized(self) -> None:
        """
        Ensure watchers are initialized for all current symbols.
        If watchers already exist, they are ignored (not recreated).
        Creates PriceWatcher instances for any missing symbols.
        """
        if not self.current_symbols:
            logger.warning("No symbols configured for watcher initialization")
            return
        
        for symbol in self.current_symbols:
            if symbol not in self.current_watchers:
                try:
                    self.current_watchers[symbol] = PriceWatcher('option-chain')
                    logger.info(f"Initialized watcher for symbol: {symbol}")
                except Exception as e:
                    logger.error(f"Failed to initialize watcher for {symbol}: {e}")
            else:
                logger.info(f"Watcher for {symbol} already exists, skipping initialization")
 
    def start_live_price_monitoring(self) -> None:
        """
        Start live price subscriptions for all configured symbols.
        Streams real-time prices via WebSocket from Fyers.
        """
        try:
            if not self.current_watchers:
                logger.warning("No watchers available for live price monitoring")
                return
            
            logger.info("Initializing live price monitoring...")
            self.live_price_fetcher = LivePriceFetcher(self.current_watchers)
            
            # Subscribe to live prices
            self.live_price_fetcher.subscribe_to_live_prices()
            
            # Log subscription status
            status = self.live_price_fetcher.get_subscription_status()
            logger.info(f"Live price subscriptions active: {status['subscribed_count']}/{status['total_symbols']} symbols")
        
        except Exception as e:
            logger.error(f"Error starting live price monitoring: {e}", exc_info=True)

    def stop_live_price_monitoring(self) -> None:
        """
        Stop live price subscriptions and cleanup resources.
        """
        try:
            if not self.live_price_fetcher:
                logger.info("Live price fetcher not initialized")
                return
            
            logger.info("Stopping live price monitoring...")
            
            # Unsubscribe from all live prices
            self.live_price_fetcher.unsubscribe_from_live_prices()
            
            # Cleanup resources
            self.live_price_fetcher.cleanup()
            self.live_price_fetcher = None
            
            logger.info("Live price monitoring stopped")
        
        except Exception as e:
            logger.error(f"Error stopping live price monitoring: {e}", exc_info=True)

    def poll_option_chain(self, symbol_config: Dict[str, Dict[str, Any]]) -> None:
        """
        Main polling function - runs in a separate thread.
        Fetches option chain data at symbol-specific intervals.
        Allows adding new symbols without restarting.

        Args:
            symbol_config: dict {symbol: {'poll_seconds': [list], 'strikes': int}}
        """
        logger.info(f"[THREAD STARTED] fetch_monitor thread is now running")
        
        # Create initial watchers and managers
        self.current_symbols = symbol_config.copy()
        successful_symbols = {}

        for symbol in self.current_symbols:
            try:
                self.current_watchers[symbol] = PriceWatcher('option-chain')
                symbol_name = FileUtils.get_symbol_name(symbol)
                self.current_managers[symbol] = OptionChainManager(db_file=f"{symbol_name}.db")
                successful_symbols[symbol] = self.current_symbols[symbol]
            except Exception as e:
                logger.error(f"Failed to initialize {symbol}: {e}")
                # Clean up failed initialization
                self.current_watchers.pop(symbol, None)
                self.current_managers.pop(symbol, None)

        # Update current_symbols to only include successfully initialized symbols
        self.current_symbols = successful_symbols

        if not self.current_symbols:
            logger.error("No symbols successfully initialized")
            return

        logger.info(f"Polling thread started for: {list(self.current_symbols.keys())}")
        self.monitor_running = True

        last_second = None

        is_market_open = True
        if len(self.current_watchers) > 0:
            first_watcher = next(iter(self.current_watchers.values()), None)
            if first_watcher is not None:
                is_market_open = first_watcher.is_market_open()       

        try:
            is_first_fetch_done = False
            
            # Synchronize to minute boundary (00 seconds)
            self._sync_to_minute_boundary(self.stop_event)
            
            # Start live price monitoring if enabled
            # if config.LIVE_DATA_ENABLED:
            #     self.start_live_price_monitoring()
            
            # CSV Export Setup (if enabled)
            csv_export_enabled = getattr(config, 'csv_export_enabled', False)
            symbol_filenames = {}
            no_expiry_symbols = []

            if csv_export_enabled:
                # Pre-compute filenames for all symbols using FileUtils
                for sym in self.current_symbols:
                    # Note: Using 'OPTION-CHAIN' as data_type to distinguish from LIVE/HISTORICAL
                    # FileUtils will create the appropriate folder structure
                    symbol_filenames[sym] = FileUtils.get_csv_file_path(sym, data_type='OPTION-CHAIN')
                logger.info(f"CSV export enabled for {len(symbol_filenames)} symbols")
                                    
            while not self.stop_event.is_set():
                current_time = datetime.datetime.now()
                current_second = current_time.second

                # Check if any symbol needs polling at this second
                if current_second != last_second:
                    # Get symbols to poll (thread-safe)
                    with self.state_lock:
                        symbols_to_check = self.current_symbols.copy()

                    symbols_to_poll = []
                    for symbol, config_data in symbols_to_check.items():
                        if current_second in config_data['poll_seconds']:
                            symbols_to_poll.append(symbol)                    
                    
                    if symbols_to_poll:
                        logger.debug(f"Polling {len(symbols_to_poll)} symbols at second {current_second}")
                       
                        for symbol in symbols_to_poll:
                            if symbol in no_expiry_symbols:
                                logger.info(f"Skipping {symbol} due to previous no expiry data")
                                continue
                            try:
                                # Get symbol-specific strikes
                                symbol_strikes = symbols_to_check[symbol]['strikes']
                                option_chain = self.current_watchers[symbol].get_option_chain(symbol, symbol_strikes)
                                if (option_chain['s'] == 'error'):
                                    logger.info(f"Error option chain for {symbol} with {option_chain['message']}")
                                    no_expiry_symbols.append(symbol)
                                    continue

                                logger.info(f"Fetched option chain for {symbol} with {len(option_chain['data'])} strikes")
                                if option_chain and 'data' in option_chain:
                                    data_count = len(option_chain['data'])
                                    logger.info(f"Ok {symbol}: {data_count} options (strikes: {symbol_strikes})")
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
                                else:
                                    logger.warning(f"Error {symbol}: No data")

                            except Exception as e:
                                logger.error(f"Error {symbol}: {str(e)}")
                            
                            is_first_fetch_done = True

                    last_second = current_second

                # Sleep for configured duration before next iteration
                self.stop_event.wait(timeout=config.OPTION_CHAIN_FETCH_DURATION)  
                if (is_first_fetch_done == True and is_market_open == False):
                    logger.info("Market is closed. Stopping monitor.")
                    break


        except Exception as e:
            logger.error(f"Polling thread error: {str(e)}", exc_info=True)

        finally:
            self.monitor_running = False
            self._cleanup_resources()
            logger.info(f"[THREAD STOPPED] fetch_monitor thread stopped gracefully")
            
            # Ensure health check monitor is running if monitoring was intentionally stopped
            # (health_check_stop_event would be set). Only restart if it wasn't intentionally stopped.
            # If health check stop event is NOT set, it means monitoring is still desired
            if not self.health_check_stop_event.is_set():
                if not self.health_check_thread or not self.health_check_thread.is_alive():
                    logger.info("[HEALTH CHECK] Polling thread stopped - health check monitor is not running")
                    logger.info("[HEALTH CHECK] Restarting health_check_monitor thread...")
                    try:
                        self.health_check_stop_event.clear()
                        self.health_check_thread = threading.Thread(
                            target=self.health_check_monitor,
                            daemon=False,
                            name="health_check_monitor"
                        )
                        self.health_check_thread.start()
                        logger.info(f"[THREAD START] health_check_monitor thread restarted (ID: {self.health_check_thread.ident})")
                    except Exception as hc_error:
                        logger.error(f"Failed to restart health_check_monitor: {hc_error}", exc_info=True)
                else:
                    logger.info("[HEALTH CHECK] Polling thread stopped but health check monitor is still running")
            else:
                logger.info("[HEALTH CHECK] Monitoring was intentionally stopped (health_check_stop_event is set)")

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
            symbol_config = symbol_config or config.get_default_symbol_config()
            
            # Handle backward compatibility: if old format (symbol -> poll_seconds), convert to new format
            if symbol_config and isinstance(next(iter(symbol_config.values())), list):
                default_strikes = default_strikes or config.DEFAULT_STRIKES
                converted_config = {}
                for symbol, poll_secs in symbol_config.items():
                    converted_config[symbol] = {"poll_seconds": poll_secs, "strikes": default_strikes}
                symbol_config = converted_config

            # Validate symbol configuration
            is_valid, validation_msg = config.validate_symbol_config(symbol_config)
            if not is_valid:
                logger.error(f"Invalid symbol config: {validation_msg}")
                return False, validation_msg
            
            # Set default strikes for backward compatibility
            self.number_of_strikes = default_strikes or config.DEFAULT_STRIKES

            self.stop_event.clear()
            self.current_symbols = symbol_config.copy()
            self.current_watchers = {}
            self.current_managers = {}

            # Start polling in a thread
            self.monitor_thread = threading.Thread(
                target=self.poll_option_chain,
                args=(symbol_config,),
                daemon=False,
                name="fetch_monitor"
            )
            self.monitor_thread.start()
            logger.info(f"[THREAD START] fetch_monitor thread started (ID: {self.monitor_thread.ident})")

            # Save config for health check restart
            self.saved_symbol_config = symbol_config.copy()
            
            # Start health check monitor if not already running
            if not self.health_check_thread or not self.health_check_thread.is_alive():
                self.health_check_stop_event.clear()
                self.health_check_thread = threading.Thread(
                    target=self.health_check_monitor,
                    daemon=False,
                    name="health_check_monitor"
                )
                self.health_check_thread.start()
                logger.info(f"[THREAD START] health_check_monitor thread started (ID: {self.health_check_thread.ident})")

            # logger.info(f"Monitor started: symbols={list(symbol_config.keys())}")
            # for symbol, config_data in symbol_config.items():
            #     logger.info(f"  {symbol}: poll at seconds {config_data['poll_seconds']}, strikes: {config_data['strikes']}")
            return True, 'Monitor started'

        except Exception as e:
            logger.error(f"Start error: {str(e)}", exc_info=True)
            # Clean up if thread was started but error occurred
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
            poll_secs = poll_secs or [0, 30]  # Default to 30 seconds
            strikes = strikes or config.DEFAULT_STRIKES  # Default strikes

            if not new_symbol or not new_symbol.strip():
                return False, 'Symbol not provided', {}
            
            # Validate single symbol config
            temp_config = {new_symbol: {"poll_seconds": poll_secs, "strikes": strikes}}
            is_valid, validation_msg = config.validate_symbol_config(temp_config)
            if not is_valid:
                return False, validation_msg, {}

            with self.state_lock:
                if new_symbol in self.current_symbols:
                    logger.info(f"Symbol {new_symbol} already being monitored")
                    return True, f'Symbol {new_symbol} already being monitored', self.current_symbols
                
                # Check max symbols limit
                if len(self.current_symbols) >= config.MAX_SYMBOLS:
                    return False, f'Maximum {config.MAX_SYMBOLS} symbols reached', self.current_symbols

                # Initialize watcher and manager for new symbol
                try:
                    self.current_watchers[new_symbol] = PriceWatcher('option-chain')
                    symbol_name = FileUtils.get_symbol_name(new_symbol)
                    self.current_managers[new_symbol] = OptionChainManager(db_file=f"{symbol_name}.db")
                    
                    # Add to symbols dict with poll interval and strikes
                    self.current_symbols[new_symbol] = {"poll_seconds": poll_secs, "strikes": strikes}
                except Exception as init_error:
                    # Cleanup partial initialization
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
            self.health_check_stop_event.set()
            self.saved_symbol_config = None

            if self.monitor_thread:
                logger.info(f"[THREAD STOP] Waiting for fetch_monitor thread (ID: {self.monitor_thread.ident}) to stop...")
                self.monitor_thread.join(timeout=10)
                if self.monitor_thread.is_alive():
                    logger.warning(f"[THREAD TIMEOUT] fetch_monitor thread did not stop gracefully after 10s")
                else:
                    logger.info(f"[THREAD STOPPED] fetch_monitor thread stopped successfully")
            
            if self.health_check_thread:
                logger.info(f"[THREAD STOP] Waiting for health_check_monitor thread (ID: {self.health_check_thread.ident}) to stop...")
                self.health_check_thread.join(timeout=5)
                if self.health_check_thread.is_alive():
                    logger.warning(f"[THREAD TIMEOUT] health_check_monitor thread did not stop gracefully after 5s")
                else:
                    logger.info(f"[THREAD STOPPED] health_check_monitor thread stopped successfully")

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
                'health_check_running': self.health_check_thread.is_alive() if self.health_check_thread else False,
                'health_check_interval': self.health_check_interval
            }
