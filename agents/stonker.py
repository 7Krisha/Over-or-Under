import pandas as pd
from statistics import median, stdev
import json

class Stonker:
    def __init__(self):
        self.equities_df = pd.read_csv('data/equities.csv')
        with open('data/industry_benchmarks.json') as f:
            self.benchmarks = json.load(f)
    
    def get_peers(self, equity):
        peers = self.equities_df[
            (self.equities_df['sector'] == equity['sector']) &
            (self.equities_df['ticker'] != equity['ticker'])
        ]
        return peers
    
    def calculate_tobins_q(self, equity):
        market_cap = equity['market_cap_b'] * 1e9
        book_value = (equity['total_assets_b'] - equity['total_liabilities_b']) * 1e9
        if book_value <= 0:
            return None
        return market_cap / book_value
    
    def analyze(self, ticker):
        equity_row = self.equities_df[self.equities_df['ticker'] == ticker]
        if equity_row.empty:
            raise ValueError(f"Ticker not found")
        
        equity = equity_row.iloc[0].to_dict()
        peers = self.get_peers(equity)
        tobins_q = self.calculate_tobins_q(equity)
        
        pe = equity['pe_ratio']
        if pe > 50:
            verdict = 'OVERVALUED'
            confidence = 85
        elif pe < 10:
            verdict = 'UNDERVALUED'
            confidence = 75
        else:
            verdict = 'FAIRLY_VALUED'
            confidence = 70
        
        return {
            'agent': 'Stonker',
            'instrument_type': 'equity',
            'equity': equity,
            'peers': peers,
            'tobins_q': tobins_q,
            'verdict': verdict,
            'confidence': confidence
        }