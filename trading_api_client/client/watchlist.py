"""Price Watcher Module

Monitors and watches price movements across brokers.
"""

import logging
from client.auth import get_auth_manager
from client.utils.logger_factory import LoggerFactory
from typing import Dict, Any, List, Callable, Union

logger = logging.getLogger(__name__)


class PriceWatcher:
    """Watch prices across multiple brokers."""
    
    def __init__(self, context: str = None):
        """Initialize price watcher with authenticated clients.
        
        Args:
            context: Optional context name for logging ('live', 'history', 'option-chain').
                    If not provided, uses default 'price_watcher' logger.
        """
        self.auth_manager = get_auth_manager()
        self.price_watcher = self.auth_manager.price_watcher
        self.watchlist = []
        
        # Get context-aware logger
        self.logger = LoggerFactory.get_logger(context)
    
    def add_to_watchlist(self, symbol):
        """Add symbol to watchlist."""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
            self.subscribe_to_price(symbol)
            self.subscribe_to_depth(symbol)
            self.logger.info(f"Added {symbol} to watchlist")
    
    def remove_from_watchlist(self, symbol):
        """Remove symbol from watchlist."""
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            self.unsubscribe_from_price(symbol)
            self.unsubscribe_from_depth(symbol)
            self.logger.info(f"Removed {symbol} from watchlist")
    
    def get_price(self, symbol):
        """Get current price for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return {"symbol": symbol, "price": None, "broker": "fyers", "error": "Not authenticated"}
            
            self.logger.info(f"Fetching price for {symbol}...")
            # Use price watcher interface to get price
            price_data = self.price_watcher.get_price(symbol)
            return {"symbol": symbol, "price": price_data, "broker": "fyers"}
        except Exception as e:
            self.logger.error(f"Failed to get price: {e}")
            return {"symbol": symbol, "price": None, "broker": "fyers", "error": str(e)}
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get quotes for multiple symbols."""
        try:
            if not self.price_watcher:
                self.logger.warning("Price watcher not available")
                return {}
            
            self.logger.info(f"Fetching quotes for {symbols}...")
            return self.price_watcher.get_quotes(symbols)
        except Exception as e:
            self.logger.error(f"Failed to get quotes: {e}")
            return {}
    
    def ltp_callback(self, symbol, message):
        """Callback for LTP updates."""
        self.logger.info(f"LTP update for {symbol}:")
        self.logger.info(f"  ltp: {message.get('ltp')}")
        self.logger.info(f"  vol_traded_today: {message.get('vol_traded_today')}")
        self.logger.info(f"  last_traded_time: {message.get('last_traded_time')}")
        self.logger.info(f"  exch_feed_time: {message.get('exch_feed_time')}")
        self.logger.info(f"  bid_size: {message.get('bid_size')}")
        self.logger.info(f"  ask_size: {message.get('ask_size')}")
        self.logger.info(f"  bid_price: {message.get('bid_price')}")
        self.logger.info(f"  ask_price: {message.get('ask_price')}")
        self.logger.info(f"  last_traded_qty: {message.get('last_traded_qty')}")
        self.logger.info(f"  tot_buy_qty: {message.get('tot_buy_qty')}")
        self.logger.info(f"  tot_sell_qty: {message.get('tot_sell_qty')}")
        self.logger.info(f"  avg_trade_price: {message.get('avg_trade_price')}")
        self.logger.info(f"  low_price: {message.get('low_price')}")
        self.logger.info(f"  high_price: {message.get('high_price')}")
        self.logger.info(f"  lower_ckt: {message.get('lower_ckt')}")
        self.logger.info(f"  upper_ckt: {message.get('upper_ckt')}")
        self.logger.info(f"  open_price: {message.get('open_price')}")
        self.logger.info(f"  prev_close_price: {message.get('prev_close_price')}")
        self.logger.info(f"  type: {message.get('type')}")
        self.logger.info(f"  symbol: {message.get('symbol')}")
        self.logger.info(f"  ch: {message.get('ch')}")
        self.logger.info(f"  chp: {message.get('chp')}")
    
    def subscribe_to_price(self, symbol: str, ltp_callback) -> bool:
        """Subscribe to real-time LTP price updates for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return False
            
            self.logger.info(f"Subscribing to price updates for {symbol}...")
            if not ltp_callback:
                ltp_callback = self.ltp_callback
            return self.price_watcher.subscribe_to_price(symbol, ltp_callback)
        except Exception as e:
            self.logger.error(f"Failed to subscribe to price: {e}")
            return False
    
    def unsubscribe_from_price(self, symbol: str) -> bool:
        """Unsubscribe from LTP price updates for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return False
            
            self.logger.info(f"Unsubscribing from price updates for {symbol}...")
            return self.price_watcher.unsubscribe_from_price(symbol)
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from price: {e}")
            return False
    
    def price_depth_callback(self, ticker, message):
        """Callback function for depth updates."""
        self.logger.info(f"Depth update for {ticker}:")
        self.logger.info(f"  send_ts: {message.sendtime}")
        self.logger.info(f"  tbq: {message.tbq}")
        self.logger.info(f"  tsq: {message.tsq}")
        self.logger.info(f"  bidprice: {message.bidprice[:5]}")  # Show first 5 levels
        self.logger.info(f"  askprice: {message.askprice[:5]}")
        self.logger.info(f"  bidqty: {message.bidqty[:5]}")
        self.logger.info(f"  askqty: {message.askqty[:5]}")
        self.logger.info(f"  snapshot: {message.snapshot}")
        self.logger.info(f"  sNo: {message.seqNo}")

    def subscribe_to_depth(self, symbol: str) -> bool:
        """Subscribe to real-time depth (order book) updates for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return False
            
            self.logger.info(f"Subscribing to depth updates for {symbol}...")
            return self.price_watcher.subscribe_to_depth(symbol, self.price_depth_callback)
        except Exception as e:
            self.logger.error(f"Failed to subscribe to depth: {e}")
            return False
    
    def unsubscribe_from_depth(self, symbol: str) -> bool:
        """Unsubscribe from depth updates for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return False
            
            self.logger.info(f"Unsubscribing from depth updates for {symbol}...")
            return self.price_watcher.unsubscribe_from_depth(symbol)
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from depth: {e}")
            return False
    
    def get_historical_data(self, symbol: str, resolution: str, date_format: str, period_start: int, period_end: int, cont_flag: str = "1") -> Union[List[List[Any]], str]:
        """Get historical price data for a symbol.
        
        Returns:
            List[List[Any]]: Historical price data in format [timestamp, open, high, low, close, volume, oi]
            str: Error message if operation fails
        """
        try:
            if not self.price_watcher:
                error_msg = f"Price watcher not available for {symbol}"
                self.logger.warning(error_msg)
                return error_msg
            
            self.logger.info(f"Fetching historical data for {symbol}...")
            return self.price_watcher.get_historical_data(symbol, resolution, date_format, period_start, period_end, cont_flag)
        except Exception as e:
            error_msg = f"Failed to get historical data: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def get_option_chain(self, symbol: str, strikecount: int = 1) -> Dict[str, Any]:
        """Get option chain for a symbol."""
        try:
            if not self.price_watcher:
                self.logger.warning(f"Price watcher not available for {symbol}")
                return {}
            
            self.logger.info(f"Fetching option chain for {symbol}...")
            return self.price_watcher.get_option_chain(symbol, strikecount)
        except Exception as e:
            self.logger.error(f"Failed to get option chain: {e}")
            return {}
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status (open/closed)."""
        try:
            if not self.price_watcher:
                self.logger.warning("Price watcher not available")
                return {}
            
            self.logger.info("Fetching market status...")
            return self.price_watcher.get_market_status()
        except Exception as e:
            self.logger.error(f"Failed to get market status: {e}")
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
            self.logger.error(f"Failed to check market status: {e}")
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
    watcher = PriceWatcher('watchlist')
    watcher.logger.info("\n[Price Watcher]")
    watcher.add_to_watchlist("RELIANCE")
    watcher.add_to_watchlist("TCS")
    watcher.add_to_watchlist("INFY")
    
    prices = watcher.get_all_prices()
    watcher.logger.info(f"\n[Watchlist] {watcher.watchlist}")


if __name__ == "__main__":
    main()
