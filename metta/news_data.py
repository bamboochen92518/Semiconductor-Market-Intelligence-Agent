import json
import feedparser
import requests
import os
import urllib.parse
from datetime import datetime, timedelta
from .prompt import (
    MAX_NEWS_ARTICLES,
    get_news_filtering_prompt,
    get_article_summary_prompt,
    get_comprehensive_analysis_prompt
)


def filter_news_with_llm(all_news, user_query, time_period, llm):
    """Use LLM to intelligently select the most important news articles"""
    if len(all_news) <= MAX_NEWS_ARTICLES:
        print(f"📊 Total articles ({len(all_news)}) is within limit ({MAX_NEWS_ARTICLES}), no filtering needed")
        return all_news
    
    print(f"🧠 Using LLM to filter {len(all_news)} articles down to {MAX_NEWS_ARTICLES} most important ones...")
    
    # Prepare news titles for LLM filtering
    news_titles = ""
    for i, news in enumerate(all_news, 1):
        news_titles += f"{i}. {news['title']}\n"
        news_titles += f"   Source: {news['source']} | Published: {news['published']}\n\n"
    
    prompt = get_news_filtering_prompt(
        user_query=user_query,
        time_period=time_period,
        total_count=len(all_news),
        max_articles=MAX_NEWS_ARTICLES,
        news_titles=news_titles
    )
    
    try:
        response = llm.create_completion(prompt, max_tokens=300)
        print(f"🔍 DEBUG: LLM response for filtering: {response[:200]}...")
        
        # Try to extract JSON from the response
        selected_indices = []
        
        try:
            # First, try to parse the entire response as JSON
            result = json.loads(response)
            selected_indices = result.get("selected_articles", [])
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the response
            import re
            json_match = re.search(r'\{[^}]*"selected_articles"[^}]*\}', response)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    selected_indices = result.get("selected_articles", [])
                except json.JSONDecodeError:
                    pass
            
            # If still no valid JSON, try to extract numbers from the response
            if not selected_indices:
                numbers = re.findall(r'\b(\d+)\b', response)
                selected_indices = [int(num) for num in numbers if 1 <= int(num) <= len(all_news)]
                selected_indices = selected_indices[:MAX_NEWS_ARTICLES]  # Limit to max articles
        
        if not selected_indices:
            print(f"❌ Could not extract valid article indices from LLM response")
            print(f"🔄 Falling back to first {MAX_NEWS_ARTICLES} articles")
            return all_news[:MAX_NEWS_ARTICLES]
        
        # Convert 1-based indices to 0-based and filter
        filtered_news = []
        for idx in selected_indices:
            if 1 <= idx <= len(all_news):
                filtered_news.append(all_news[idx - 1])  # Convert to 0-based
        
        print(f"✅ LLM selected {len(filtered_news)} most important articles")
        return filtered_news[:MAX_NEWS_ARTICLES]  # Ensure we don't exceed limit
        
    except Exception as e:
        print(f"❌ Error in LLM filtering: {e}")
        print(f"🔄 Falling back to first {MAX_NEWS_ARTICLES} articles")
        return all_news[:MAX_NEWS_ARTICLES]


def summarize_individual_article(news_item, llm):
    """Use LLM to summarize a single news article if it's too long"""
    title = news_item.get('title', '')
    description = news_item.get('description', '')
    
    # If description is short or empty, no need to summarize
    if len(description) < 300:
        return description
    
    prompt = get_article_summary_prompt(title=title, description=description)
    
    try:
        summary = llm.create_completion(prompt, max_tokens=150)
        return summary.strip()
    except Exception as e:
        print(f"Error summarizing individual article: {e}")
        # Fallback to truncation only if LLM fails
        return description[:300] + "..." if len(description) > 300 else description


