from hyperon import MeTTa, E, S, ValueAtom

def initialize_investment_knowledge(metta: MeTTa):
    """Initialize the MeTTa knowledge graph with semiconductor market intelligence data."""
    
    # Semiconductor Companies → Market Cap (in billions USD)
    metta.space().add_atom(E(S("company_market_cap"), S("TSMC"), ValueAtom("$500B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("NVIDIA"), ValueAtom("$1T+")))
    metta.space().add_atom(E(S("company_market_cap"), S("Samsung"), ValueAtom("$300B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("Intel"), ValueAtom("$150B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("ASML"), ValueAtom("$250B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("AMD"), ValueAtom("$200B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("Qualcomm"), ValueAtom("$150B+")))
    metta.space().add_atom(E(S("company_market_cap"), S("Broadcom"), ValueAtom("$600B+")))
    
    # Semiconductor Companies → Revenue Growth (recent trend)
    metta.space().add_atom(E(S("revenue_growth"), S("TSMC"), ValueAtom("15-20% YoY")))
    metta.space().add_atom(E(S("revenue_growth"), S("NVIDIA"), ValueAtom("50-100% YoY (AI boom)")))
    metta.space().add_atom(E(S("revenue_growth"), S("Samsung"), ValueAtom("8-12% YoY")))
    metta.space().add_atom(E(S("revenue_growth"), S("Intel"), ValueAtom("flat to negative")))
    metta.space().add_atom(E(S("revenue_growth"), S("ASML"), ValueAtom("25-30% YoY")))
    metta.space().add_atom(E(S("revenue_growth"), S("AMD"), ValueAtom("20-30% YoY")))
    metta.space().add_atom(E(S("revenue_growth"), S("Qualcomm"), ValueAtom("10-15% YoY")))
    metta.space().add_atom(E(S("revenue_growth"), S("Broadcom"), ValueAtom("15-20% YoY")))
    
    # Semiconductor Companies → Primary Region
    metta.space().add_atom(E(S("company_region"), S("TSMC"), S("Taiwan")))
    metta.space().add_atom(E(S("company_region"), S("NVIDIA"), S("USA")))
    metta.space().add_atom(E(S("company_region"), S("Samsung"), S("South_Korea")))
    metta.space().add_atom(E(S("company_region"), S("Intel"), S("USA")))
    metta.space().add_atom(E(S("company_region"), S("ASML"), S("Netherlands")))
    metta.space().add_atom(E(S("company_region"), S("AMD"), S("USA")))
    metta.space().add_atom(E(S("company_region"), S("Qualcomm"), S("USA")))
    metta.space().add_atom(E(S("company_region"), S("Broadcom"), S("USA")))
    
    # News Classification → System-Level Topics
    metta.space().add_atom(E(S("system_level_topic"), S("policy"), ValueAtom("government regulations, export controls, subsidies")))
    metta.space().add_atom(E(S("system_level_topic"), S("materials"), ValueAtom("silicon supply, rare earth elements, substrates")))
    metta.space().add_atom(E(S("system_level_topic"), S("supply_chain"), ValueAtom("global logistics, manufacturing capacity, shortages")))
    metta.space().add_atom(E(S("system_level_topic"), S("geopolitics"), ValueAtom("US-China tensions, trade wars, sanctions")))
    metta.space().add_atom(E(S("system_level_topic"), S("technology"), ValueAtom("node advancements, EUV lithography, chip architecture")))
    
    # News Classification → Company-Level Topics
    metta.space().add_atom(E(S("company_level_topic"), S("earnings"), ValueAtom("quarterly results, revenue, profit margins")))
    metta.space().add_atom(E(S("company_level_topic"), S("innovation"), ValueAtom("new products, patents, R&D breakthroughs")))
    metta.space().add_atom(E(S("company_level_topic"), S("leadership"), ValueAtom("CEO changes, strategic shifts, M&A")))
    metta.space().add_atom(E(S("company_level_topic"), S("partnerships"), ValueAtom("collaborations, contracts, customer wins")))
    
    # Company → Business Segment
    metta.space().add_atom(E(S("company_segment"), S("TSMC"), ValueAtom("foundry services, advanced nodes")))
    metta.space().add_atom(E(S("company_segment"), S("NVIDIA"), ValueAtom("AI chips, GPUs, data center")))
    metta.space().add_atom(E(S("company_segment"), S("Samsung"), ValueAtom("memory, foundry, consumer electronics")))
    metta.space().add_atom(E(S("company_segment"), S("Intel"), ValueAtom("CPUs, foundry services, data center")))
    metta.space().add_atom(E(S("company_segment"), S("ASML"), ValueAtom("lithography equipment, EUV systems")))
    metta.space().add_atom(E(S("company_segment"), S("AMD"), ValueAtom("CPUs, GPUs, data center")))
    metta.space().add_atom(E(S("company_segment"), S("Qualcomm"), ValueAtom("mobile chips, 5G, IoT")))
    metta.space().add_atom(E(S("company_segment"), S("Broadcom"), ValueAtom("networking, broadband, wireless")))
    
    # Investment Recommendations
    metta.space().add_atom(E(S("recommendation"), S("TSMC"), ValueAtom("BUY - leading foundry position, AI demand")))
    metta.space().add_atom(E(S("recommendation"), S("NVIDIA"), ValueAtom("BUY - AI market leader, strong growth")))
    metta.space().add_atom(E(S("recommendation"), S("Samsung"), ValueAtom("HOLD - diversified but facing competition")))
    metta.space().add_atom(E(S("recommendation"), S("Intel"), ValueAtom("HOLD - turnaround in progress, uncertain timeline")))
    metta.space().add_atom(E(S("recommendation"), S("ASML"), ValueAtom("BUY - monopoly in EUV technology")))
    metta.space().add_atom(E(S("recommendation"), S("AMD"), ValueAtom("BUY - gaining market share from Intel")))
    metta.space().add_atom(E(S("recommendation"), S("Qualcomm"), ValueAtom("HOLD - stable mobile business, 5G growth")))
    metta.space().add_atom(E(S("recommendation"), S("Broadcom"), ValueAtom("BUY - strong networking position")))
    
    # Key Industry Trends
    metta.space().add_atom(E(S("industry_trend"), S("AI_boom"), ValueAtom("massive demand for AI chips driving NVIDIA, AMD growth")))
    metta.space().add_atom(E(S("industry_trend"), S("advanced_nodes"), ValueAtom("race to 3nm and 2nm manufacturing processes")))
    metta.space().add_atom(E(S("industry_trend"), S("geopolitical_risk"), ValueAtom("US-China tensions affecting supply chains")))
    metta.space().add_atom(E(S("industry_trend"), S("reshoring"), ValueAtom("government subsidies for domestic chip manufacturing")))
    metta.space().add_atom(E(S("industry_trend"), S("consolidation"), ValueAtom("M&A activity increasing in semiconductor sector")))
    
    # Risk Factors
    metta.space().add_atom(E(S("risk_factor"), S("cyclicality"), ValueAtom("semiconductor industry highly cyclical")))
    metta.space().add_atom(E(S("risk_factor"), S("capex"), ValueAtom("high capital expenditure requirements")))
    metta.space().add_atom(E(S("risk_factor"), S("geopolitical"), ValueAtom("export controls, sanctions, trade restrictions")))
    metta.space().add_atom(E(S("risk_factor"), S("competition"), ValueAtom("intense competition and rapid technological change")))
    
    # FAQs about Semiconductor Industry
    metta.space().add_atom(E(S("faq"), S("What is driving semiconductor demand?"), ValueAtom("AI, data centers, 5G, IoT, automotive electrification")))
    metta.space().add_atom(E(S("faq"), S("Which companies lead in AI chips?"), ValueAtom("NVIDIA dominates, AMD gaining ground, Intel lagging")))
    metta.space().add_atom(E(S("faq"), S("What is EUV lithography?"), ValueAtom("Extreme ultraviolet lithography for advanced chip manufacturing, ASML monopoly")))
    metta.space().add_atom(E(S("faq"), S("How do geopolitics affect semiconductors?"), ValueAtom("Export controls, supply chain disruptions, reshoring initiatives")))