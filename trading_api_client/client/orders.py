"""Order Management Module

Manages buy/sell orders across multiple brokers.
"""

import logging
from client.auth import get_auth_manager

logger = logging.getLogger(__name__)

class OrderManager:
    """Manage orders across multiple brokers."""
    
    def __init__(self):
        """Initialize order manager with authenticated clients."""
        self.auth_manager = get_auth_manager()        
        self.orders = self.auth_manager.get_order_manager()

    def place_order(self, symbol, qty, price, order_type="BUY"):
        """Place order on Fyers broker."""
        try:
            if not self.orders:
                logger.error("Fyers not authenticated")
                return {"status": "error", "message": "Fyers not authenticated", "broker": "fyers"}
            
            logger.info(f"Placing Fyers {order_type} order: {symbol} x{qty} @ {price}")
            # Use orders interface to place order
            order_result = self.orders.place_order({
                "symbol": symbol,
                "quantity": qty,
                "price": price,
                "order_type": order_type
            })
            return {"status": "success", "broker": "fyers", "result": order_result}
        except Exception as e:
            logger.error(f"Fyers order failed: {e}")
            return {"status": "error", "message": str(e), "broker": "fyers"}
    
    def get_order_status(self, order_id, broker="dhan"):
        """Get status of an order."""
        logger.info(f"Fetching order {order_id} status from {broker}")
        return {"order_id": order_id, "status": "pending"}


def main():
    """Main function for orders module."""
    manager = OrderManager()
    logger.info("\n[Order Management]")
    manager.place_order("TCS", 1, 3500)


if __name__ == "__main__":
    main()
