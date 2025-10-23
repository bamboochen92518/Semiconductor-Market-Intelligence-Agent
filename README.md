# Semiconductor Market Intelligence Agent

> **AI-Powered 24/7 Market Analysis** | Integrating SingularityNET MeTTa Knowledge Graph & Fetch.ai uAgents

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

An autonomous AI agent that provides real-time semiconductor market analysis, combining intelligent news aggregation, live stock data, and structured knowledge reasoning to deliver institutional-grade investment insights.

## 🤖 Agent Details

- **Agent Name**: Semiconductor Market Intelligence Agent
- **Agent Address**: `agent1qddlqsx7ch8c5g6h600w0cexmw46777nrc74p7qu6mmt9zpfevjeyxhny58`
- **Category**: Innovation Lab
- **Hackathon**: ETH Global Online 2025

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11+
- ASI:One API key ([Get it here](https://asi1.ai/))
- NewsAPI key ([Get it here](https://newsapi.org/))

### **Installation**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
echo "ASI_ONE_API_KEY=your_asi_one_api_key" > .env
echo "NEWS_API_KEY=your_news_api_key" >> .env

# 5. Run the agent
python agent.py
```

### **Expected Output**

```
INFO:     [Semiconductor Market Intelligence Agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=...
INFO:     [Semiconductor Market Intelligence Agent]: Starting server on http://0.0.0.0:8008
```

### **Connect to Agent**

1. **Via Agentverse Inspector**:
   - Copy the inspector URL from console
   - Click `Connect` → Select `Mailbox`
   - Follow [mailbox setup guide](https://innovationlab.fetch.ai/resources/docs/agent-creation/uagent-creation#mailbox-agents)

2. **Via Agentverse Chat**:
   - Go to `Agent Profile` → `Chat with Agent`
   - Start interacting through the web interface

### **Sample Queries**

#### 🎯 Multi-Intent Analysis
```
"Analyze TSMC stock price based on latest news"
"Should I invest in NVIDIA given recent developments?"
"What's happening with AMD and should I buy?"
"How do recent chip policy changes affect TSMC stock?"
```

#### 📈 Stock Price Tracking
```
"NVIDIA stock price"
"What's TSMC trading at?"
"Show me Broadcom price"
```

#### 📰 Real-Time News Intelligence
```
"What's the latest news about NVIDIA?"
"Tell me recent semiconductor news"
"What happened to TSMC this week?"
"Show me Intel developments from last month"
```

#### 🏢 Company Analysis
```
"Tell me about NVIDIA's market position"
"Analyze TSMC as an investment"
"Evaluate AMD's competitive position"
```

## ✨ Key Features

### 📰 **Multi-Source News Aggregation**
Intelligent news collection and filtering:

1. **Fetch** from NewsAPI, Google News RSS, Yahoo Finance
2. **Filter** with LLM to select top 15 most important articles
3. **Analyze** with cross-article synthesis and trend identification
4. **Deduplicate** to eliminate redundant coverage

**Result**: Curated intelligence instead of information overload.

### 📊 **Real-Time Market Data**
Live financial metrics via yfinance:
- Current stock price & daily change
- Trading volume & market capitalization
- Historical performance tracking

### 🔗 **MeTTa Knowledge Graph**
Structured semiconductor industry intelligence with hypergraph reasoning:
- **Symbolic Reasoning**: Pattern matching and logical inference
- **Hypergraph Structure**: Complex multi-way relationships
- **Dynamic Knowledge**: Runtime knowledge addition
- **Type Safety**: Strongly-typed atoms and expressions

**Knowledge Domains**:
- Company fundamentals (market cap, revenue growth, segments)
- Industry trends (AI boom, advanced nodes, geopolitics)
- Risk factors (cyclicality, capex, competition)
- Investment recommendations (buy/hold/sell with rationale)

## 🏗️ Architecture

### **System Overview**

![System Overview](system_overview.png)

### **Data Flow**

```
User Query: "Analyze NVIDIA stock based on latest news"
    │
    ├─► Intent Classification
    │   └─► ["recent_news", "stock_price", "company_analysis"]
    │
    ├─► Entity Extraction
    │   ├─► Company: NVIDIA
    │   ├─► Time Period: 3 days
    │   └─► Search Queries: ["NVIDIA AI chips", "NVIDIA earnings"]
    │
    ├─► Parallel Data Collection
    │   ├─► News (50+ articles) → LLM Filter → Top 15
    │   ├─► Stock Data → Real-time price, volume, market cap
    │   └─► Knowledge Graph → Fundamentals & recommendations
    │
    ├─► LLM Synthesis
    │   └─► Comprehensive professional analysis
    │
    └─► Response with Sources & URLs
```

## 📁 Project Structure

```
project/
├── agent.py                      # Main uAgent with Chat Protocol
├── metta/
│   ├── knowledge.py             # MeTTa knowledge graph (semiconductor data)
│   ├── investment_rag.py        # RAG system for knowledge retrieval
│   ├── utils.py                 # LLM integration & query processing
│   ├── news_data.py             # Multi-source news aggregation
│   └── stock_data.py            # Real-time stock data (yfinance)
├── requirements.txt             # Python dependencies
├── .env                         # API keys (not in repo)
├── README.md                    # This file
└── report-after-discussion-gpt.md  # Design documentation
```

## 🔗 Resources

| Resource | Link |
|----------|------|
| **MeTTa Documentation** | [metta-lang.dev](https://metta-lang.dev/docs/learn/tutorials/python_use/metta_python_basics.html) |
| **Fetch.ai uAgents** | [fetch.ai/docs](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents) |
| **Agentverse Platform** | [agentverse.ai](https://agentverse.ai/) |
| **ASI:One LLM** | [asi1.ai](https://asi1.ai/) |
| **NewsAPI** | [newsapi.org](https://newsapi.org/) |
| **Design Report** | [report-after-discussion-gpt.md](./report-after-discussion-gpt.md) |

## 🤝 Contributing

This project serves as a **template for domain-specific AI agents**. Extend it by:

- 📊 Adding more semiconductor companies to knowledge graph
- 📰 Integrating additional news sources (Bloomberg, Reuters)
- 💹 Adding technical indicators and sentiment analysis
- 🎨 Building visualization dashboard (Streamlit, Dash)
- 🧪 Implementing backtesting for investment strategies

## 🎓 Key Innovation

This project demonstrates **next-generation agentic AI** through:

1. **Multi-Source Intelligence Fusion**: NewsAPI + Google News + Yahoo Finance + yfinance
2. **Hypergraph Knowledge Reasoning**: MeTTa's symbolic AI capabilities
3. **Production-Ready Architecture**: Robust error handling, logging, and fallbacks
4. **Time-Flexible Natural Language**: LLM understands "2 hours ago", "last week", "past month"

**Result**: A Wall Street-grade analyst that works 24/7, never misses information, and delivers institutional-quality insights in seconds.

## 📄 License

MIT License - Part of ETH Global Online Hackathon 2025

## 🙏 Acknowledgments

- **SingularityNET** - MeTTa knowledge graph framework
- **Fetch.ai** - uAgents and Agentverse platform  
- **ASI Alliance** - ASI:One LLM capabilities
- **NewsAPI, Google News, Yahoo Finance** - News data providers

<div align="center">

**Built with 🧠 for ETH Global Online Hackathon**  
*October 2025*

[🚀 Try Demo](https://agentverse.ai/agents/details/agent1qddlqsx7ch8c5g6h600w0cexmw46777nrc74p7qu6mmt9zpfevjeyxhny58/profile)

</div>