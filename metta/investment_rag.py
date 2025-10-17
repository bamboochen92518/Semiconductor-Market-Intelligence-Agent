import re
from hyperon import MeTTa, E, S, ValueAtom

class InvestmentRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def get_company_market_cap(self, company):
        """Get market capitalization for a semiconductor company."""
        company = company.strip('"')
        query_str = f'!(match &self (company_market_cap {company} $cap) $cap)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_revenue_growth(self, company):
        """Get revenue growth trend for a semiconductor company."""
        company = company.strip('"')
        query_str = f'!(match &self (revenue_growth {company} $growth) $growth)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_company_region(self, company):
        """Get the primary region/country of a semiconductor company."""
        company = company.strip('"')
        query_str = f'!(match &self (company_region {company} $region) $region)'
        results = self.metta.run(query_str)
        print(results, query_str)
        unique_regions = list(set(str(r[0]) for r in results if r and len(r) > 0)) if results else []
        return unique_regions

    def get_company_segment(self, company):
        """Get business segment information for a semiconductor company."""
        company = company.strip('"')
        query_str = f'!(match &self (company_segment {company} $segment) $segment)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_recommendation(self, company):
        """Get investment recommendation for a semiconductor company."""
        company = company.strip('"')
        query_str = f'!(match &self (recommendation {company} $rec) $rec)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def query_system_level_topic(self, topic):
        """Get information about system-level semiconductor topics (policy, materials, supply chain)."""
        topic = topic.strip('"')
        query_str = f'!(match &self (system_level_topic {topic} $info) $info)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def query_company_level_topic(self, topic):
        """Get information about company-level topics (earnings, innovation, leadership)."""
        topic = topic.strip('"')
        query_str = f'!(match &self (company_level_topic {topic} $info) $info)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_industry_trend(self, trend):
        """Get information about key semiconductor industry trends."""
        trend = trend.strip('"')
        query_str = f'!(match &self (industry_trend {trend} $info) $info)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def get_risk_factor(self, risk):
        """Get information about semiconductor industry risk factors."""
        risk = risk.strip('"')
        query_str = f'!(match &self (risk_factor {risk} $info) $info)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return [r[0].get_object().value for r in results if r and len(r) > 0] if results else []

    def query_companies_by_region(self, region):
        """Get all semiconductor companies in a specific region."""
        region = region.strip('"')
        query_str = f'!(match &self (company_region $company {region}) $company)'
        results = self.metta.run(query_str)
        print(results, query_str)
        unique_companies = list(set(str(r[0]) for r in results if r and len(r) > 0)) if results else []
        return unique_companies

    def query_faq(self, question):
        """Retrieve semiconductor industry FAQ answers."""
        query_str = f'!(match &self (faq "{question}" $answer) $answer)'
        results = self.metta.run(query_str)
        print(results, query_str)
        return results[0][0].get_object().value if results and results[0] else None

    def get_all_companies(self):
        """Get all semiconductor companies in the knowledge base."""
        query_str = '!(match &self (company_market_cap $company $cap) $company)'
        results = self.metta.run(query_str)
        print(results, query_str)
        unique_companies = list(set(str(r[0]) for r in results if r and len(r) > 0)) if results else []
        return unique_companies

    def add_knowledge(self, relation_type, subject, object_value):
        """Add new semiconductor market knowledge dynamically."""
        if isinstance(object_value, str):
            object_value = ValueAtom(object_value)
        self.metta.space().add_atom(E(S(relation_type), S(subject), object_value))
        return f"Added {relation_type}: {subject} → {object_value}"