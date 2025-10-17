import json
import shutil
from openai import OpenAI
from .investment_rag import InvestmentRAG
from .stock_data import stock_fetcher
from .news_data import (
    filter_news_with_llm,
    summarize_news_with_llm,
    get_news_from_multiple_sources,
    build_source_references,
    summarize_individual_article
)
from .prompt import (
    SYSTEM_PROMPT, 
    get_intent_classification_prompt
)

class LLM:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.asi1.ai/v1"
        )

    def create_completion(self, prompt, max_tokens=2500):
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="asi1-mini",
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content

def get_intent_and_keyword(query, llm):
    """Use ASI:One API to classify semiconductor market query intent and extract entities."""
    prompt = get_intent_classification_prompt(query)
    
    try:
        response = llm.create_completion(prompt, max_tokens=200)
        
        # Clean the response - sometimes LLM includes extra text
        response_cleaned = response.strip()
        
        # Try to extract JSON if it's wrapped in other text
        if '{' in response_cleaned and '}' in response_cleaned:
            start_idx = response_cleaned.find('{')
            end_idx = response_cleaned.rfind('}') + 1
            json_str = response_cleaned[start_idx:end_idx]
        else:
            json_str = response_cleaned
        
        result = json.loads(json_str)
        
        intents = result.get("intents", ["unknown"])
        company_name = result.get("company_name", None)
        time_period = result.get("time_period", "3d")
        topic = result.get("topic", None)
        recommended_search_queries = result.get("recommended_search_queries", ["semiconductor"])
        
        print(f"✅ Successfully extracted: intents={intents}, company={company_name}, time={time_period}, topic={topic}")
        return intents, company_name, time_period, topic, recommended_search_queries
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"❌ Raw response that failed to parse: {response}")
        return ["unknown"], None, "3d", None, ["semiconductor"]
    except Exception as e:
        print(f"❌ General error in get_intent_and_keyword: {e}")
        print(f"❌ Response: {response}")
        return ["unknown"], None, "3d", None, ["semiconductor"]

