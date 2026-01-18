import datetime
import logging
from typing import Dict, Any, Callable

from client.watchlist import PriceWatcher
from client.utils.config import Config
from client.utils.file_utils import FileUtils
from nslogger.history_data_manager import HistoryDataManager

config = Config()
logger = logging.getLogger("live")

class LivePriceFetcher:
    """Manage live price subscriptions and logging from Fyers."""

    def __init__(self):
        """
        Initialize Live Price Fetcher.
        
        Args:
            watchers: Dictionary of PriceWatcher instances by symbol
        """
        self.price_watcher = PriceWatcher('live')
        self.sql_data_manager: Dict[str, HistoryDataManager] = {}
        
        # Get symbols from config if configured, otherwise use watchers
        if config.LIVE_DATA_SYMBOLS:
            # Use configured symbols from live_data section
            self.symbols = config.LIVE_DATA_SYMBOLS
            logger.info(f"LivePriceFetcher using configured symbols: {self.symbols}")
                
        # Initialize HistoryDataManager for live data logging
        try:
            for symbol in self.symbols:
                symbol_name = symbol.split(':')[-1] if ':' in symbol else symbol
                self.sql_data_manager[symbol_name] = HistoryDataManager(db_file = f"{symbol_name}.db")
            logger.info(f"HistoryDataManager initialized for live price logging")
        except Exception as e:
            logger.error(f"Failed to initialize HistoryDataManager: {e}")
            self.sql_data_manager = None
        
        # Track subscribed symbols
        self.subscribed_symbols = set()
        self.active_subscriptions = {}  # {symbol: callback}
    
        
    def insert_live_price_to_db(self, data: Dict[str, Any], symbol: str) -> bool:
        """
        Insert live price data to the database and CSV using HistoryDataManager.
        
        Args:
            data: Dictionary with live price data
            symbol: Stock symbol
            
        Returns:
            bool: True if insertion successful, False otherwise
        """
        try:
            if not data or not symbol:
                logger.warning(f"No data to insert for {symbol}")
                return False           
            

            # Check if HistoryDataManager is available
            if self.sql_data_manager is None:
                logger.error(f"HistoryDataManager not available for {symbol}")
                return False

            symbol_name = symbol.split(':')[-1] if ':' in symbol else symbol
            if symbol_name not in self.sql_data_manager:
                logger.error(f"No HistoryDataManager instance for {symbol}")
                return False
            
            # Use HistoryDataManager's insert method
            # For tick data or price snapshots
            dmg: HistoryDataManager = self.sql_data_manager[symbol_name]
            dmg.insert_historical_data([data], 'live_data')
            logger.info(f"Logged live price to database for {symbol}")
            
            # Save to CSV if enabled
            if config.LIVE_DATA_CSV_EXPORT_ENABLED:
                self._save_live_price_to_csv(data, symbol)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in insert_live_price_to_db for {symbol}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _save_live_price_to_csv(self, data: Dict[str, Any], symbol: str) -> None:
        """
        Save live price data to CSV file.
        
        Args:
            data: Dictionary with live price data
            symbol: Stock symbol
        """
        try:
            # Get CSV file path and append data using FileUtils
            file_path = FileUtils.get_csv_file_path(symbol, data_type='LIVE')
            FileUtils.append_dict_to_csv(data, file_path)
            
        except Exception as e:
            logger.error(f"Error saving live price to CSV for {symbol}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _convert_live_price_message(self, symbol: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Fyers WebSocket message to database format.
        
        Args:
            symbol: Stock symbol
            message: Raw message from Fyers WebSocket
            
        Returns:
            dict: Formatted data for database insertion
        """
        try:
            timestamp = int(datetime.datetime.now().timestamp())
            
            # Convert message to database format
            converted_data = {
                'timestamp': timestamp,
                'symbol': symbol,
                'ltp': message.get('ltp', 0),  # Last Traded Price
                'bid': message.get('bid', 0),
                'ask': message.get('ask', 0),
                'open': message.get('open', 0),
                'high': message.get('high', 0),
                'low': message.get('low', 0),
                'close': message.get('close', 0),
                'volume': message.get('volume', 0),
                'change': message.get('change', 0),
                'changep': message.get('changep', 0),
                'atp': message.get('atp', 0),  # Average Trade Price
                'spread': message.get('spread', 0),
                'exchange': message.get('exchange', ''),
                'created_at': datetime.datetime.now().isoformat()
            }
            
            return converted_data
        
        except Exception as e:
            logger.error(f"Error converting live price message for {symbol}: {e}")
            return {}

    def _live_price_callback(self, symbol: str, message: Dict[str, Any]) -> None:
        """
        Handle live price updates from WebSocket.
        
        Args:
            symbol: Stock symbol
            message: Price update message from Fyers
        """
        try:
            if not message:
                logger.warning(f"Empty message received for {symbol}")
                return
            
            ltp = message.get('ltp', 0)
            logger.debug(f"[LIVE PRICE] {symbol}: LTP = {ltp}")
            
            # Convert message to database format
            converted_data = self._convert_live_price_message(symbol, message)
            
            if not converted_data:
                logger.warning(f"Failed to convert message for {symbol}")
                return
            
            # Log to database if enabled
            if config.LIVE_DATA_ENABLED:
                self.insert_live_price_to_db(converted_data, symbol)
            
            # Additional processing can be added here
            # e.g., price analysis, alerts, etc.
        
        except Exception as e:
            logger.error(f"Error in live price callback for {symbol}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def subscribe_to_live_prices(self) -> None:
        """
        Subscribe to live price updates for all configured symbols.
        Uses WebSocket connection to stream real-time prices.
        """
        if not self.symbols:
            logger.warning("No symbols configured for live price subscription")
            return
        
        logger.info(f"Starting live price subscriptions for {len(self.symbols)} symbols: {self.symbols}")
        
        for symbol in self.symbols:
            try:
                # Check if symbol exists in watchers
                if not self.price_watcher:
                    logger.warning(f"Symbol {symbol} not in available watchers")
                    continue
                
                # Check if already subscribed
                if symbol in self.subscribed_symbols:
                    logger.debug(f"Symbol {symbol} already subscribed")
                    continue
                
                
                # Subscribe to live prices
                success = self.price_watcher.subscribe_to_price(
                    symbol, self._live_price_callback           
                )
                
                if success:
                    self.subscribed_symbols.add(symbol)
                    logger.info(f"Subscribed to live prices for {symbol}")
                else:
                    logger.warning(f"Failed to subscribe to live prices for {symbol}")
            
            except Exception as e:
                logger.error(f"Error subscribing to {symbol}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

    def unsubscribe_from_live_prices(self) -> None:
        """
        Unsubscribe from live price updates for all symbols.
        Closes WebSocket connection and stops price streaming.
        """
        logger.info(f"Stopping live price subscriptions for {len(self.subscribed_symbols)} symbols")
        
        for symbol in list(self.subscribed_symbols):
            try:
                if not self.price_watcher:
                    logger.warning(f"Symbol {symbol} not in available watchers")
                    self.subscribed_symbols.discard(symbol)
                    self.active_subscriptions.pop(symbol, None)
                    continue
                
                # Unsubscribe from live prices
                success = self.price_watcher.unsubscribe_from_price(symbol)
                
                if success:
                    self.subscribed_symbols.discard(symbol)
                    self.active_subscriptions.pop(symbol, None)
                    logger.info(f"Unsubscribed from live prices for {symbol}")
                else:
                    logger.warning(f"Failed to unsubscribe from {symbol}")
            
            except Exception as e:
                logger.error(f"Error unsubscribing from {symbol}: {e}")
                # Force remove even if unsubscribe failed
                self.subscribed_symbols.discard(symbol)
                self.active_subscriptions.pop(symbol, None)
        
        logger.info("All live price subscriptions stopped")

    def subscribe_with_custom_callback(self, symbol: str, callback: Callable[[str, Dict[str, Any]], None]) -> bool:
        """
        Subscribe to live prices with a custom callback function.
        
        Args:
            symbol: Stock symbol to subscribe to
            callback: Custom callback function(symbol, message)
            
        Returns:
            bool: True if subscription successful, False otherwise
        """
        try:
            if not self.price_watcher:
                logger.warning(f"Symbol {symbol} not in available watchers")
                return False
            
            if symbol in self.subscribed_symbols:
                logger.warning(f"Symbol {symbol} already subscribed")
                return False
            
            # Subscribe with custom callback
            success = self.price_watcher.subscribe_to_price(symbol, callback)
            
            if success:
                self.subscribed_symbols.add(symbol)
                self.active_subscriptions[symbol] = callback
                logger.info(f"Subscribed to live prices for {symbol} with custom callback")
                return True
            else:
                logger.warning(f"Failed to subscribe to {symbol} with custom callback")
                return False
        
        except Exception as e:
            logger.error(f"Error subscribing to {symbol} with custom callback: {e}")
            return False

    def unsubscribe_with_custom_callback(self, symbol: str) -> bool:
        """
        Unsubscribe from live prices for a specific symbol.
        
        Args:
            symbol: Stock symbol to unsubscribe from
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        try:
            if not self.price_watcher:
                logger.warning(f"Symbol {symbol} not in available watchers")
                return False
            
            if symbol not in self.subscribed_symbols:
                logger.warning(f"Symbol {symbol} not subscribed")
                return False
            
            # Unsubscribe from live prices
            success = self.price_watcher.unsubscribe_from_price(symbol)
            
            if success:
                self.subscribed_symbols.discard(symbol)
                self.active_subscriptions.pop(symbol, None)
                logger.info(f"Unsubscribed from live prices for {symbol}")
                return True
            else:
                logger.warning(f"Failed to unsubscribe from {symbol}")
                return False
        
        except Exception as e:
            logger.error(f"Error unsubscribing from {symbol}: {e}")
            return False

    def get_subscription_status(self) -> Dict[str, Any]:
        """
        Get current subscription status.
        
        Returns:
            dict: Status information about live price subscriptions
        """
        return {
            'total_symbols': len(self.symbols),
            'subscribed_count': len(self.subscribed_symbols),
            'subscribed_symbols': list(self.subscribed_symbols),
            'configured_symbols': self.symbols,
            'history_manager_available': self.sql_data_manager is not None,
            'active_subscriptions': list(self.active_subscriptions.keys())
        }

    def cleanup(self) -> None:
        """
        Clean up resources and close all subscriptions.
        """
        try:
            logger.info("Cleaning up LivePriceFetcher resources...")
            self.unsubscribe_from_live_prices()
            self.subscribed_symbols.clear()
            self.active_subscriptions.clear()
            
            logger.info("LivePriceFetcher cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
