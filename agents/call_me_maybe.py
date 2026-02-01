import pandas as pd
from statistics import median, stdev

class CallMeMaybe:
    def __init__(self):
        self.derivatives_df = pd.read_csv('data/derivatives.csv')
    
    def get_peers(self, derivative):
        peers = self.derivatives_df[
            (self.derivatives_df['underlying'] == derivative['underlying']) &
            (self.derivatives_df['type'] == derivative['type']) &
            (abs(self.derivatives_df['strike'] - derivative['strike']) <= derivative['strike'] * 0.1)
        ]
        peers = peers[
            (peers['strike'] != derivative['strike']) |
            (peers['expiry_days'] != derivative['expiry_days'])
        ]
        return peers
    
    def analyze(self, identifier):
        parts = identifier.split('_')
        if len(parts) != 3:
            raise ValueError("Format: UNDERLYING_type_strike")
        
        underlying, opt_type, strike = parts[0], parts[1], float(parts[2])
        
        derivative_row = self.derivatives_df[
            (self.derivatives_df['underlying'] == underlying) &
            (self.derivatives_df['type'] == opt_type) &
            (self.derivatives_df['strike'] == strike)
        ]
        
        if derivative_row.empty:
            raise ValueError("Derivative not found")
        
        derivative = derivative_row.iloc[0].to_dict()
        peers = self.get_peers(derivative)
        
        iv = derivative['implied_vol']
        hist_vol = derivative['historical_vol']
        iv_premium = ((iv - hist_vol) / hist_vol) * 100
        
        if iv_premium > 50:
            verdict = 'OVERVALUED'
            confidence = 80
        elif iv_premium < -10:
            verdict = 'UNDERVALUED'
            confidence = 75
        else:
            verdict = 'FAIRLY_VALUED'
            confidence = 65
        
        if iv_premium > 100:
            verdict = 'MASSIVELY_OVERPRICED'
            confidence = 95
        
        return {
            'agent': 'CallMeMaybe',
            'instrument_type': 'derivative',
            'derivative': derivative,
            'peers': peers,
            'verdict': verdict,
            'confidence': confidence
        }