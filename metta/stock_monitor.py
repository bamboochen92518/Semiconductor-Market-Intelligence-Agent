import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .stock_data import stock_fetcher
from .email_service import email_service

class StockMonitor:
    """Stock price monitoring class for detecting significant fluctuations and triggering alerts"""
    
    def __init__(self):
        # List of major semiconductor companies
        self.watched_companies = [
            "NVIDIA", "TSMC", "Intel", "AMD", "Qualcomm", 
            "Broadcom", "Micron", "ASML", "Texas Instruments"
        ]
        
        # Volatility threshold settings
        self.volatility_thresholds = {
            "high": 5.0,      # 5% change triggers high volatility alert
            "extreme": 10.0,   # 10% change triggers extreme volatility alert
        }
    
    async def check_volatility(self) -> List[Dict]:
        """Simple volatility check: compare current price vs 5 minutes ago"""
        print("🔍 Checking 5-minute price changes...")
        
        alerts = []
        
        for company in self.watched_companies:
            try:
                # Get current price
                stock_data = stock_fetcher.fetch_company_stock_data(company)
                if not stock_data or not stock_data.get('current'):
                    continue
                
                symbol = stock_data['symbol'] 
                current_price = stock_data['current']['current_price']
                
                # Get price from 5 minutes ago
                price_5min_ago = stock_fetcher.get_price_at_time(symbol, 5)
                
                if not price_5min_ago or price_5min_ago <= 0:
                    print(f"📊 {company} ({symbol}): ${current_price:.2f} (no 5min data)")
                    continue
                
                # Calculate percentage change
                change_percent = ((current_price - price_5min_ago) / price_5min_ago) * 100
                
                print(f"📊 {company} ({symbol}): {change_percent:+.2f}% (${price_5min_ago:.2f} → ${current_price:.2f})")
                
                # Check if it exceeds thresholds
                if abs(change_percent) >= self.volatility_thresholds["extreme"]:
                    severity = 'extreme'
                    trigger = f'Extreme 5-minute volatility: {change_percent:+.2f}%'
                elif abs(change_percent) >= self.volatility_thresholds["high"]:
                    severity = 'high' 
                    trigger = f'High 5-minute volatility: {change_percent:+.2f}%'
                else:
                    continue  # No alert needed
                
                # Get LLM analysis
                llm_analysis = await self._analyze_stock_event_with_llm(
                    company, symbol, change_percent, current_price, price_5min_ago, "5 minutes"
                )
                
                alert = {
                    'company': company,
                    'symbol': symbol,
                    'current_price': current_price,
                    'previous_price': price_5min_ago,
                    'change_percent': change_percent,
                    'trigger_reason': trigger,
                    'severity': severity,
                    'time_period': '5 minutes',
                    'llm_analysis': llm_analysis
                }
                alerts.append(alert)
                print(f"🚨 {severity.upper()} alert: {company} {change_percent:+.2f}%")
                
            except Exception as e:
                print(f"❌ Error checking {company}: {e}")
        
        # Send alerts if any
        if alerts:
            print(f"📧 Sending {len(alerts)} volatility alerts...")
            success = email_service.send_volatility_alert(alerts)
            print("✅ Alerts sent" if success else "❌ Failed to send alerts")
        else:
            print("✅ No significant volatility detected")
        
        return alerts
    
    async def _analyze_stock_event_with_llm(self, company: str, symbol: str, 
                                          change_percent: float, current_price: float, 
                                          previous_price: float, time_period: str) -> str:
        """Analyze the cause of abnormal stock price fluctuations using LLM"""
        try:
            # Dynamically import to avoid circular imports
            import os
            from .utils import LLM, process_query
            from .investment_rag import InvestmentRAG
            from .knowledge import initialize_investment_knowledge
            from hyperon import MeTTa
            
            # Initialize LLM
            llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))
            
            # Initialize knowledge graph and RAG
            metta = MeTTa()
            initialize_investment_knowledge(metta)
            rag = InvestmentRAG(metta)
            
            # Construct query
            query = f"""
            {company} ({symbol}) stock price just moved {change_percent:+.2f}% in the last {time_period}, 
            from ${previous_price:.2f} to ${current_price:.2f}. 
            
            What might have caused this significant price movement? 
            Please analyze recent news, market events, or company developments that could explain this volatility.
            Keep the response concise and focused on the most likely causes.
            """
            
            # Use process_query to get analysis
            response = process_query(query, rag, llm)
            
            if isinstance(response, dict):
                analysis = response.get('humanized_answer', 'Unable to analyze the price movement at this time.')
            else:
                analysis = str(response)
            
            # Limit analysis length to avoid overly long emails
            return analysis[:500] + "..." if len(analysis) > 500 else analysis
            
        except Exception as e:
            print(f"❌ Error getting LLM analysis for {company}: {e}")
            return f"Price moved {change_percent:+.2f}% in {time_period}. Unable to analyze the cause at this time."

    async def get_sector_overview(self) -> Dict:
        """Get an overview of the semiconductor sector"""
        print("📊 Getting semiconductor sector overview...")
        
        sector_data = {}
        total_change = 0
        valid_companies = 0
        
        for company in self.watched_companies:
            try:
                stock_data = stock_fetcher.fetch_company_stock_data(company)
                
                if stock_data and stock_data.get('current'):
                    current_data = stock_data['current']
                    sector_data[company] = {
                        'symbol': stock_data['symbol'],
                        'price': current_data['current_price'],
                        'change_percent': current_data.get('change_percent', 0),
                        'volume': current_data.get('volume', 0),
                        'market_cap': current_data.get('market_cap', 'N/A')
                    }
                    
                    total_change += current_data.get('change_percent', 0)
                    valid_companies += 1
                    
            except Exception as e:
                print(f"❌ Error getting data for {company}: {e}")
                continue
        
        # Calculate sector average change
        if valid_companies > 0:
            sector_data['sector_average_change'] = round(total_change / valid_companies, 2)
            sector_data['companies_tracked'] = valid_companies
        else:
            sector_data['sector_average_change'] = 0
            sector_data['companies_tracked'] = 0
        
        return sector_data

# Global instance
stock_monitor = StockMonitor()