def process_query(query, rag: InvestmentRAG, llm: LLM):
    intents, company_name, time_period, topic, recommended_search_queries = get_intent_and_keyword(query, llm)
    print(f"Intents: {intents}, Company: {company_name}, Time: {time_period}, Topic: {topic}")
    print(f"LLM-generated search queries: {recommended_search_queries}")
    
    # Build prompt sections additively
    prompt_sections = [f"Query: '{query}'\n"]
    news_references = ""  # Store news references for final output
    
    # Handle each intent independently
    if "recent_news" in intents:
        print(f"Fetching news using LLM search queries (past {time_period})")
        
        # Step 1: Fetch ALL available news
        all_news = get_news_from_multiple_sources(recommended_search_queries, time_period)
        
        if all_news:
            # Step 2: Use LLM to filter to most important articles
            filtered_news = filter_news_with_llm(all_news, query, time_period, llm)
            
            # Step 3: Use LLM to analyze the filtered articles
            news_summary, summarized_news_list = summarize_news_with_llm(filtered_news, llm)
            
            # Step 4: Build source references for final output
            print(f"🔗 DEBUG: Building source references from {len(summarized_news_list)} processed articles...")
            news_references = build_source_references(summarized_news_list)
            print(f"🔗 DEBUG: Source references length: {len(news_references)} characters")
            print(f"🔗 DEBUG: Source references preview: {news_references[:200]}...")
        else:
            news_summary = "No recent news found."
            print("⚠️  DEBUG: No news found, skipping source references")
        
        terminal_width = shutil.get_terminal_size().columns
        separator = "=" * min(terminal_width, 80)
        prompt_sections.append(f"\n{separator[:20]} LATEST NEWS {separator[:20]}\n{news_summary}\n")

    if "stock_price" in intents and company_name:
        print(f"Fetching stock data for: {company_name}")
        stock_data = stock_fetcher.fetch_company_stock_data(company_name)
        
        if stock_data:
            current = stock_data.get('current', {})
            
            prompt_sections.append(
                f"=== REAL-TIME STOCK DATA ===\n"
                f"Company: {company_name} ({stock_data.get('symbol', 'N/A')})\n"
                f"Current Price: ${current.get('current_price', 'N/A')}\n"
                f"Daily Change: ${current.get('change', 'N/A')} ({current.get('change_percent', 'N/A')}%)\n"
                f"Volume: {current.get('volume', 'N/A'):,}\n"
                f"Market Cap: {current.get('market_cap', 'N/A')}\n"
                f"Last Updated: {current.get('timestamp', 'N/A')}\n\n"
            )
    
    if "company_analysis" in intents and company_name:
        print(f"Fetching company data for: {company_name}")
        market_cap = rag.get_company_market_cap(company_name)
        revenue_growth = rag.get_revenue_growth(company_name)
        region = rag.get_company_region(company_name)
        segment = rag.get_company_segment(company_name)
        recommendation = rag.get_recommendation(company_name)
        
        prompt_sections.append(
            f"=== COMPANY FUNDAMENTALS ===\n"
            f"Company: {company_name}\n"
            f"Market Cap: {market_cap[0] if market_cap else 'N/A'}\n"
            f"Revenue Growth: {revenue_growth[0] if revenue_growth else 'N/A'}\n"
            f"Region: {region[0] if region else 'N/A'}\n"
            f"Segment: {segment[0] if segment else 'N/A'}\n"
            f"Recommendation: {recommendation[0] if recommendation else 'N/A'}\n\n"
        )
        
        # Add macro context for company analysis
        geopolitics_info = rag.query_system_level_topic("geopolitics")
        policy_info = rag.query_system_level_topic("policy")
        
        prompt_sections.append(
            f"=== MACRO FACTORS ===\n"
            f"Geopolitics: {', '.join(geopolitics_info) if geopolitics_info else 'US-China tensions, export controls'}\n"
            f"Policy: {', '.join(policy_info) if policy_info else 'CHIPS Act, subsidies'}\n\n"
        )
    
    if "recommendation" in intents and company_name:
        recommendation = rag.get_recommendation(company_name)
        market_cap = rag.get_company_market_cap(company_name)
        
        prompt_sections.append(
            f"=== INVESTMENT RECOMMENDATION ===\n"
            f"Company: {company_name}\n"
            f"Current Recommendation: {', '.join(recommendation) if recommendation else 'N/A'}\n"
            f"Market Cap: {', '.join(market_cap) if market_cap else 'N/A'}\n\n"
        )
    
    if "market_cap" in intents and company_name:
        market_cap = rag.get_company_market_cap(company_name)
        prompt_sections.append(
            f"=== MARKET CAPITALIZATION ===\n"
            f"Company: {company_name}\n"
            f"Market Cap: {', '.join(market_cap) if market_cap else 'N/A'}\n\n"
        )
    
    if "revenue_growth" in intents and company_name:
        revenue_growth = rag.get_revenue_growth(company_name)
        prompt_sections.append(
            f"=== REVENUE GROWTH ===\n"
            f"Company: {company_name}\n"
            f"Growth: {', '.join(revenue_growth) if revenue_growth else 'N/A'}\n\n"
        )
    
    if "region_analysis" in intents and (company_name or topic):
        region_key = company_name or topic
        companies = rag.query_companies_by_region(region_key)
        prompt_sections.append(
            f"=== REGIONAL ANALYSIS ===\n"
            f"Region: {region_key}\n"
            f"Companies: {', '.join(companies) if companies else 'N/A'}\n\n"
        )
    
    if "system_level" in intents and topic:
        system_info = rag.query_system_level_topic(topic)
        prompt_sections.append(
            f"=== SYSTEM-LEVEL FACTORS ===\n"
            f"Topic: {topic}\n"
            f"Info: {', '.join(system_info) if system_info else 'N/A'}\n\n"
        )
    
    if "company_level" in intents and topic:
        company_info = rag.query_company_level_topic(topic)
        prompt_sections.append(
            f"=== COMPANY-LEVEL FACTORS ===\n"
            f"Topic: {topic}\n"
            f"Info: {', '.join(company_info) if company_info else 'N/A'}\n\n"
        )
    
    if "industry_trend" in intents and topic:
        trend_info = rag.get_industry_trend(topic)
        prompt_sections.append(
            f"=== INDUSTRY TREND ===\n"
            f"Trend: {topic}\n"
            f"Info: {', '.join(trend_info) if trend_info else 'N/A'}\n\n"
        )
    
    if "risk_factor" in intents and topic:
        risk_info = rag.get_risk_factor(topic)
        prompt_sections.append(
            f"=== RISK FACTORS ===\n"
            f"Risk: {topic}\n"
            f"Info: {', '.join(risk_info) if risk_info else 'N/A'}\n\n"
        )
    
    if "faq" in intents:
        faq_answer = rag.query_faq(query)
        if faq_answer:
            prompt_sections.append(
                f"=== FAQ ANSWER ===\n"
                f"Q: {query}\n"
                f"A: {faq_answer}\n\n"
            )
    
    # Build final prompt
    prompt = "".join(prompt_sections)
    prompt += "Provide professional semiconductor market analysis. Be comprehensive and actionable."
    
    print(f"\n🔍 DEBUG: Sending prompt to LLM...")
    print(f"Prompt length: {len(prompt)} characters")
    
    response = llm.create_completion(prompt, max_tokens=4096)
    
    print(f"\n📝 DEBUG: Raw LLM Response:")
    print(f"Response length: {len(response)} characters")
    
    if not response or len(response.strip()) == 0:
        print("⚠️  WARNING: Empty response from LLM!")
        return {"selected_question": query, "humanized_answer": "I apologize, but I received an empty response. Please try again."}
    
    # Add news references to the final response that users will see
    final_response = response.strip()
    
    # Debug the final response assembly
    print(f"🔗 DEBUG: Final response assembly...")
    print(f"🔗 DEBUG: Base response length: {len(final_response)} characters")
    print(f"🔗 DEBUG: News references length: {len(news_references)} characters")
    print(f"🔗 DEBUG: News references exists: {bool(news_references)}")
    
    if news_references:
        final_response += news_references
        print(f"✅ DEBUG: Added news references to final response")
        print(f"✅ DEBUG: Final response with references length: {len(final_response)} characters")
    else:
        print("⚠️  DEBUG: No news references to add")
    
    print(f"\n✅ Response generated successfully")
    return {"selected_question": query, "humanized_answer": final_response}
