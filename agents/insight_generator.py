import anthropic
import os

class InsightGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def generate_explanation(self, result):
        agent_names = {
            'bond': 'Bond007',
            'equity': 'Stonker',
            'derivative': 'CallMeMaybe'
        }
        
        agent = result.get('agent', agent_names.get(result['instrument_type'], 'Agent'))
        verdict = result['verdict']
        confidence = result['confidence']
        
        if result['instrument_type'] == 'bond':
            bond = result['bond']
            stats = result['stats']
            context = f"""Bond: {bond['issuer']}
Yield: {bond['yield_pct']}%
Peer Median: {stats.get('peer_median_yield', 'N/A')}%
Credit Spread: {result.get('credit_spread', 'N/A')}%
Rating: {bond['rating']}"""
        elif result['instrument_type'] == 'equity':
            equity = result['equity']
            context = f"""Stock: {equity['ticker']} ({equity['company']})
Tobin's Q: {result.get('tobins_q', 'N/A'):.2f}
P/E: {equity['pe_ratio']:.1f}
Sector: {equity['sector']}"""
        else:
            deriv = result['derivative']
            context = f"""Option: {deriv['underlying']} {deriv['type']} ${deriv['strike']}
Implied Vol: {deriv['implied_vol']:.2f}
Historical Vol: {deriv['historical_vol']:.2f}"""
        
        prompt = f"""You are {agent}, a witty financial analyst. Provide a 2-3 sentence gamified explanation.

{context}

Verdict: {verdict} ({confidence}% confidence)

Style: Fun, emojis, accurate. Under 60 words."""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"{verdict.replace('_', ' ').title()} with {confidence}% confidence."
