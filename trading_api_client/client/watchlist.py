"""Price Watcher Module

Monitors and watches price movements across brokers.
"""

from client.auth import get_auth_manager
from typing import Dict, Any, List, Callable


class PriceWatcher:
    """Watch prices across multiple brokers."""
    
    def __init__(self):
        """Initialize price watcher with authenticated clients."""
        self.auth_manager = get_auth_manager()
        self.price_watcher = self.auth_manager.price_watcher
        self.watchlist = []
    
    def add_to_watchlist(self, symbol):
        """Add symbol to watchlist."""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
            self.subscribe_to_price(symbol)
            self.subscribe_to_depth(symbol)
            print(f"[INFO] Added {symbol} to watchlist")
    
    def remove_from_watchlist(self, symbol):
        """Remove symbol from watchlist."""
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            self.unsubscribe_from_price(symbol)
            self.unsubscribe_from_depth(symbol)
            print(f"[INFO] Removed {symbol} from watchlist")
    
    def get_price(self, symbol):
        """Get current price for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return {"symbol": symbol, "price": None, "broker": "fyers", "error": "Not authenticated"}
            
            print(f"[INFO] Fetching price for {symbol}...")
            # Use price watcher interface to get price
            price_data = self.price_watcher.get_price(symbol)
            return {"symbol": symbol, "price": price_data, "broker": "fyers"}
        except Exception as e:
            print(f"[ERROR] Failed to get price: {e}")
            return {"symbol": symbol, "price": None, "broker": "fyers", "error": str(e)}
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get quotes for multiple symbols."""
        try:
            if not self.price_watcher:
                print("[WARNING] Price watcher not available")
                return {}
            
            print(f"[INFO] Fetching quotes for {symbols}...")
            return self.price_watcher.get_quotes(symbols)
        except Exception as e:
            print(f"[ERROR] Failed to get quotes: {e}")
            return {}
    
    def ltp_callback(self, symbol, message):
        """Callback for LTP updates."""
        print(f"  [LTP] {symbol}:")
        print(f"    ltp: {message.get('ltp')}")
        print(f"    vol_traded_today: {message.get('vol_traded_today')}")
        print(f"    last_traded_time: {message.get('last_traded_time')}")
        print(f"    exch_feed_time: {message.get('exch_feed_time')}")
        print(f"    bid_size: {message.get('bid_size')}")
        print(f"    ask_size: {message.get('ask_size')}")
        print(f"    bid_price: {message.get('bid_price')}")
        print(f"    ask_price: {message.get('ask_price')}")
        print(f"    last_traded_qty: {message.get('last_traded_qty')}")
        print(f"    tot_buy_qty: {message.get('tot_buy_qty')}")
        print(f"    tot_sell_qty: {message.get('tot_sell_qty')}")
        print(f"    avg_trade_price: {message.get('avg_trade_price')}")
        print(f"    low_price: {message.get('low_price')}")
        print(f"    high_price: {message.get('high_price')}")
        print(f"    lower_ckt: {message.get('lower_ckt')}")
        print(f"    upper_ckt: {message.get('upper_ckt')}")
        print(f"    open_price: {message.get('open_price')}")
        print(f"    prev_close_price: {message.get('prev_close_price')}")
        print(f"    type: {message.get('type')}")
        print(f"    symbol: {message.get('symbol')}")
        print(f"    ch: {message.get('ch')}")
        print(f"    chp: {message.get('chp')}")
    
    def subscribe_to_price(self, symbol: str) -> bool:
        """Subscribe to real-time LTP price updates for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return False
            
            print(f"[INFO] Subscribing to price updates for {symbol}...")
            return self.price_watcher.subscribe_to_price(symbol, self.ltp_callback)
        except Exception as e:
            print(f"[ERROR] Failed to subscribe to price: {e}")
            return False
    
    def unsubscribe_from_price(self, symbol: str) -> bool:
        """Unsubscribe from LTP price updates for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return False
            
            print(f"[INFO] Unsubscribing from price updates for {symbol}...")
            return self.price_watcher.unsubscribe_from_price(symbol)
        except Exception as e:
            print(f"[ERROR] Failed to unsubscribe from price: {e}")
            return False
    
    def price_depth_callback(self, ticker, message):
        """Callback function for depth updates."""
        print(f"  [DEPTH] {ticker}:")
        print(f"    send_ts: {message.sendtime}")
        print(f"    tbq: {message.tbq}")
        print(f"    tsq: {message.tsq}")
        print(f"    bidprice: {message.bidprice[:5]}")  # Show first 5 levels
        print(f"    askprice: {message.askprice[:5]}")
        print(f"    bidqty: {message.bidqty[:5]}")
        print(f"    askqty: {message.askqty[:5]}")
        print(f"    snapshot: {message.snapshot}")
        print(f"    sNo: {message.seqNo}")

    def subscribe_to_depth(self, symbol: str) -> bool:
        """Subscribe to real-time depth (order book) updates for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return False
            
            print(f"[INFO] Subscribing to depth updates for {symbol}...")
            return self.price_watcher.subscribe_to_depth(symbol, self.price_depth_callback)
        except Exception as e:
            print(f"[ERROR] Failed to subscribe to depth: {e}")
            return False
    
    def unsubscribe_from_depth(self, symbol: str) -> bool:
        """Unsubscribe from depth updates for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return False
            
            print(f"[INFO] Unsubscribing from depth updates for {symbol}...")
            return self.price_watcher.unsubscribe_from_depth(symbol)
        except Exception as e:
            print(f"[ERROR] Failed to unsubscribe from depth: {e}")
            return False
    
    def get_historical_data(self, symbol: str, resolution: str, date_format: str, period_start: int, period_end: int, cont_flag: str = "1") -> List[List[Any]]:
        """Get historical price data for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return []
            
            print(f"[INFO] Fetching historical data for {symbol}...")
            return self.price_watcher.get_historical_data(symbol, resolution, date_format, period_start, period_end, cont_flag)
        except Exception as e:
            print(f"[ERROR] Failed to get historical data: {e}")
            return []
    
    def get_option_chain(self, symbol: str, strikecount: int = 1) -> Dict[str, Any]:
        """Get option chain for a symbol."""
        try:
            if not self.price_watcher:
                print(f"[WARNING] Price watcher not available for {symbol}")
                return {}
            
            print(f"[INFO] Fetching option chain for {symbol}...")
            return self.price_watcher.get_option_chain(symbol, strikecount)
        except Exception as e:
            print(f"[ERROR] Failed to get option chain: {e}")
            return {}
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status (open/closed)."""
        try:
            if not self.price_watcher:
                print("[WARNING] Price watcher not available")
                return {}
            
            print("[INFO] Fetching market status...")
            return self.price_watcher.get_market_status()
        except Exception as e:
            print(f"[ERROR] Failed to get market status: {e}")
            return {}
    
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        try:
            market_status = self.get_market_status()
            if not market_status:
                return False
            
            # Check if equity or derivatives market is open
            equity_open = market_status.get('equity', {}).get('is_open', False)
            derivatives_open = market_status.get('derivatives', {}).get('is_open', False)
            
            is_open = equity_open or derivatives_open
            return is_open
        except Exception as e:
            print(f"[ERROR] Failed to check market status: {e}")
            return False
    
    def get_all_prices(self):
        """Get prices for all symbols in watchlist."""
        prices = {}
        for symbol in self.watchlist:
            prices[symbol] = self.get_price(symbol)
        return prices
    
    def subscribe_watchlist_to_price(self, callback: Callable) -> bool:
        """Subscribe to price updates for all symbols in watchlist."""
        success = True
        for symbol in self.watchlist:
            if not self.subscribe_to_price(symbol, callback):
                success = False
        return success
    
    def unsubscribe_watchlist_from_price(self) -> bool:
        """Unsubscribe from price updates for all symbols in watchlist."""
        success = True
        for symbol in self.watchlist:
            if not self.unsubscribe_from_price(symbol):
                success = False
        return success


def main():
    """Main function for watchlist module."""
    watcher = PriceWatcher()
    print("\n[Price Watcher]")
    watcher.add_to_watchlist("RELIANCE")
    watcher.add_to_watchlist("TCS")
    watcher.add_to_watchlist("INFY")
    
    prices = watcher.get_all_prices()
    print(f"\n[Watchlist] {watcher.watchlist}")


if __name__ == "__main__":
    main()
