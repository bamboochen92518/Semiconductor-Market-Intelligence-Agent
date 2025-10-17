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
            "NVIDIA": "NVDA",
            "TSMC": "TSM", 
            "Intel": "INTC",
            "AMD": "AMD",
            "Qualcomm": "QCOM",
            "Broadcom": "AVGO",
            "Texas Instruments": "TXN",
            "ASML": "ASML",
            "Micron": "MU",
            "Analog Devices": "ADI",
            "Marvell": "MRVL",
            "KLA Corporation": "KLAC",
            "Applied Materials": "AMAT",
            "Lam Research": "LRCX",
            "MediaTek": "2454.TW",
            "SK Hynix": "000660.KS",
            "Samsung": "005930.KS",
            "Tokyo Electron": "8035.T",
            "SMIC": "0981.HK",
            "UMC": "UMC"
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
        
    def fetch_current_price(self, symbol: str) -> Optional[Dict]:
        """Fetch current stock price and basic info"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty or not info:
                return None
                
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
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
            
    def fetch_price_history(self, symbol: str, period: str = "5d") -> Optional[Dict]:
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
                
            return {
                "symbol": symbol,
                "period": period,
                "high_52w": round(hist['High'].max(), 2),
                "low_52w": round(hist['Low'].min(), 2),
                "avg_volume": int(hist['Volume'].mean()),
                "price_data": [
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(row['Open'], 2),
                        "high": round(row['High'], 2),
                        "low": round(row['Low'], 2),
                        "close": round(row['Close'], 2),
                        "volume": int(row['Volume'])
                    }
                    for date, row in hist.iterrows()
                ][-5:]  # Last 5 days
            }
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None
            
    def fetch_company_stock_data(self, company_name: str) -> Optional[Dict]:
        """Fetch comprehensive stock data for a company"""
        symbol = self.get_stock_symbol(company_name)
        if not symbol:
            return None
            
        current_data = self.fetch_current_price(symbol)
        history_data = self.fetch_price_history(symbol)
        
        if not current_data:
            return None
            
        return {
            "company": company_name,
            "symbol": symbol,
            "current": current_data,
            "history": history_data
        }
        
    def fetch_sector_overview(self) -> Dict:
        """Fetch overview of semiconductor sector performance"""
        sector_companies = ["NVDA", "TSM", "INTC", "AMD", "QCOM", "AVGO", "MU"]
        results = {}
        
        for symbol in sector_companies:
            data = self.fetch_current_price(symbol)
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

def get_stock_analysis_prompt(company_name: str, stock_data: Dict, context: str = "") -> str:
    """Generate prompt for LLM analysis including stock data"""
    if not stock_data:
        return f"No stock data available for {company_name}. {context}"
        
    current = stock_data.get('current', {})
    analysis = stock_data.get('analysis', '')
    
    prompt = f"""
=== REAL-TIME STOCK DATA ===
Company: {company_name} ({stock_data.get('symbol', 'N/A')})
Current Price: ${current.get('current_price', 'N/A')}
Daily Change: ${current.get('change', 'N/A')} ({current.get('change_percent', 'N/A')}%)
Volume: {current.get('volume', 'N/A'):,}
Market Cap: {current.get('market_cap', 'N/A')}
Price Trend: {analysis}
Last Updated: {current.get('timestamp', 'N/A')}

{context}

Provide analysis that:
1. Interprets the current stock price movement
2. Analyzes volume patterns and market sentiment
3. Connects stock performance to recent news/events
4. Assesses if the price reflects company fundamentals
5. Identifies potential trading opportunities or risks
"""
    
    return prompt

# Global instance for easy access
stock_fetcher = StockDataFetcher()