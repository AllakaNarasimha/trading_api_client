import datetime
import logging
from typing import Dict

from client.watchlist import PriceWatcher
from client.utils.config import Config
from client.utils.file_utils import FileUtils
from nslogger.history_data_manager import HistoryDataManager

logger = logging.getLogger(__name__)
config = Config()

class HistoricalDataFetcher:

    def __init__(self, watchers: Dict[str, PriceWatcher]):
        self.watchers = watchers
        self.sql_data_manager: Dict[str, HistoryDataManager] = {}
        
        # Get symbols from config if configured, otherwise use watchers
        if config.HISTORICAL_SYMBOLS:
            # Use configured historical symbols
            self.symbols = config.HISTORICAL_SYMBOLS
            logger.info(f"HistoricalDataFetcher using configured symbols: {self.symbols}")
        else:
            # Fall back to watcher symbols if no explicit config
            self.symbols = list(watchers.keys()) if watchers else []
            logger.info(f"HistoricalDataFetcher using watcher symbols: {self.symbols}")
        
        # Initialize HistoryDataManager for historical data logging
        try:
            self.history_manager = HistoryDataManager()
            logger.info(f"HistoryDataManager initialized successfully")
            for symbol in self.symbols:
                symbol_name = symbol.split(':')[-1] if ':' in symbol else symbol
                self.sql_data_manager[symbol_name] = HistoryDataManager(db_file = f"{symbol_name}.db")

        except Exception as e:
            logger.error(f"Failed to initialize HistoryDataManager: {e}")
            self.history_manager = None

    def insert_historical_data_to_db(self, data: list, symbol: str) -> bool:
        """Insert historical data to the database using HistoryDataManager.
        
        Args:
            data: List of dicts with historical data
            symbol: Stock symbol
            
        Returns:
            bool: True if insertion successful, False otherwise
        """
        try:
            if not data or len(data) == 0:
                logger.warning(f"No data to insert for {symbol}")
                return False
            
            # Check if HistoryDataManager is available
            if self.history_manager is None:
                logger.error(f"HistoryDataManager not available for {symbol}")
                return False
            
            # Use HistoryDataManager's insert_historical_data method
            self.history_manager.insert_historical_data(data)
            logger.info(f"Successfully logged {len(data)} historical data records to database for {symbol}")
            
            if self.sql_data_manager is None:
                logger.error(f"HistoryDataManager not available for {symbol}")
                return False

            symbol_name = symbol.split(':')[-1] if ':' in symbol else symbol
            if symbol_name not in self.sql_data_manager:
                logger.error(f"No HistoryDataManager instance for {symbol}")
                return False
            
            # For tick data or price snapshots
            dmg: HistoryDataManager = self.sql_data_manager[symbol_name]
            dmg.insert_historical_data(data)
            logger.debug(f"Logged live price to database for {symbol}")

            return True
            
        except Exception as e:
            logger.error(f"Error in insert_historical_data_to_db for {symbol}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def fetch_historical_data(self) -> None:
        """Fetch historical data for all configured symbols."""
        historical_data_enabled = config.HISTORICAL_DATA_ENABLED
        if not historical_data_enabled:
            logger.info("Historical data fetching is disabled")
            return

        if not self.symbols:
            logger.warning("No symbols available for historical data fetch")
            return

        historical_backdays = config.HISTORICAL_BACKDAYS
        historical_duration = config.HISTORICAL_DURATION
        
        logger.info(f"Starting historical data fetch for {len(self.symbols)} symbols: {self.symbols}")

        for historical_symbol in self.symbols:
            self._fetch_historical_data_for_symbol(historical_symbol, historical_backdays, historical_duration)

    def _fetch_historical_data_for_symbol(self, historical_symbol: str, historical_backdays: int, 
                                          historical_duration: int) -> None:
        """Fetch and save historical data for a single symbol.
        
        Args:
            historical_symbol: Symbol to fetch data for
            historical_backdays: Number of days to go back
            historical_duration: Duration interval in minutes
        """
        if not historical_symbol:
            logger.warning("Historical symbol not provided")
            return

        if historical_symbol not in self.watchers:
            logger.warning(f"Historical symbol {historical_symbol} not in available watchers")
            return

        # Get CSV file path using utility function
        file_path = FileUtils.get_csv_file_path(historical_symbol, data_type='HISTORY')

        try:
            # Calculate timestamps for historical data
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(days=historical_backdays)

            period_start = int(start_time.timestamp())
            period_end = int(end_time.timestamp())

            logger.info(f"Fetching historical data for {historical_symbol}: {historical_backdays} days back, {historical_duration}min intervals")

            # Fetch historical data
            historical_data = self.watchers[historical_symbol].get_historical_data(
                symbol=historical_symbol,
                resolution=str(historical_duration),
                date_format="0",  # 0 for timestamp format
                period_start=period_start,
                period_end=period_end
            )

            if historical_data:
                logger.info(f"Fetched {len(historical_data)} historical records for {historical_symbol}")
                
                # Convert list of lists to list of dicts if necessary
                converted_data = historical_data
                if historical_data and isinstance(historical_data, list) and len(historical_data) > 0:
                    if isinstance(historical_data[0], (list, tuple)):
                        # Data is in list/tuple format, convert to dict
                        # Common fields for stock historical data
                        dict_data = []
                        for row in historical_data:
                            if isinstance(row, (list, tuple)) and len(row) >= 5:
                                # Typical format: [timestamp, open, high, low, close, volume, oi]
                                dict_data.append({
                                    'timestamp': row[0] if len(row) > 0 else None,
                                    'open': row[1] if len(row) > 1 else None,
                                    'high': row[2] if len(row) > 2 else None,
                                    'low': row[3] if len(row) > 3 else None,
                                    'close': row[4] if len(row) > 4 else None,
                                    'volume': row[5] if len(row) > 5 else None,
                                    'oi': row[6] if len(row) > 6 else None,
                                    'symbol': historical_symbol
                                })
                        converted_data = dict_data
                
                # Log historical data to database using internal method
                try:
                    self.insert_historical_data_to_db(converted_data, historical_symbol)
                except Exception as e:
                    logger.error(f"Error logging historical data to database for {historical_symbol}: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    
                # Save historical data to CSV if enabled
                if config.HISTORICAL_CSV_EXPORT_ENABLED:
                    try:
                        # Use FileUtils to save CSV
                        success = FileUtils.save_dict_list_to_csv(converted_data, file_path, mode='w')
                        if success:
                            logger.info(f"Saved historical data to CSV: {file_path}")
                        else:
                            logger.warning(f"Failed to save historical data to CSV: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to save historical data to CSV: {e}")
            else:
                logger.warning(f"No historical data received for {historical_symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {historical_symbol}: {e}")
            logger.error(f"Historical data fetch failed - symbol: {historical_symbol}, backdays: {historical_backdays}, duration: {historical_duration}min")