def summarize_news_with_llm(news_list, llm):
    """Use LLM to analyze filtered news articles"""
    if not news_list:
        return "No news to summarize.", []
    
    print(f"📊 Processing {len(news_list)} filtered news articles...")
    
    # First, summarize each individual article if needed
    processed_articles = []
    for i, news in enumerate(news_list, 1):
        print(f"🔄 Processing article {i}/{len(news_list)}: {news['title'][:60]}...")
        
        # Get summarized description
        summarized_description = summarize_individual_article(news, llm)
        
        # Create processed version
        processed_article = news.copy()
        processed_article['processed_description'] = summarized_description
        processed_articles.append(processed_article)
    
    # Prepare all processed news for overall analysis
    news_text = ""
    for i, news in enumerate(processed_articles, 1):
        news_text += f"Article {i}: {news['title']}\n"
        news_text += f"Content: {news['processed_description']}\n"
        news_text += f"Source: {news['source']}\n"
        news_text += f"Published: {news['published']}\n\n"
    
    prompt = get_comprehensive_analysis_prompt(
        article_count=len(processed_articles),
        news_text=news_text
    )
    
    try:
        print(f"🧠 Generating comprehensive analysis of {len(processed_articles)} articles...")
        summary = llm.create_completion(prompt, max_tokens=1200)
        return summary, processed_articles
    except Exception as e:
        print(f"Error generating comprehensive analysis: {e}")
        # Fallback to simple format
        return format_news_simple(processed_articles), processed_articles


def get_news_from_multiple_sources(recommended_search_queries, time_period):
    """Fetch news from multiple sources using multiple LLM-optimized search queries"""
    
    print(f"🔍 DEBUG: Starting news fetch with {len(recommended_search_queries)} search queries")
    print(f"🔍 DEBUG: Search queries: {recommended_search_queries}")
    print(f"🔍 DEBUG: Time period: {time_period}")
    
    all_news = []
    
    # Convert time_period to days for NewsAPI (which only accepts days)
    try:
        if time_period.endswith('h'):
            days_for_newsapi = max(1, int(time_period[:-1]) // 24 + 1)  # Convert hours to days, minimum 1
        elif time_period.endswith('d'):
            days_for_newsapi = int(time_period[:-1])
        else:
            days_for_newsapi = 3  # fallback
    except:
        days_for_newsapi = 3  # fallback
    
    # Process each search query
    for idx, search_query in enumerate(recommended_search_queries, 1):
        print(f"\n📊 Processing query {idx}/{len(recommended_search_queries)}: '{search_query}'")
        
        # Source 1: NewsAPI with current search query
        news_api_key = os.getenv("NEWS_API_KEY")
        if news_api_key:
            try:
                print(f"📡 Fetching from NewsAPI...")
                to_date = datetime.now()
                from_date = to_date - timedelta(days=days_for_newsapi)
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": search_query,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": news_api_key,
                    "pageSize": 10
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    
                    articles_added = 0
                    for article in articles[:5]:  # Top 5 per query from NewsAPI
                        all_news.append({
                            "title": article.get('title', 'N/A'),
                            "published": article.get('publishedAt', 'N/A'),
                            "source": f"NewsAPI ({article.get('source', {}).get('name', 'Unknown')})",
                            "description": article.get('description', ''),
                            "url": article.get('url', ''),
                            "search_query": search_query
                        })
                        articles_added += 1
                    print(f"✅ NewsAPI: Added {articles_added} articles (total available: {len(articles)})")
                else:
                    print(f"❌ NewsAPI request failed with status {response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching from NewsAPI: {e}")
        else:
            print(f"⚠️  NewsAPI key not available, skipping...")
        
        # Source 2: Google News RSS with native time format
        try:
            print(f"📡 Fetching from Google News RSS...")
            encoded_query = urllib.parse.quote_plus(search_query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:{time_period}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
            
            articles_added = 0
            
            for entry in feed.entries:  # Use all available entries
                # Extract description from RSS content if available
                description = ""
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'content') and entry.content:
                    description = entry.content[0].value if entry.content else ""
                
                all_news.append({
                    "title": entry.get('title', 'N/A'),
                    "published": entry.get('published', 'N/A'),
                    "source": "Google News",
                    "description": description,
                    "url": entry.get('link', ''),
                    "search_query": search_query
                })
                articles_added += 1
            
            print(f"✅ Google News: Added {articles_added} articles (total available: {len(feed.entries)})")
        except Exception as e:
            print(f"❌ Error fetching from Google News: {e}")
    
    # Source 3: Yahoo Finance (only once, not per query to avoid duplication)
    try:
        print(f"\n📡 Fetching from Yahoo Finance...")
        yahoo_rss = f"https://feeds.finance.yahoo.com/rss/2.0/headline?region=US&lang=en-US"
        yahoo_feed = feedparser.parse(yahoo_rss)
        
        # Check relevance against any of the search queries
        all_search_terms = []
        for query in recommended_search_queries:
            all_search_terms.extend(query.lower().split())
        
        relevant_entries = []
        for entry in yahoo_feed.entries:
            title = entry.get('title', '').lower()
            if any(term in title for term in all_search_terms if len(term) > 3):  # Skip short words
                relevant_entries.append(entry)
        
        articles_added = 0
        for entry in relevant_entries[:3]:
            all_news.append({
                "title": entry.get('title', 'N/A'),
                "published": entry.get('published', 'N/A'),
                "source": "Yahoo Finance",
                "description": entry.get('summary', ''),
                "url": entry.get('link', ''),
                "search_query": "yahoo_finance_filter"
            })
            articles_added += 1
        
        print(f"✅ Yahoo Finance: Added {articles_added} relevant articles (total scanned: {len(yahoo_feed.entries)})")
    except Exception as e:
        print(f"❌ Error fetching from Yahoo Finance: {e}")
    
    print(f"\n📊 FETCH SUMMARY:")
    print(f"   Total articles fetched: {len(all_news)}")
    
    if not all_news:
        print(f"❌ No articles found for any search query")
        return []
    
    # Remove duplicates and return news list for LLM processing
    print(f"🔄 Removing duplicates...")
    unique_news = remove_duplicates(all_news)
    print(f"   Articles after deduplication: {len(unique_news)}")
    
    # Show source breakdown
    source_counts = {}
    for news in unique_news:
        source = news['source'].split(' (')[0]  # Get main source name
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"📈 Source breakdown:")
    for source, count in source_counts.items():
        print(f"   {source}: {count} articles")
    
    return unique_news


