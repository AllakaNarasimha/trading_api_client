import logging
from logging.handlers import RotatingFileHandler
import os
import threading
import time

from .utils.live_price_fetcher import LivePriceFetcher
from .utils.config import Config
from .utils.logger_manager import LoggerManager

class LiveDataFetchController:
    # ============================================================================
    # Global Configuration Instance
    # ============================================================================

    config = Config()
    def __init__(self):
        self.config = Config()
        self.cutoff_timer = None
        self._fetch_live_data_called = False
        self.logger = LoggerManager.setup_logging("live")
        self.live_price_fetcher = LivePriceFetcher()

    def setup_logging(self, name: str = "live"):
        """Deprecated: Use LoggerManager.setup_logging() instead."""
        return LoggerManager.setup_logging(name)
    
    def _fetch_live_data(self):
        """Fetch live data after 5 second delay."""
        thread_timeout = 30  # seconds
        if not self._fetch_live_data_called:
            self._fetch_live_data_called = True
            try:
                self.logger.info(f"Waiting {thread_timeout} seconds before fetching live data...")
                time.sleep(5)
                self.logger.info("Fetching live data...")
                self.live_price_fetcher.subscribe_to_live_prices()
                self.logger.info("Live data fetch completed")
            except Exception as e:
                self.logger.error(f"Error fetching live data: {e}", exc_info=True)
    
    def authorize_broker(self) -> bool:
        from .auth import get_auth_manager
        auth_manager = get_auth_manager()
        if auth_manager.is_authenticated:
            self.logger.info("Broker authorization successful")
            return True
        return False
        
    def run(self) -> None:
        # Authorize broker before starting
        while self.authorize_broker() == False:
            time.sleep(5)
            self.logger.info("Retrying broker authorization...")    
        self.logger.info("Broker authorized successfully")
        
        try:  
            # Initiate live data fetch if enabled
            if self.config.LIVE_DATA_ENABLED:
                self._fetch_live_data()      
        except Exception as e:
            self.logger.error(f"Error Auto-start error: {e}", exc_info=True)     

if __name__ == "__main__":
    app = LiveDataFetchController()
    app.run()       