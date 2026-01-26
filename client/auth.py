"""Authentication Module

Centralized authentication management for Dhan and Fyers APIs.
Provides authenticated client objects for use across the application.
"""

from time import sleep
import sys
from trading_api import DhanAPI, FyersAPI, Config, IAuthentication, IOrderManagement, IFundManagement, IPriceWatcher
from typing import Optional

from .utils.logger_manager import LoggerManager

class AuthManager:
    """Centralized authentication manager for trading APIs."""    
    def __init__(self, broker: str = "fyers"):
        """Initialize authentication manager."""
        self.config = Config()
        self.config.load_from_xml()
        self.logger = LoggerManager.setup_logging("auth_manager")
        config_data = self.config.get_all_config()
        self.broker = broker
        self.broker_config = config_data.get(broker, {})
        
        if broker == 'dhan':
            self.auth: IAuthentication = DhanAPI()
        if broker == 'fyers':
            self.auth: IAuthentication = FyersAPI()            
            self._orders: IOrderManagement = self.auth
            self._funds: IFundManagement = self.auth
            self._price_watcher: IPriceWatcher  = self.auth

        # Authenticated client instances
        self.dhan_client: Optional[DhanAPI] = None
        self.fyers_client: Optional[FyersAPI] = None

        # Authentication status
        self.is_authenticated = False

        # Initialize authentication
        self._initialize_auth()
    
    def setup_logging(self, name: str = "auth_manager"):
        """Deprecated: Use LoggerManager.setup_logging() instead."""
        return LoggerManager.setup_logging(name)
    

    def _initialize_auth(self):
        """Initialize authentication for all brokers."""
        self.logger.info("Initializing authentication manager...")

        # Authenticate
        auth_result = self.auth.authenticate(self.broker_config)
        if auth_result[0] == "success":
            self.is_authenticated = True
        else:
            self.is_authenticated = False

        self.logger.info(f"authenticated: {self.is_authenticated}")
        self.logger.info("Authentication initialization complete")        

    def get_order_manager(self):
        """Get order management interface (Fyers)."""
        return self._orders if self.is_authenticated else None

    def get_fund_manager(self):
        """Get fund management interface (Fyers)."""
        return self._funds if self.is_authenticated else None
    
    def get_price_watcher_interface(self):
        """Get price watcher interface (Fyers)."""
        return self._price_watcher if self.is_authenticated else None

    @property
    def orders(self):
        """Access order management interface."""
        return self._orders if self.is_authenticated else None

    @property
    def funds(self):
        """Access fund management interface."""
        return self._funds if self.is_authenticated else None

    @property
    def price_watcher(self):
        """Access price watcher interface."""
        return self._price_watcher if self.is_authenticated else None

    def authorize_broker(self) -> bool:
        from .auth import get_auth_manager
        auth_manager = get_auth_manager()
        if auth_manager.is_authenticated:
            self.logger.info("Broker authorization successful")
            return True
        return False
    
    def run(self) -> True:
        while self.authorize_broker() == False:
            sleep(5)
            self.logger.info("Retrying broker authorization...")    
        self.logger.info("Broker authorized successfully")
        sys.exit(0)


# Global authentication manager instance
_auth_manager = None

def get_auth_manager(broker: str = "fyers") -> AuthManager:
    """Get the global authentication manager instance."""
    global _auth_manager
    if _auth_manager is None or _auth_manager.broker != broker:
        _auth_manager = AuthManager(broker)
    elif not _auth_manager.is_authenticated:
        _auth_manager.logger.warning("Re-initializing authentication manager due to unauthenticated state.")
        _auth_manager = AuthManager(broker)

    return _auth_manager


if __name__ == "__main__":
    app = AuthManager()
    app.run() 
        