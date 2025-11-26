import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple

class StockDataFetcher:
    """Fetches real-time stock data for semiconductor companies"""
    
    def __init__(self):
        # Map company names to their stock symbols
        self.company_symbols = {
            "NVIDIA": "NVDA", "TSMC": "TSM", "Intel": "INTC", "AMD": "AMD",
            "Qualcomm": "QCOM", "Broadcom": "AVGO", "Texas Instruments": "TXN",
            "ASML": "ASML", "Micron": "MU", "Analog Devices": "ADI",
            "Marvell": "MRVL", "KLA Corporation": "KLAC", "Applied Materials": "AMAT",
            "Lam Research": "LRCX", "MediaTek": "2454.TW", "SK Hynix": "000660.KS",
            "Samsung": "005930.KS", "Tokyo Electron": "8035.T", "SMIC": "0981.HK", "UMC": "UMC"
        }
        
    def get_stock_symbol(self, company_name: str) -> Optional[str]:
        """Get stock symbol for a company name"""
        # Direct symbol lookup
        if company_name.upper() in [s.upper() for s in self.company_symbols.values()]:
            return company_name.upper()
            
        # Company name lookup
        for name, symbol in self.company_symbols.items():
            if company_name.upper() in name.upper() or name.upper() in company_name.upper():
                return symbol
        return None
        
    def _fetch_stock_history(self, symbol: str, period: str = "1d", interval: str = "1m") -> Optional[Dict]:
        """Core function to fetch stock data - all other functions use this"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval, prepost=True)
            
            if (hist.empty):
                return None
                
            # Get additional info only when needed (for current price calculations)
            info = None
            if interval == "1m" and period == "1d":  # Current price request
                try:
                    info = ticker.info
                except:
                    info = {}
                
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "hist_data": hist,
                "info": info or {},
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current stock price and basic metrics"""
        data = self._fetch_stock_history(symbol, period="1d", interval="1m")
        if not data or data["hist_data"].empty:
            return None
            
        hist = data["hist_data"]
        info = data["info"]
        
        current_price = hist['Close'].iloc[-1]
        previous_close = info.get('previousClose', current_price)
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(current_price - previous_close, 2),
            "change_percent": round(((current_price - previous_close) / previous_close) * 100, 2),
            "volume": hist['Volume'].iloc[-1] if not hist['Volume'].empty else 0,
            "market_cap": info.get('marketCap', 'N/A'),
            "timestamp": data["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_price_at_time(self, symbol: str, minutes_ago: int) -> Optional[float]:
        """Get stock price from X minutes ago - simplified approach"""
        data = self._fetch_stock_history(symbol, period="1d", interval="1m")
        if not data or data["hist_data"].empty:
            return None
        
        hist = data["hist_data"]
        
        # Check if latest data is recent enough (within 1 minute)
        latest_time = hist.index[-1]
        if hasattr(latest_time, 'tz_localize'):
            latest_time = latest_time.tz_localize(None)
        elif latest_time.tzinfo:
            latest_time = latest_time.replace(tzinfo=None)
        
        time_diff_seconds = (datetime.now() - latest_time).total_seconds()
        
        # If latest data is older than 1 minute, print warning and return None
        if time_diff_seconds > 60:
            print(f"⚠️ Latest data for {symbol} is {time_diff_seconds/60:.1f} minutes old (timestamp: {latest_time})")
            return None
        
        # Use simple indexing: -1 is current, -5 is ~5 minutes ago, etc.
        target_index = -min(minutes_ago, len(hist))
        
        # Make sure we have enough data points
        if abs(target_index) > len(hist):
            print(f"⚠️ Not enough historical data for {symbol} (requested: {minutes_ago} min ago, available: {len(hist)} points)")
            return None
        
        target_price = hist['Close'].iloc[target_index]
        return round(target_price, 2)
    
    def get_historical_data(self, symbol: str, period: str = "5d", interval: str = "1d", max_points: int = 20) -> Optional[Dict]:
        """Get historical price data"""
        data = self._fetch_stock_history(symbol, period=period, interval=interval)
        if not data or data["hist_data"].empty:
            return None
            
        hist = data["hist_data"]
        
        # Format timestamp based on interval
        timestamp_format = "%Y-%m-%d %H:%M:%S" if interval in ["1m", "5m", "15m", "30m", "1h"] else "%Y-%m-%d"
        
        price_data = []
        for timestamp, row in hist.iterrows():
            price_data.append({
                "date": timestamp.strftime(timestamp_format),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2), 
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "high": round(hist['High'].max(), 2),
            "low": round(hist['Low'].min(), 2),
            "avg_volume": int(hist['Volume'].mean()),
            "price_data": price_data[-max_points:]  # Last N points
        }
    
    # Simplified wrapper functions for backward compatibility
    def fetch_current_price(self, symbol: str) -> Optional[Dict]:
        """Legacy wrapper - use get_current_price instead"""
        return self.get_current_price(symbol)
    
    def fetch_price_history(self, symbol: str, period: str = "5d") -> Optional[Dict]:
        """Legacy wrapper - use get_historical_data instead"""
        return self.get_historical_data(symbol, period=period, interval="1d")
        
    def fetch_company_stock_data(self, company_name: str) -> Optional[Dict]:
        """Get comprehensive stock data for a company"""
        symbol = self.get_stock_symbol(company_name)
        if not symbol:
            return None
            
        current_data = self.get_current_price(symbol)
        if not current_data:
            return None
            
        # Try to get intraday data first, fall back to daily if not available
        intraday_history = self.get_historical_data(symbol, period="1d", interval="1m", max_points=50)
        daily_history = self.get_historical_data(symbol, period="5d", interval="1d", max_points=20)
        
        return {
            "company": company_name,
            "symbol": symbol,
            "current": current_data,
            "history": intraday_history if intraday_history else daily_history,
            "daily_history": daily_history  # Keep daily data for longer-term analysis
        }
        
    def fetch_sector_overview(self) -> Dict:
        """Get semiconductor sector performance overview"""
        sector_companies = ["NVDA", "TSM", "INTC", "AMD", "QCOM", "AVGO", "MU"]
        results = {}
        
        for symbol in sector_companies:
            data = self.get_current_price(symbol)
            if data:
                results[symbol] = {
                    "price": data['current_price'],
                    "change_percent": data['change_percent'],
                    "volume": data['volume']
                }
                
        # Calculate sector average
        if results:
            avg_change = sum(stock['change_percent'] for stock in results.values()) / len(results)
            results['sector_average'] = round(avg_change, 2)
            
        return results

# Global instance for easy access
stock_fetcher = StockDataFetcher()