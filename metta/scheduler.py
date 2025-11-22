import asyncio
import schedule
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
from .utils import LLM, process_query
from .investment_rag import InvestmentRAG
from .email_service import email_service
from .stock_monitor import stock_monitor
from .stock_data import stock_fetcher  # Direct import of stock_fetcher

class ScheduledTaskManager:
    """Scheduled task manager responsible for hourly reports and stock monitoring"""
    
    def __init__(self, rag: InvestmentRAG, llm: LLM):
        self.rag = rag
        self.llm = llm
        self.is_running = False
        self.scheduler_thread = None
        self.monitor_task = None
        
        # Configure scheduled tasks
        self._setup_scheduled_tasks()
    
    def _setup_scheduled_tasks(self):
        """Set up scheduled tasks"""
        # Execute market report at the top of every hour
        schedule.every().hour.at(":00").do(self._run_hourly_report)
        
        # Check stock volatility every 15 minutes
        schedule.every(15).minutes.do(self._run_volatility_check)
        
        print("📅 Scheduled tasks configured:")
        print("   📊 Hourly market report: Every hour at :00")
        print("   🚨 Volatility monitoring: Every 15 minutes")
    
    def start(self):
        """Start scheduled tasks"""
        if self.is_running:
            print("⚠️  Task scheduler is already running")
            return
        
        self.is_running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Start asynchronous monitoring task
        asyncio.create_task(self._continuous_monitor())
        
        print("🚀 Scheduled task manager started")
        print(f"⏰ Next hourly report: {self._get_next_hour_time()}")
        print(f"🔍 Volatility checks: Every 15 minutes")
    
    def stop(self):
        """Stop scheduled tasks"""
        self.is_running = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
        
        print("⏸️  Scheduled task manager stopped")
    
    def _run_scheduler(self):
        """Scheduler thread function"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    async def _continuous_monitor(self):
        """Continuous monitoring task"""
        self.monitor_task = asyncio.current_task()
        
        while self.is_running:
            try:
                # Perform a quick stock price check every 5 minutes
                await asyncio.sleep(300)  # 5 minutes
                
                if not self.is_running:
                    break
                
                # Perform a quick volatility check (no email, just record)
                await self._quick_volatility_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in continuous monitor: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying after an error
    
    def _run_hourly_report(self):
        """Execute hourly market report"""
        print(f"\n🕐 Running hourly market report at {datetime.now().strftime('%H:00')}")
        
        try:
            # Execute asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_hourly_report())
            loop.close()
            
        except Exception as e:
            print(f"❌ Error in hourly report: {e}")
    
    def _run_volatility_check(self):
        """Execute stock volatility check"""
        print(f"\n🔍 Running volatility check at {datetime.now().strftime('%H:%M')}")
        
        try:
            # Execute asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(stock_monitor.check_volatility())
            loop.close()
            
        except Exception as e:
            print(f"❌ Error in volatility check: {e}")
    
    async def _generate_hourly_report(self):
        """Generate hourly market report"""
        try:
            print("🔍 Generating hourly semiconductor market analysis...")
            
            # Query market dynamics for the past hour
            query = "What happened in semiconductor market in the past hour?"
            
            # Generate market analysis
            response = process_query(query, self.rag, self.llm)
            
            if isinstance(response, dict):
                market_analysis = response.get('humanized_answer', 'Unable to generate market analysis')
            else:
                market_analysis = str(response)
            
            # Add sector overview
            sector_overview = await stock_monitor.get_sector_overview()
            
            # Build comprehensive report
            full_report = self._build_comprehensive_report(market_analysis, sector_overview)
            
            # Send email report
            success = email_service.send_hourly_report(full_report)
            
            if success:
                print("✅ Hourly report sent successfully")
            else:
                print("❌ Failed to send hourly report")
            
        except Exception as e:
            print(f"❌ Error generating hourly report: {e}")
    
    async def _quick_volatility_check(self):
        """Quick volatility check (compare prices from 15 minutes ago)"""
        try:
            alerts = []
            
            # Check several major stocks
            major_stocks = ["NVIDIA", "TSMC", "Intel", "AMD"]
            
            for company in major_stocks:
                stock_data = stock_fetcher.fetch_company_stock_data(company)
                
                if stock_data and stock_data.get('current'):
                    current_data = stock_data['current']
                    symbol = stock_data['symbol']
                    current_price = current_data['current_price']
                    
                    # Get price from 15 minutes ago directly from yfinance
                    price_15min_ago = stock_fetcher.get_price_at_time(symbol, 15)
                    
                    if price_15min_ago and price_15min_ago > 0:
                        # Calculate price change percentage over 15 minutes
                        price_change_percent = ((current_price - price_15min_ago) / price_15min_ago) * 100
                        
                        print(f"📊 {company} ({symbol}): 15min change {price_change_percent:+.2f}% (${price_15min_ago:.2f} → ${current_price:.2f})")
                        
                        # Check if it exceeds the threshold
                        if abs(price_change_percent) >= stock_monitor.volatility_thresholds["extreme"]:
                            # Get LLM analysis
                            llm_analysis = await stock_monitor._analyze_stock_event_with_llm(
                                company, symbol, price_change_percent, 
                                current_price, price_15min_ago, "15 minutes"
                            )
                            
                            alert_info = {
                                'company': company,
                                'symbol': symbol,
                                'current_price': current_price,
                                'previous_price': price_15min_ago,
                                'change_percent': price_change_percent,
                                'trigger_reason': f'Extreme 15-minute volatility: {price_change_percent:+.2f}%',
                                'severity': 'extreme',
                                'time_period': '15 minutes',
                                'llm_analysis': llm_analysis
                            }
                            alerts.append(alert_info)
                            print(f"🚨 EXTREME volatility alert for {company}: {price_change_percent:+.2f}% in 15 minutes")
                            
                        elif abs(price_change_percent) >= stock_monitor.volatility_thresholds["high"]:
                            # Get LLM analysis
                            llm_analysis = await stock_monitor._analyze_stock_event_with_llm(
                                company, symbol, price_change_percent, 
                                current_price, price_15min_ago, "15 minutes"
                            )
                            
                            alert_info = {
                                'company': company,
                                'symbol': symbol,
                                'current_price': current_price,
                                'previous_price': price_15min_ago,
                                'change_percent': price_change_percent,
                                'trigger_reason': f'High 15-minute volatility: {price_change_percent:+.2f}%',
                                'severity': 'high',
                                'time_period': '15 minutes',
                                'llm_analysis': llm_analysis
                            }
                            alerts.append(alert_info)
                            print(f"🚨 HIGH volatility alert for {company}: {price_change_percent:+.2f}% in 15 minutes")
                    else:
                        # Unable to get 15-minute historical data
                        print(f"📊 {company} ({symbol}): ${current_price:.2f} (unable to get 15-min history)")
            
            # If there are alerts, send them immediately
            if alerts:
                print(f"🚨 Immediate volatility alert triggered for {len(alerts)} stocks")
                # Send alert email
                success = email_service.send_volatility_alert(alerts)
                if success:
                    print("✅ Enhanced volatility alert email sent successfully")
                else:
                    print("❌ Failed to send enhanced volatility alert email")
            
        except Exception as e:
            print(f"❌ Error in quick volatility check: {e}")
    
    def _build_comprehensive_report(self, market_analysis: str, sector_overview: dict) -> str:
        """Build comprehensive market report"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Build sector overview text
        sector_text = f"Sector Average: {sector_overview.get('sector_average_change', 0):+.2f}%\n"
        sector_text += f"Companies Tracked: {sector_overview.get('companies_tracked', 0)}\n\n"
        
        # Add individual stock performance
        sector_text += "Individual Stock Performance:\n"
        sector_text += "-" * 40 + "\n"
        
        for company, data in sector_overview.items():
            if isinstance(data, dict) and 'symbol' in data:
                sector_text += f"{company:15} ({data['symbol']:4}): ${data['price']:8.2f} ({data['change_percent']:+6.2f}%)\n"
        
        # Combine full report
        full_report = f"""
SEMICONDUCTOR MARKET INTELLIGENCE REPORT
Generated at: {current_time}

=== MARKET ANALYSIS ===
{market_analysis}

=== SECTOR OVERVIEW ===
{sector_text}

=== MONITORING STATUS ===
Volatility Thresholds: High ≥5%, Extreme ≥10%
Next Report: {self._get_next_hour_time()}
        """
        
        return full_report.strip()
    
    def _get_next_hour_time(self) -> str:
        """Get next top of the hour time"""
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return next_hour.strftime("%Y-%m-%d %H:00")
    
    def get_status(self) -> dict:
        """Get task manager status"""
        return {
            'is_running': self.is_running,
            'next_hourly_report': self._get_next_hour_time(),
            'scheduler_thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False,
            'monitor_task_running': self.monitor_task and not self.monitor_task.done() if self.monitor_task else False,
            'scheduled_jobs_count': len(schedule.jobs)
        }
    
    def force_hourly_report(self):
        """Manually trigger hourly report"""
        print("🔄 Manually triggering hourly report...")
        self._run_hourly_report()
    
    def force_volatility_check(self):
        """Manually trigger volatility check"""
        print("🔄 Manually triggering volatility check...")
        self._run_volatility_check()

# Since it needs to be initialized in agent.py, no global instance is created here