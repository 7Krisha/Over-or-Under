import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agents import Bond007, Stonker, CallMeMaybe, InsightGenerator

st.set_page_config(
    page_title="Over or Under",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🎯 Over or Under</h1>
    <h3>Multi-Agent Financial Valuation System</h3>
    <p>Bond007 🕶️ | Stonker 📈 | CallMeMaybe 📞</p>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_agents():
    return {
        'bond007': Bond007(),
        'stonker': Stonker(),
        'call_me_maybe': CallMeMaybe(),
        'insight_gen': InsightGenerator()
    }

agents = get_agents()

with st.sidebar:
    st.header("🔍 Select Asset")
    
    asset_categories = {
        'equity': 'Stocks (Equities)',
        'bond': 'Bonds (Debt)',
        'derivative': 'Options (Derivatives)'
    }
    
    instrument_type = st.selectbox(
        "Select Asset Category:",
        ["equity", "bond", "derivative"],
        format_func=lambda x: asset_categories[x]
    )
    
    if instrument_type == 'bond':
        options = agents['bond007'].bonds_df['issuer'].tolist()
        agent_name = "Bond007 🕶️"
    elif instrument_type == 'equity':
        options = agents['stonker'].equities_df['ticker'].tolist()
        agent_name = "Stonker 📈"
    else:
        deriv_df = agents['call_me_maybe'].derivatives_df
        options = [f"{row['underlying']}_{row['type']}_{int(row['strike'])}" 
                  for _, row in deriv_df.iterrows()]
        agent_name = "CallMeMaybe 📞"
    
    selected = st.selectbox("Choose Instrument:", options)
    
    analyze_button = st.button("🚀 Analyze Now", type="primary", use_container_width=True)
    
if 'result' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px; margin-bottom: 1rem;'>
            <p style='font-size: 3rem; font-weight: bold; margin: 0; color: #667eea;'>{st.session_state.result['confidence']}%</p>
            <p style='font-size: 1rem; margin: 0; color: #666;'>Confidence</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
            <p style='font-size: 1.5rem; font-weight: bold; margin: 0;'>{st.session_state.result['verdict'].replace('_', ' ')}</p>
            <p style='font-size: 0.9rem; margin: 0; color: #666;'>Verdict</p>
        </div>
        """, unsafe_allow_html=True)

if analyze_button:
    with st.spinner(f"{agent_name} is analyzing..."):
        try:
            if instrument_type == 'bond':
                result = agents['bond007'].analyze(selected)
            elif instrument_type == 'equity':
                result = agents['stonker'].analyze(selected)
            else:
                result = agents['call_me_maybe'].analyze(selected)
            
            with st.spinner("🤖 Generating fun insights..."):
                explanation = agents['insight_gen'].generate_explanation(result)
                result['explanation'] = explanation
            
            st.session_state.result = result
            st.success(f"✅ {agent_name} has spoken!")
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if 'result' in st.session_state:
    r = st.session_state.result
    
    verdict_colors = {
        'OVERVALUED': '🔴',
        'UNDERVALUED': '🟢',
        'FAIRLY_VALUED': '🟡',
        'EXTREMELY_OVERVALUED': '🔴🔴',
        'MASSIVELY_OVERPRICED': '🔴🔴🔴',
        'JUNK_HIGH_YIELD': '🟠'
    }
    
    verdict_emoji = verdict_colors.get(r['verdict'], '⚪')
    
    st.markdown(f"# {verdict_emoji} {r['verdict'].replace('_', ' ')}")
    
    st.markdown("---")
    
    st.markdown(f"### 💬 {r['agent']} says:")
    
    explanation_text = r.get('explanation', 'Analysis complete.')
    
    if 'OVERVALUED' in r['verdict']:
        st.warning(f"😤 **{explanation_text}**")
    elif 'UNDERVALUED' in r['verdict']:
        st.success(f"💎 **{explanation_text}**")
    else:
        st.info(f"😊 **{explanation_text}**")
    
    st.markdown("---")
    
    if r['instrument_type'] == 'equity':
        
        st.subheader("📊 Valuation Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tobins_q = r.get('tobins_q', 0)
            st.metric("Tobin's Q", f"{tobins_q:.2f}" if tobins_q else "N/A")
        
        with col2:
            st.metric("P/E Ratio", f"{r['equity']['pe_ratio']:.1f}x")
        
        with col3:
            st.metric("P/B Ratio", f"{r['equity']['pb_ratio']:.1f}x")
        
        with col4:
            st.metric("EV/EBITDA", f"{r['equity']['ev_ebitda']:.1f}x")
        
        intrinsic = r.get('intrinsic_values', {})
        
        if intrinsic.get('weighted_fair_value'):
            st.markdown("### 💎 Intrinsic Value")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                graham = intrinsic.get('graham_number')
                st.metric("Graham", f"${graham:.2f}" if graham else "N/A")
            
            with col2:
                dcf = intrinsic.get('dcf_value')
                st.metric("DCF", f"${dcf:.2f}" if dcf else "N/A")
            
            with col3:
                gordon = intrinsic.get('gordon_value')
                st.metric("Gordon", f"${gordon:.2f}" if gordon else "N/A")
            
            with col4:
                st.metric("Current Price", f"${intrinsic['current_price']:.2f}")
            
            st.markdown(f"**Fair Value:** ${intrinsic['weighted_fair_value']:.2f}")
            
            mos = intrinsic.get('margin_of_safety', 0)
            if mos > 0:
                st.success(f"📈 Margin of Safety: +{mos:.1f}% (Underpriced!)")
            elif mos < 0:
                st.warning(f"📉 Margin of Safety: {mos:.1f}% (Overpriced!)")
        
        market_metrics = r.get('market_metrics', {})
        
        if market_metrics:
            st.markdown("### 🌍 5 Market Models")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cape = market_metrics.get('cape', {})
                st.markdown(f"**CAPE:** {cape.get('value', 'N/A')} - {cape.get('signal', 'N/A')}")
            
            with col2:
                fed = market_metrics.get('fed_model', {})
                st.markdown(f"**Fed Model:** {fed.get('spread', 0):.2f}% - {fed.get('signal', 'N/A')}")
            
            with col3:
                rule20 = market_metrics.get('rule_of_20', {})
                st.markdown(f"**Rule of 20:** {rule20.get('deviation_pct', 0):.1f}% deviation")
            
            col4, col5 = st.columns(2)
            
            with col4:
                peg = market_metrics.get('peg', {})
                peg_val = peg.get('value')
                st.markdown(f"**PEG:** {peg_val:.2f} - {peg.get('signal', 'N/A')}" if peg_val else "**PEG:** N/A")
            
            with col5:
                buffett = market_metrics.get('buffett', {})
                st.markdown(f"**Buffett Indicator:** {buffett.get('signal', 'N/A')}")
        
        st.markdown("### 📈 Peer Comparison")
        
        if len(r['peers']) > 0:
            fig = go.Figure()
            
            peers_df = r['peers']
            
            fig.add_trace(go.Scatter(
                x=peers_df['pe_ratio'],
                y=peers_df['pb_ratio'],
                mode='markers',
                name='Peers',
                marker=dict(size=12, color='lightblue'),
                text=peers_df['ticker']
            ))
            
            fig.add_trace(go.Scatter(
                x=[r['equity']['pe_ratio']],
                y=[r['equity']['pb_ratio']],
                mode='markers',
                name=r['equity']['ticker'],
                marker=dict(size=25, color='red', symbol='star'),
                text=[r['equity']['ticker']]
            ))
            
            if intrinsic.get('weighted_fair_value'):
                fair_value = intrinsic['weighted_fair_value']
                current_price = intrinsic['current_price']
                ratio = fair_value / current_price
                fair_pe = r['equity']['pe_ratio'] * ratio
                fair_pb = r['equity']['pb_ratio'] * ratio
                
                fig.add_trace(go.Scatter(
                    x=[fair_pe],
                    y=[fair_pb],
                    mode='markers',
                    name='Fair Value',
                    marker=dict(size=20, color='green', symbol='diamond')
                ))
            
            fig.update_layout(
                title=f"{r['equity']['ticker']} vs Peers",
                xaxis_title="P/E Ratio",
                yaxis_title="P/B Ratio",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔮 What-If Scenarios")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_pe = st.slider("P/E Ratio", 5.0, 200.0, float(r['equity']['pe_ratio']), 1.0)
        
        with col2:
            new_pb = st.slider("P/B Ratio", 0.5, 60.0, float(r['equity']['pb_ratio']), 0.5)
        
        with col3:
            new_ev = st.slider("EV/EBITDA", 5.0, 100.0, float(r['equity']['ev_ebitda']), 1.0)
        
        if st.button("🔄 Recalculate"):
            delta_pe = new_pe - r['equity']['pe_ratio']
            price_change = (delta_pe / r['equity']['pe_ratio']) * 100
            
            if abs(price_change) > 20:
                st.balloons()
                if price_change < 0:
                    st.success(f"🎉 Stock is being GREEDY! Needs {abs(price_change):.1f}% price drop to be fair!")
                else:
                    st.success(f"💎 Hidden gem! Could be {price_change:.1f}% undervalued!")
            else:
                st.info("📊 Small change - verdict likely similar")
    
    elif r['instrument_type'] == 'bond':
        st.subheader("📊 Bond Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Yield", f"{r['bond']['yield_pct']:.2f}%")
        
        with col2:
            stats = r.get('stats', {})
            peer_yield = stats.get('peer_median_yield', 0)
            st.metric("Peer Median", f"{peer_yield:.2f}%")
        
        with col3:
            spread = r.get('credit_spread', 0)
            st.metric("Credit Spread", f"{spread:.2f}%")
        
        if len(r['peers']) > 0:
            st.markdown("### 📈 Yield vs Peers")
            
            fig = go.Figure()
            
            peers_df = r['peers']
            
            fig.add_trace(go.Bar(
                x=peers_df['issuer'],
                y=peers_df['yield_pct'],
                marker_color='lightblue'
            ))
            
            fig.add_hline(y=r['bond']['yield_pct'], line_color="red", 
                         annotation_text=f"{r['bond']['issuer']}: {r['bond']['yield_pct']:.2f}%")
            
            fig.update_layout(title="Bond Yield Comparison", height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.subheader("📊 Options Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Implied Vol", f"{r['derivative']['implied_vol']:.2%}")
        
        with col2:
            st.metric("Historical Vol", f"{r['derivative']['historical_vol']:.2%}")
        
        with col3:
            iv_prem = ((r['derivative']['implied_vol'] - r['derivative']['historical_vol']) / r['derivative']['historical_vol']) * 100
            st.metric("IV Premium", f"{iv_prem:.1f}%")
        
        st.markdown("### 📈 Volatility")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(x=['Historical'], y=[r['derivative']['historical_vol']], marker_color='blue'))
        fig.add_trace(go.Bar(x=['Implied'], y=[r['derivative']['implied_vol']], marker_color='red'))
        
        fig.update_layout(title="Volatility Comparison", height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🔍 Technical Details"):
        st.json(r)

else:
    st.info("👈 Select an instrument to analyze")
