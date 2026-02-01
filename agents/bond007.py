import pandas as pd
from statistics import median, stdev
from typing import Dict, Tuple
import json

class Bond007:
    def __init__(self):
        self.bonds_df = pd.read_csv('data/bonds.csv')
        with open('data/industry_benchmarks.json') as f:
            self.benchmarks = json.load(f)
    
    def get_peers(self, bond):
        peers = self.bonds_df[
            (self.bonds_df['sector'] == bond['sector']) &
            (self.bonds_df['issuer'] != bond['issuer']) &
            (abs(self.bonds_df['maturity_years'] - bond['maturity_years']) <= 2)
        ]
        return peers
    
    def calculate_credit_spread(self, bond):
        treasury_yield = self.benchmarks.get('Government', {}).get('bond_yield_avg', 4.35)
        return bond['yield_pct'] - treasury_yield
    
    def analyze_yield_spread(self, bond, peers):
        if len(peers) < 2:
            return {'error': 'Insufficient peer bonds'}
        
        peer_yields = peers['yield_pct'].tolist()
        peer_median = median(peer_yields)
        peer_std = stdev(peer_yields) if len(peer_yields) > 1 else 0.5
        
        deviation = bond['yield_pct'] - peer_median
        z_score = deviation / peer_std if peer_std > 0 else 0
        
        return {
            'bond_yield': bond['yield_pct'],
            'peer_median_yield': peer_median,
            'deviation': deviation,
            'z_score': z_score,
            'peer_count': len(peers)
        }
    
    def generate_verdict(self, bond, yield_analysis, credit_spread):
        if 'error' in yield_analysis:
            return 'INSUFFICIENT_DATA', 0, yield_analysis
        
        signals = []
        z_score = yield_analysis['z_score']
        
        if z_score > 1.5:
            signals.append(('UNDERVALUED', 40))
        elif z_score < -1.5:
            signals.append(('OVERVALUED', 40))
        else:
            signals.append(('NEUTRAL', 20))
        
        sector_avg_spread = self.benchmarks.get(bond['sector'], {}).get('credit_spread_avg', 2.0)
        spread_ratio = credit_spread / sector_avg_spread if sector_avg_spread > 0 else 1.0
        
        if spread_ratio > 1.5:
            signals.append(('UNDERVALUED', 30))
        elif spread_ratio < 0.7:
            signals.append(('OVERVALUED', 30))
        else:
            signals.append(('NEUTRAL', 15))
        
        verdicts = {}
        for v, weight in signals:
            verdicts[v] = verdicts.get(v, 0) + weight
        
        final_verdict = max(verdicts, key=verdicts.get)
        confidence = min(95, verdicts[final_verdict])
        
        if bond['yield_pct'] > 10:
            final_verdict = 'JUNK_HIGH_YIELD'
            confidence = 50
        
        stats = {**yield_analysis, 'credit_spread': credit_spread}
        return final_verdict, confidence, stats
    
    def analyze(self, issuer):
        bond_row = self.bonds_df[self.bonds_df['issuer'] == issuer]
        if bond_row.empty:
            raise ValueError(f"Bond '{issuer}' not found")
        
        bond = bond_row.iloc[0].to_dict()
        peers = self.get_peers(bond)
        credit_spread = self.calculate_credit_spread(bond)
        yield_analysis = self.analyze_yield_spread(bond, peers)
        verdict, confidence, stats = self.generate_verdict(bond, yield_analysis, credit_spread)
        
        return {
            'agent': 'Bond007',
            'instrument_type': 'bond',
            'bond': bond,
            'peers': peers,
            'verdict': verdict,
            'confidence': confidence,
            'stats': stats,
            'credit_spread': credit_spread
        }
