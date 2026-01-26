import time

from .utils.live_price_fetcher import LivePriceFetcher
from .utils.config import Config
from .utils.logger_manager import LoggerManager
from .utils.program_manager import ProgramManager
from .utils.watchdog import Watchdog

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
        self.watchdog = Watchdog(logger=self.logger)
        self.live_price_fetcher = LivePriceFetcher(watchdog=self.watchdog)
        self.program_manager = ProgramManager(logger=self.logger)
        

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
                self.logger.info("Live data subscription completed successfully")
                
                # Start idle monitoring for price feeds - monitors if WebSocket stops sending callbacks
                self.logger.info("Starting idle monitoring for live price feeds")
                self.watchdog.start_idle_monitoring()
                
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
            self.logger.error(f"Error in run(): {e}", exc_info=True)
            # Restart program when crash occurs
            self.program_manager.restart_current_program(delay=5)   
    def test_bat(self):
        try:  
            import os
            import subprocess
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.logger.info(f"Script directory: {script_dir}")
            
            # The bat file is located in the same directory as this script when installed
            bat_path = os.path.join(script_dir, 'launch_python_program.bat')
            
            if os.path.exists(bat_path):
                self.logger.info(f"Bat file exists at: {bat_path}")
                subprocess.run([bat_path])  
            else:
                self.logger.error(f"Bat file does not exist at: {bat_path}")

        except Exception as e:
            self.logger.error(f"Error in test_bat(): {e}", exc_info=True)

    def cleanup(self):
        """Clean up resources."""
        try:
            self.logger.info("Cleaning up LiveDataFetchController resources...")
            if hasattr(self, 'live_price_fetcher'):
                self.live_price_fetcher.cleanup()
            if hasattr(self, 'watchdog'):
                self.watchdog.cleanup()
            self.logger.info("LiveDataFetchController cleanup complete")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)

if __name__ == "__main__":
    app = LiveDataFetchController()
    # try:
    #     app.test_bat()
    # except Exception as e:
    #     app.logger.error(f"Error in test_bat(): {e}", exc_info=True)
    
    try:
        app.run()
    except KeyboardInterrupt:
        app.logger.info("Received keyboard interrupt, cleaning up...")
        app.cleanup()
    except Exception as e:
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        app.cleanup()       