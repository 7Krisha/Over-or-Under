import pandas as pd
from statistics import median, stdev
from typing import Dict, Tuple
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
    
    def calculate_intrinsic_values(self, equity):
        shares = equity['shares_out_m'] * 1_000_000
        eps = equity['net_income_b'] * 1_000_000_000 / shares
        book_value_per_share = (equity['total_assets_b'] - equity['total_liabilities_b']) * 1_000_000_000 / shares
        fcf_per_share = equity['fcf_b'] * 1_000_000_000 / shares
        
        graham = None
        if eps > 0 and book_value_per_share > 0:
            graham = (22.5 * eps * book_value_per_share) ** 0.5
        
        growth_rate = min(equity['eps_growth_5yr'] / 100, 0.25)
        discount_rate = 0.10
        
        dcf = None
        if fcf_per_share > 0 and growth_rate < discount_rate:
            terminal_value = (fcf_per_share * (1 + growth_rate)) / (discount_rate - growth_rate)
            dcf = terminal_value
        
        gordon = None
        if equity['dividend_yield'] > 0:
            dividend_per_share = equity['price'] * equity['dividend_yield'] / 100
            div_growth = min(growth_rate, 0.06)
            if div_growth < discount_rate:
                gordon = (dividend_per_share * (1 + div_growth)) / (discount_rate - div_growth)
        
        valid_values = []
        weights = []
        
        if graham:
            valid_values.append(graham)
            weights.append(0.3)
        if dcf:
            valid_values.append(dcf)
            weights.append(0.5)
        if gordon:
            valid_values.append(gordon)
            weights.append(0.2)
        
        weighted_fair_value = None
        margin_of_safety = None
        
        if valid_values:
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            weighted_fair_value = sum(v * w for v, w in zip(valid_values, normalized_weights))
            margin_of_safety = ((weighted_fair_value - equity['price']) / weighted_fair_value) * 100
        
        return {
            'graham_number': graham,
            'dcf_value': dcf,
            'gordon_value': gordon,
            'weighted_fair_value': weighted_fair_value,
            'margin_of_safety': margin_of_safety,
            'current_price': equity['price']
        }
    
    def market_valuation_metrics(self, equity, sector_benchmarks):
        pe = equity['pe_ratio']
        sector_cape = sector_benchmarks.get('cape_ratio', 25)
        cape_signal = 'OVERVALUED' if sector_cape > 25 else 'UNDERVALUED' if sector_cape < 15 else 'FAIR'
        
        buffett_signal = 'OVERVALUED'
        
        earnings_yield = 100 / pe if pe > 0 else 0
        treasury_yield = 4.58
        fed_spread = earnings_yield - treasury_yield
        fed_signal = 'UNDERVALUED' if fed_spread > 2 else 'OVERVALUED' if fed_spread < -1 else 'FAIR'
        
        inflation = 2.8
        fair_pe_rule20 = 20 - inflation
        rule20_deviation = ((pe - fair_pe_rule20) / fair_pe_rule20) * 100
        rule20_signal = 'OVERVALUED' if rule20_deviation > 20 else 'UNDERVALUED' if rule20_deviation < -20 else 'FAIR'
        
        growth = equity['eps_growth_5yr']
        peg = pe / growth if growth > 0 else None
        peg_signal = None
        if peg:
            peg_signal = 'UNDERVALUED' if peg < 1 else 'OVERVALUED' if peg > 2 else 'FAIR'
        
        return {
            'cape': {'value': sector_cape, 'signal': cape_signal},
            'buffett': {'signal': buffett_signal},
            'fed_model': {'earnings_yield': earnings_yield, 'treasury_yield': treasury_yield, 
                         'spread': fed_spread, 'signal': fed_signal},
            'rule_of_20': {'current_pe': pe, 'fair_pe': fair_pe_rule20, 
                          'deviation_pct': rule20_deviation, 'signal': rule20_signal},
            'peg': {'value': peg, 'signal': peg_signal}
        }
    
    def analyze_peer_multiples(self, equity, peers):
        if len(peers) < 2:
            return {'error': 'Insufficient peers'}
        
        results = {}
        
        peer_pe = peers['pe_ratio'].dropna()
        if len(peer_pe) >= 2:
            pe_median = median(peer_pe)
            pe_std = stdev(peer_pe)
            results['pe'] = {
                'value': equity['pe_ratio'],
                'peer_median': pe_median,
                'z_score': (equity['pe_ratio'] - pe_median) / pe_std if pe_std > 0 else 0
            }
        
        peer_pb = peers['pb_ratio'].dropna()
        if len(peer_pb) >= 2:
            pb_median = median(peer_pb)
            pb_std = stdev(peer_pb)
            results['pb'] = {
                'value': equity['pb_ratio'],
                'peer_median': pb_median,
                'z_score': (equity['pb_ratio'] - pb_median) / pb_std if pb_std > 0 else 0
            }
        
        peer_ev = peers['ev_ebitda'].dropna()
        if len(peer_ev) >= 2:
            ev_median = median(peer_ev)
            ev_std = stdev(peer_ev)
            results['ev_ebitda'] = {
                'value': equity['ev_ebitda'],
                'peer_median': ev_median,
                'z_score': (equity['ev_ebitda'] - ev_median) / ev_std if ev_std > 0 else 0
            }
        
        return results
    
    def generate_verdict(self, tobins_q, intrinsic, market_metrics, peer_multiples):
        overvalued_score = 0
        undervalued_score = 0
        total_weight = 0
        
        if tobins_q:
            if tobins_q > 1.5:
                overvalued_score += 15
            elif tobins_q < 0.8:
                undervalued_score += 15
            total_weight += 15
        
        if intrinsic.get('margin_of_safety'):
            mos = intrinsic['margin_of_safety']
            if mos > 20:
                undervalued_score += 30
            elif mos < -20:
                overvalued_score += 30
            else:
                if mos > 0:
                    undervalued_score += 15
                else:
                    overvalued_score += 15
            total_weight += 30
        
        market_signals = [
            market_metrics['cape']['signal'],
            market_metrics['fed_model']['signal'],
            market_metrics['rule_of_20']['signal'],
            market_metrics['peg']['signal'] if market_metrics['peg']['signal'] else 'FAIR'
        ]
        
        for signal in market_signals:
            if signal == 'OVERVALUED':
                overvalued_score += 7
            elif signal == 'UNDERVALUED':
                undervalued_score += 7
            total_weight += 7
        
        for metric in ['pe', 'pb', 'ev_ebitda']:
            if metric in peer_multiples:
                z = peer_multiples[metric]['z_score']
                if z > 1.5:
                    overvalued_score += 7
                elif z < -1.5:
                    undervalued_score += 7
                total_weight += 7
        
        if total_weight == 0:
            return 'INSUFFICIENT_DATA', 0, {}
        
        overvalued_pct = (overvalued_score / total_weight) * 100
        undervalued_pct = (undervalued_score / total_weight) * 100
        
        if overvalued_pct >= 60:
            verdict = 'OVERVALUED'
            confidence = min(95, int(overvalued_pct + 15))
        elif undervalued_pct >= 60:
            verdict = 'UNDERVALUED'
            confidence = min(95, int(undervalued_pct + 15))
        else:
            verdict = 'FAIRLY_VALUED'
            confidence = 70
        
        if tobins_q and tobins_q > 3:
            verdict = 'EXTREMELY_OVERVALUED'
            confidence = 95
        
        reasoning = {
            'overvalued_score': overvalued_score,
            'undervalued_score': undervalued_score,
            'total_weight': total_weight
        }
        
        return verdict, confidence, reasoning
    
    def analyze(self, ticker):
        equity_row = self.equities_df[self.equities_df['ticker'] == ticker]
        if equity_row.empty:
            raise ValueError(f"Ticker '{ticker}' not found")
        
        equity = equity_row.iloc[0].to_dict()
        sector_benchmarks = self.benchmarks.get(equity['sector'], {})
        
        tobins_q = self.calculate_tobins_q(equity)
        intrinsic_values = self.calculate_intrinsic_values(equity)
        market_metrics = self.market_valuation_metrics(equity, sector_benchmarks)
        peers = self.get_peers(equity)
        peer_multiples = self.analyze_peer_multiples(equity, peers)
        
        verdict, confidence, reasoning = self.generate_verdict(
            tobins_q, intrinsic_values, market_metrics, peer_multiples
        )
        
        return {
            'agent': 'Stonker',
            'instrument_type': 'equity',
            'equity': equity,
            'peers': peers,
            'tobins_q': tobins_q,
            'intrinsic_values': intrinsic_values,
            'market_metrics': market_metrics,
            'peer_multiples': peer_multiples,
            'verdict': verdict,
            'confidence': confidence,
            'reasoning': reasoning
        }
