"""Portfolio Management Module

Manages holdings, cash, and portfolio analytics.
"""
from .auth import get_auth_manager


class Portfolio:
    """Manage trading portfolio across multiple brokers."""
    
    def __init__(self):
        """Initialize portfolio manager with authenticated clients."""
        self.auth_manager = get_auth_manager()
        
        # Set interfaces from auth manager
        self.funds = self.auth_manager.get_fund_manager()
        self.price_watcher = self.auth_manager.get_price_watcher_interface()
    
    def get_holdings(self):
        """Get Fyers holdings."""
        try:                        
            if not self.auth_manager.is_authenticated:
                print("[WARNING] Fyers not authenticated")
                return {"status": "error", "message": "Fyers not authenticated", "broker": "fyers"}
            
            print("[INFO] Fetching Fyers holdings...")
            # Get holdings from Fyers API
            holdings_data = self.funds.get_holdings()
            
            # Handle different response formats
            if isinstance(holdings_data, list):
                holdings = holdings_data
            elif isinstance(holdings_data, dict):
                if 'holdings' in holdings_data:
                    holdings = holdings_data['holdings']
                else:
                    holdings = []
            else:
                holdings = []
            
            if holdings:
                total_value = sum(float(h.get('marketVal', 0)) for h in holdings if h.get('marketVal'))
                total_quantity = sum(int(h.get('quantity', 0)) for h in holdings if h.get('quantity'))
                
                return {
                    "status": "success",
                    "broker": "fyers",
                    "holdings": holdings,
                    "total_value": total_value,
                    "total_quantity": total_quantity,
                    "count": len(holdings)
                }
            else:
                return {"status": "success", "broker": "fyers", "holdings": [], "total_value": 0, "total_quantity": 0, "count": 0}
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch Fyers holdings: {e}")
            return {"status": "error", "message": str(e), "broker": "fyers"}
    
    def get_auth_status(self):
        """Get authentication status."""
        return self.auth_manager.is_authenticated
    
    def get_total_portfolio(self):
        """Get total portfolio holdings."""
        return self.get_holdings()
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Main function for portfolio module."""
    portfolio = Portfolio()
    holdings = portfolio.get_total_portfolio()
    
    print("\n[Portfolio Analysis]")
    print("=" * 60)
    
    # Holdings
    data = holdings[portfolio.auth_manager.broker]
    if data.get('status') == 'success':
        print(f"\n[Holdings]")
        print(f"  Total Value: ₹{data.get('total_value', 0):,.2f}")
        print(f"  Total Quantity: {data.get('total_quantity', 0)}")
        print(f"  Number of Stocks: {data.get('count', 0)}")
        
        if data.get('holdings'):
            print("  Holdings:")
            for holding in data['holdings'][:5]:  # Show first 5
                symbol = holding.get('trading_symbol', holding.get('symbol', 'N/A'))
                qty = holding.get('quantity', 0)
                value = holding.get('totalValue', holding.get('marketVal', 0))
                print(f"    {symbol}: {qty} shares (₹{float(value):,.2f})")
            if len(data['holdings']) > 5:
                print(f"    ... and {len(data['holdings']) - 5} more")
    else:
        print(f"\n[Holdings] ERROR: {data.get('message', 'Unknown error')}")    