def remove_duplicates(news_list):
    """Remove duplicate articles based on title similarity"""
    unique_news = []
    for news in news_list:
        title_words = set(news['title'].lower().split())
        is_duplicate = False
        
        for existing in unique_news:
            existing_words = set(existing['title'].lower().split())
            # If more than 70% of words overlap, consider it duplicate
            if len(title_words & existing_words) / len(title_words | existing_words) > 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_news.append(news)
    
    return unique_news


def format_news_simple(news_list):
    """Simple fallback formatting if LLM summarization fails"""
    summary = f"Latest semiconductor news - {len(news_list)} articles:\n\n"
    
    for idx, news in enumerate(news_list, 1):
        summary += f"{idx}. {news['title']}\n"
        summary += f"   Published: {news['published']} | Source: {news['source']}\n"
        if news['description']:
            desc = news['description'][:200] + "..." if len(news['description']) > 200 else news['description']
            summary += f"   Summary: {desc}\n"
        summary += "\n"
    
    return summary


def build_source_references(news_list):
    """Build the source references section that users will see"""
    if not news_list:
        return ""
    
    # Sort news by date (most recent first)
    try:
        sorted_news = sorted(news_list, key=lambda x: x.get('published', ''), reverse=True)
    except Exception as e:
        print(f"Error sorting news by date: {e}")
        sorted_news = news_list
    
    source_references = "\n\n **NEWS SOURCES REFERENCED** \n"
    
    for i, news in enumerate(sorted_news, 1):
        source_references += f"{i}. {news['title']}\n"
        source_references += f"   Source: {news['source']} | Published: {news['published']}\n"
        if news['url']:
            source_references += f"   Link: {news['url']}\n"
        source_references += "\n"
    
    return source_references