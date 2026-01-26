import time

from client.utils.option_chain_monitor import OptionChainMonitor

from .utils.config import Config
from .utils.logger_manager import LoggerManager

class OIDataFetchController:
    # ============================================================================
    # Global Configuration Instance
    # ============================================================================

    config = Config()
    def __init__(self):
        self.config = Config()
        self.cutoff_timer = None
        self._fetch_option_chain_data_called = False
        self.logger = LoggerManager.setup_logging("option-chain")
        self.option_chain_monitor = OptionChainMonitor()


    def setup_logging(self, name: str = "option-chain"):
        """Deprecated: Use LoggerManager.setup_logging() instead."""
        return LoggerManager.setup_logging(name)
    
    def _fetch_option_chain_data(self):
        """Fetch live data after 5 second delay."""
        if not self._fetch_option_chain_data_called:
            self._fetch_option_chain_data_called = True
            try:
                self.logger.info("Waiting 5 seconds before fetching option chain data...")
                time.sleep(5)
                self.logger.info("Fetching option chain data...")
                self.option_chain_monitor.start_monitoring()
                self.logger.info("Option chain data fetch completed")
            except Exception as e:
                self.logger.error(f"Error fetching option chain data: {e}", exc_info=True)
    
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
            if self.config.OPTION_MONITOR_ENABLED:
                self._fetch_option_chain_data()      
        except Exception as e:
            self.logger.error(f"Error Auto-start error: {e}", exc_info=True)     

if __name__ == "__main__":
    app = OIDataFetchController()
    app.run()       