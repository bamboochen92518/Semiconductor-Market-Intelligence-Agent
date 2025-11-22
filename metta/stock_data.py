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
            hist = ticker.history(period=period, interval=interval)
            
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
        """Get stock price from X minutes ago"""
        # Calculate period needed
        hours_needed = max(1, (minutes_ago + 60) // 60)
        period = f"{hours_needed}d" if hours_needed > 1 else "1d"
        
        data = self._fetch_stock_history(symbol, period=period, interval="1m")
        if not data or data["hist_data"].empty:
            return None
        
        hist = data["hist_data"]
        target_time = datetime.now() - timedelta(minutes=minutes_ago)
        
        # Check if we're looking for a time when market was closed
        latest_data_time = hist.index[-1]
        if hasattr(latest_data_time, 'tz_localize'):
            latest_data_time = latest_data_time.tz_localize(None)
        elif latest_data_time.tzinfo:
            latest_data_time = latest_data_time.replace(tzinfo=None)
        
        time_diff_hours = (datetime.now() - latest_data_time).total_seconds() / 3600
        
        # If market data is too old, return None
        if time_diff_hours > 24:
            return None
        
        closest_price = None
        min_time_diff = float('inf')
        
        for timestamp, row in hist.iterrows():
            # Normalize timestamp for comparison
            hist_time = timestamp
            if hasattr(hist_time, 'tz_localize'):
                hist_time = hist_time.tz_localize(None)
            elif hist_time.tzinfo:
                hist_time = hist_time.replace(tzinfo=None)
            
            time_diff = abs((hist_time - target_time).total_seconds())
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_price = row['Close']
        
        # Return None if time difference is too large (more than 15 minutes)
        if min_time_diff > 900:
            return None
        
        return round(closest_price, 2) if closest_price is not None else None
    
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
            
        return {
            "company": company_name,
            "symbol": symbol,
            "current": current_data,
            "history": self.get_historical_data(symbol)  # Only fetch if needed
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