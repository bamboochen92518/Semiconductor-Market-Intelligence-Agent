# Constants
MAX_NEWS_ARTICLES = 15  # Maximum number of articles to process after LLM filtering

# System prompts
SYSTEM_PROMPT = """You are a semiconductor market intelligence analyst with access to real-time, current data. You have been provided with the most up-to-date information including recent news, market data, and industry developments.

CRITICAL INSTRUCTIONS:
- You have access to current information and should NEVER mention data limitations, knowledge cutoffs, or disclaimers about your training data
- You are working with real-time, current market intelligence
- Provide confident analysis based on the information provided to you
- Do not reference any limitations about events or data beyond specific dates
- Focus on delivering professional semiconductor market analysis using the current data you have been given

Analyze the provided information and deliver professional insights without any disclaimers about data availability or limitations."""

def get_intent_classification_prompt(query):
    """Generate the intent classification prompt for a given query"""
    return f"""Given the semiconductor market query: '{query}'
Classify ALL relevant intents (can be multiple) from: 'company_analysis', 'market_cap', 'revenue_growth', 'recommendation', 'region_analysis', 'system_level', 'company_level', 'industry_trend', 'risk_factor', 'recent_news', 'stock_price', 'faq', or 'unknown'.

Use 'recent_news' intent for ANY query asking about:
- Recent events, developments, or happenings (e.g., 'what happened', 'recent performance', 'in the past X days/weeks/months')
- Current state or updates (e.g., 'today', 'this week', 'current situation', 'right now')
- News, announcements, or latest information (e.g., 'news', 'latest', 'new developments')
- Time-specific queries (e.g., 'last 3 days', 'past week', 'this month', 'recently')

Use 'stock_price' intent for ANY query asking about:
- Stock price, share price, trading price (e.g., 'NVIDIA stock price', 'how much is TSMC trading')
- Stock performance, price movement (e.g., 'how is AMD performing', 'Intel stock today')
- Current price, live price, real-time price
- Price analysis, technical analysis, chart analysis

Extract entities:
- company_name: Most relevant company (e.g., NVIDIA, TSMC, Intel)
- time_period: Convert time context to Google News format (e.g., '2 hours' → '2h', 'today' → '1d', 'week' → '7d', 'month' → '30d')
- topic: Other relevant topics (e.g., policy, AI_boom, Taiwan, earnings)
- recommended_search_queries: Generate 2-3 optimized search queries for news APIs as a LIST (e.g., ['NVIDIA AI chips', 'NVIDIA earnings Q3', 'GPU market analysis']). DO NOT include time periods in these queries - focus on company names, topics, and keywords only.

Return *only* the result in JSON format like this, with no additional text:
{{
  "intents": ["<intent1>", "<intent2>"],
  "company_name": "<company_name_or_null>",
  "time_period": "<time_period_or_3d>",
  "topic": "<topic_or_null>",
  "recommended_search_queries": ["<query1>", "<query2>", "<query3>"]
}}"""

def get_news_filtering_prompt(user_query, time_period, total_count, max_articles, news_titles):
    """Generate the news filtering prompt"""
    return f"""You are a semiconductor industry expert tasked with selecting the most important and relevant news articles from a large collection.

User Query: {user_query}
Time Period: {time_period}
Total Articles Found: {total_count}
Need to Select: {max_articles} most important articles

Here are the news article titles and sources:

{news_titles}

Select the {max_articles} most important articles that are:
1. Most relevant to the user's query
2. From reputable sources
3. Covering significant market developments
4. Providing diverse perspectives on key topics
5. Time-sensitive and impactful for semiconductor investors

Prioritize:
- Breaking news and major announcements
- Earnings reports and financial results
- Policy changes and regulatory updates
- Technology breakthroughs and product launches
- Market-moving events and analysis

Return ONLY a JSON list of the selected article numbers (1-based indexing):
{{"selected_articles": [1, 3, 7, 12, ...]}}"""

def get_article_summary_prompt(title, description):
    """Generate the individual article summarization prompt"""
    return f"""Summarize this semiconductor news article concisely:

Title: {title}
Content: {description}

Provide a 2-3 sentence summary focusing on:
1. Key facts and developments
2. Market/business impact
3. Important details for semiconductor investors

Keep it professional and factual."""

def get_comprehensive_analysis_prompt(article_count, news_text):
    """Generate the comprehensive news analysis prompt"""
    return f"""Analyze these {article_count} semiconductor news articles comprehensively:

{news_text}

Provide professional analysis covering:
1. Key developments and emerging trends across all articles
2. Most significant stories with explanations (reference by article number)
3. Market implications and investment impact
4. Sector-wide patterns and connections between stories
5. Actionable insights for semiconductor investors

Reference specific articles by number when discussing developments. Be thorough since all articles contain valuable information."""