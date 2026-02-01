import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from agents import Bond007, Stonker, CallMeMaybe, InsightGenerator

# Page config with custom theme
st.set_page_config(
    page_title="Over or Under - Financial Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
    }
    .main-header h3 {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 400;
    }
    .main-header p {
        color: rgba(255,255,255,0.8) !important;
        margin-bottom: 0;
    }
    
    /* Verdict cards */
    .verdict-card {
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Fun insight box */
    .fun-insight {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .fun-insight h4 {
        margin: 0 0 0.5rem 0;
        color: #333;
    }
    .fun-insight p {
        margin: 0;
        font-size: 1.1rem;
        line-height: 1.5;
    }
    
    /* Metrics styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #5a6fd6 0%, #6a4190 100%);
        color: white;
    }
    
    /* Verdict colors */
    .verdict-overvalued {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
    }
    .verdict-undervalued {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
    }
    .verdict-fair {
        background: linear-gradient(135deg, #ffd43b 0%, #fab005 100%);
    }
</style>
""", unsafe_allow_html=True)

# ========== FUN INSIGHT GENERATORS ==========
def get_fun_verdict_insight(verdict: str, instrument_type: str, data: dict) -> str:
    """Generate fun, witty insights based on the verdict"""
    
    if instrument_type == 'equity':
        ticker = data.get('ticker', 'This stock')
        pe = data.get('pe_ratio', 0)
        pb = data.get('pb_ratio', 0)
        
        if 'EXTREMELY_OVERVALUED' in verdict:
            return f"🔥 **Whoa there, hot shot!** {ticker} is partying like it's 1999! With a P/E of {pe:.1f}x, Wall Street is being EXTREMELY greedy. This isn't investing, it's hoping for a greater fool. The music will stop eventually... 🎵💸"
        elif 'OVERVALUED' in verdict:
            return f"💰 **Cha-ching... for someone else!** {ticker} is priced like it cures cancer AND makes coffee. At P/E {pe:.1f}x, you're paying premium prices for regular gas. The market's optimism is... let's say 'ambitious'. 🤑"
        elif 'UNDERVALUED' in verdict:
            return f"💎 **Hidden gem alert!** {ticker} is being slept on harder than a forgotten gym membership. P/E of {pe:.1f}x? That's bargain bin territory! Either the market knows something we don't, or you just found dinner at breakfast prices. 🍳"
        elif 'FAIRLY_VALUED' in verdict:
            return f"⚖️ **Goldilocks zone!** {ticker} is priced juuust right. Not too hot, not too cold. P/E of {pe:.1f}x is reasonable - you're paying fair value for what you get. Boring? Maybe. Smart? Definitely. 🐻"
        else:
            return f"🤔 **Interesting...** {ticker} is giving mixed signals. The numbers say one thing, but the vibes say another. Proceed with curious caution! 🔍"
    
    elif instrument_type == 'bond':
        issuer = data.get('issuer', 'This bond')
        yield_val = data.get('yield', 0)
        rating = data.get('rating', 'N/A')
        
        if 'JUNK' in verdict or 'HIGH_YIELD' in verdict:
            return f"🎰 **High roller alert!** {issuer} at {yield_val:.2f}% yield is basically the casino of bonds. Rating: {rating}. Sure, the yield is juicy, but so is the risk. Only play with money you can afford to see vanish! 🎲"
        elif 'PREMIUM' in verdict or 'SAFE' in verdict:
            return f"🏦 **Sleep-well-at-night territory!** {issuer} with {rating} rating is the financial equivalent of a warm blanket. {yield_val:.2f}% isn't exciting, but neither is losing money. Sometimes boring = beautiful. 😴💰"
        elif 'OVERVALUED' in verdict:
            return f"🤨 **Hmm, someone's popular!** {issuer} is priced like it's backed by actual gold bars. At {yield_val:.2f}% yield, you're not getting paid enough for the privilege. Shop around! 🛒"
        elif 'UNDERVALUED' in verdict:
            return f"🎁 **Gift alert!** {issuer} is offering {yield_val:.2f}% yield - that's generous for a {rating} rating. Either the market's asleep or there's fine print. Worth a deeper look! 🔎"
        else:
            return f"📊 **Solid pick!** {issuer} at {yield_val:.2f}% is doing exactly what bonds should do - be predictably boring. Your future self will thank you. 🙏"
    
    else:  # derivatives
        underlying = data.get('underlying', 'This option')
        iv = data.get('iv', 0)
        hv = data.get('historical_vol', 0)
        
        if 'MASSIVELY_OVERPRICED' in verdict:
            return f"🚨 **DANGER ZONE!** {underlying} options are priced like volatility is going to the moon! IV of {iv:.2f} vs historical {hv:.2f}? Someone's selling lottery tickets at diamond prices. Hard pass unless you're selling! 📉"
        elif 'OVERPRICED' in verdict:
            return f"💸 **Pricey vibes!** {underlying} options have IV pumped up to {iv:.2f} (historical: {hv:.2f}). The options market is charging fear premium. Consider being the house, not the gambler! 🎰"
        elif 'UNDERPRICED' in verdict:
            return f"🎯 **Rare find!** {underlying} options at IV {iv:.2f} vs historical {hv:.2f}? The market's being generous with volatility pricing. This is when smart money loads up! 🧠💰"
        else:
            return f"⚖️ **Fair game!** {underlying} options are priced reasonably. IV {iv:.2f} vs historical {hv:.2f} - no edge here, but no trap either. Trade if you have a thesis! 📈"

def get_counterfactual_insight(original_verdict: str, new_verdict: str, changes: dict, instrument_type: str) -> str:
    """Generate witty counterfactual insights"""
    
    if instrument_type == 'equity':
        pe_change = changes.get('pe_change', 0)
        price_change_pct = changes.get('price_change_pct', 0)
        
        if 'OVERVALUED' in original_verdict and 'OVERVALUED' not in new_verdict:
            return f"💰 **Reality check unlocked!** Drop that P/E by {abs(pe_change):.1f} points (~{abs(price_change_pct):.1f}% price correction) and suddenly Wall Street stops being greedy! This stock goes from 'lol no' to 'hmm interesting...' 🤔"
        elif 'UNDERVALUED' in original_verdict and 'UNDERVALUED' not in new_verdict:
            return f"📈 **Hype machine activated!** Pump those metrics up and watch the bargain disappear! A {abs(price_change_pct):.1f}% rise would price out the value. Get in before the crowd! 🏃‍♂️"
        elif 'OVERVALUED' not in original_verdict and 'OVERVALUED' in new_verdict:
            return f"🎢 **Welcome to Bubble Town!** Push those numbers higher and you've got yourself a classic overvaluation. This is what FOMO looks like in spreadsheet form! 📊"
        else:
            return f"🔄 **Plot twist!** Adjust these metrics and the whole story changes. Markets are just vibes with math attached! ✨"
    
    elif instrument_type == 'bond':
        yield_change = changes.get('yield_change', 0)
        
        if yield_change > 0:
            return f"📈 **Risk premium adjusted!** Bump that yield by {abs(yield_change):.2f}% and suddenly the risk-reward makes sense. Bonds are just IOUs with personality! 💸"
        else:
            return f"📉 **Premium pricing!** Cut the yield by {abs(yield_change):.2f}% and you're paying luxury prices. Sometimes the best trade is no trade! 🧘"
    
    else:
        iv_change = changes.get('iv_change', 0)
        
        if iv_change < 0:
            return f"😌 **Volatility chills out!** Drop IV by {abs(iv_change):.2f} and those expensive options become reasonable. Fear is expensive, patience is cheap! 🧘‍♂️"
        else:
            return f"🌪️ **Chaos premium!** Crank up the IV and watch option prices go brrr. Volatility is the only free lunch that actually costs money! 💨"


# Initialize agents (cached for performance)
@st.cache_resource
def get_agents():
    return {
        'bond007': Bond007(),
        'stonker': Stonker(),
        'call_me_maybe': CallMeMaybe(),
        'insight_gen': InsightGenerator()
    }

agents = get_agents()

# Header with gradient background
st.markdown("""
<div class="main-header">
    <h1>🎯 Over or Under</h1>
    <h3>Multi-Agent Financial Valuation System</h3>
    <p>Bond007 🕶️ | Stonker 📈 | CallMeMaybe 📞</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with improved styling
with st.sidebar:
    st.markdown("## 🔍 Analysis Controls")
    
    # Agent selector with emojis
    instrument_type = st.selectbox(
        "Select Asset Class:",
        ["equity", "bond", "derivative"],
        format_func=lambda x: {
            'equity': '📈 Equities (Stocks)',
            'bond': '📊 Bonds (Fixed Income)',
            'derivative': '📉 Derivatives (Options)'
        }[x]
    )
    
    # Dynamic info based on selection
    info_text = {
        'equity': "💡 **Tobin's Q > 1.5** typically indicates overvaluation",
        'bond': "💡 **Higher yield** generally means undervalued (better deal)",
        'derivative': "💡 **High IV** means expensive option pricing"
    }
    st.info(info_text[instrument_type])
    
    # Get available instruments
    if instrument_type == 'bond':
        options = agents['bond007'].bonds_df['issuer'].tolist()
        agent_name = "Bond007 🕶️"
    elif instrument_type == 'equity':
        options = agents['stonker'].equities_df['ticker'].tolist()
        agent_name = "Stonker 📈"
    else:
        deriv_df = agents['call_me_maybe'].derivatives_df
        options = [
            f"{row['underlying']}_{row['type']}_{idx}" 
            for idx, row in deriv_df.iterrows()
        ]
        agent_name = "CallMeMaybe 📞"
    
    selected = st.selectbox(f"Select {instrument_type.title()}:", options)
    
    st.markdown("---")
    st.markdown(f"**Active Agent:** {agent_name}")
    
    analyze_btn = st.button("🚀 Analyze Now", use_container_width=True)

# Main content area
if analyze_btn:
    with st.spinner(f"{agent_name} is analyzing..."):
        # Run analysis based on type
        if instrument_type == 'bond':
            result = agents['bond007'].analyze(selected)
        elif instrument_type == 'equity':
            result = agents['stonker'].analyze(selected)
        else:
            # Parse derivative selection
            parts = selected.rsplit('_', 2)
            underlying = parts[0]
            opt_type = parts[1]
            idx = int(parts[2])
            result = agents['call_me_maybe'].analyze(underlying, opt_type, idx)
        
        # Store result in session state
        st.session_state.result = result
        st.session_state.instrument_type = instrument_type

# Display results
if 'result' in st.session_state:
    r = st.session_state.result
    inst_type = st.session_state.instrument_type
    
    # Verdict banner with dynamic color
    verdict = r.get('verdict', 'UNKNOWN')
    confidence = r.get('confidence', 0)
    
    # Determine verdict color class
    if 'OVERVALUED' in verdict or 'OVERPRICED' in verdict or 'JUNK' in verdict:
        verdict_class = "verdict-overvalued"
        verdict_emoji = "🔴"
    elif 'UNDERVALUED' in verdict or 'UNDERPRICED' in verdict:
        verdict_class = "verdict-undervalued"
        verdict_emoji = "🟢"
    else:
        verdict_class = "verdict-fair"
        verdict_emoji = "🟡"
    
    st.markdown(f"""
    <div class="verdict-card {verdict_class}">
        <h2 style="color: white; margin: 0;">{verdict_emoji} {verdict}</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
            Confidence: {confidence}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")  # Spacing
    
    # ========== FUN AI INSIGHT ==========
    if inst_type == 'equity':
        data_for_insight = r.get('equity', {})
    elif inst_type == 'bond':
        data_for_insight = r.get('bond', {})
    else:
        data_for_insight = r.get('derivative', {})
    
    fun_insight = get_fun_verdict_insight(verdict, inst_type, data_for_insight)
    
    st.markdown(f"""
    <div class="fun-insight">
        <h4>🤖 {agent_name.split()[0]} Says:</h4>
        <p>{fun_insight}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    if inst_type == 'equity':
        equity_data = r.get('equity', {})
        col1.metric("P/E Ratio", f"{equity_data.get('pe_ratio', 'N/A'):.1f}x")
        col2.metric("P/B Ratio", f"{equity_data.get('pb_ratio', 'N/A'):.1f}x")
        col3.metric("EV/EBITDA", f"{equity_data.get('ev_ebitda', 'N/A'):.1f}x")
        col4.metric("Tobin's Q", f"{equity_data.get('tobins_q', 'N/A'):.2f}")
    elif inst_type == 'bond':
        bond_data = r.get('bond', {})
        col1.metric("Yield", f"{bond_data.get('yield', 0):.2f}%")
        col2.metric("Rating", bond_data.get('rating', 'N/A'))
        col3.metric("Duration", f"{bond_data.get('duration', 0):.1f} yrs")
        col4.metric("Spread", f"{bond_data.get('spread', 0):.0f} bps")
    else:
        deriv_data = r.get('derivative', {})
        col1.metric("IV", f"{deriv_data.get('iv', 0)*100:.1f}%")
        col2.metric("Historical Vol", f"{deriv_data.get('historical_vol', 0)*100:.1f}%")
        col3.metric("Delta", f"{deriv_data.get('delta', 0):.2f}")
        col4.metric("Theta", f"{deriv_data.get('theta', 0):.4f}")
    
    st.markdown("---")
    
    # Peer Comparison Chart
    st.subheader("📊 Peer Comparison")
    
    if inst_type == 'equity':
        peers_df = agents['stonker'].equities_df.head(5)
        fig = px.bar(
            peers_df, 
            x='ticker', 
            y='pe_ratio',
            color='pe_ratio',
            color_continuous_scale='RdYlGn_r',
            title='P/E Ratio Comparison'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif inst_type == 'bond':
        bonds_df = agents['bond007'].bonds_df.head(5)
        fig = px.bar(
            bonds_df,
            x='issuer',
            y='yield',
            color='yield',
            color_continuous_scale='RdYlGn',
            title='Yield Comparison'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        derivs_df = agents['call_me_maybe'].derivatives_df.head(5)
        fig = px.bar(
            derivs_df,
            x='underlying',
            y='iv',
            color='iv',
            color_continuous_scale='RdYlGn_r',
            title='Implied Volatility Comparison'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ========== COUNTERFACTUAL ANALYSIS WITH GRAPH ==========
    st.markdown("---")
    st.subheader("🔮 Counterfactual Analysis: What-If Scenarios")
    st.markdown("*Adjust the sliders to see how different metrics would change the verdict*")
    
    cf_col1, cf_col2 = st.columns(2)
    
    if inst_type == 'equity':
        equity_data = r.get('equity', {})
        original_pe = equity_data.get('pe_ratio', 30)
        original_pb = equity_data.get('pb_ratio', 5)
        original_ev = equity_data.get('ev_ebitda', 20)
        original_tq = equity_data.get('tobins_q', 1.5)
        
        with cf_col1:
            new_pe = st.slider("📊 P/E Ratio", 5.0, 150.0, float(original_pe), 0.5)
            new_pb = st.slider("📈 P/B Ratio", 0.5, 50.0, float(original_pb), 0.1)
        
        with cf_col2:
            new_ev = st.slider("💰 EV/EBITDA", 5.0, 100.0, float(original_ev), 0.5)
            new_tq = st.slider("🏛️ Tobin's Q", 0.5, 5.0, float(original_tq), 0.05)
        
        # Recalculate verdict
        if st.button("🔄 Recalculate Verdict", key="equity_recalc"):
            # Simple scoring logic
            score = 0
            if new_pe > 25: score += 1
            if new_pe > 50: score += 1
            if new_pe > 100: score += 1
            if new_pb > 10: score += 1
            if new_pb > 30: score += 1
            if new_ev > 30: score += 1
            if new_ev > 60: score += 1
            if new_tq > 1.5: score += 1
            if new_tq > 2.5: score += 1
            
            if score >= 6:
                new_verdict = "EXTREMELY_OVERVALUED"
                new_confidence = 95
            elif score >= 4:
                new_verdict = "OVERVALUED"
                new_confidence = 80
            elif score >= 2:
                new_verdict = "FAIRLY_VALUED"
                new_confidence = 70
            else:
                new_verdict = "UNDERVALUED"
                new_confidence = 85
            
            # Calculate changes
            pe_change = new_pe - original_pe
            price_change_pct = (pe_change / original_pe) * 100 if original_pe > 0 else 0
            
            # ========== COUNTERFACTUAL COMPARISON GRAPH ==========
            st.markdown("### 📊 Before vs After Comparison")
            
            # Create comparison chart
            metrics = ['P/E', 'P/B', 'EV/EBITDA', 'Tobin\'s Q']
            original_values = [original_pe, original_pb, original_ev, original_tq * 20]  # Scale Tobin's Q for visibility
            new_values = [new_pe, new_pb, new_ev, new_tq * 20]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Original',
                x=metrics,
                y=original_values,
                marker_color='#667eea',
                text=[f"{original_pe:.1f}x", f"{original_pb:.1f}x", f"{original_ev:.1f}x", f"{original_tq:.2f}"],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='What-If',
                x=metrics,
                y=new_values,
                marker_color='#f093fb',
                text=[f"{new_pe:.1f}x", f"{new_pb:.1f}x", f"{new_ev:.1f}x", f"{new_tq:.2f}"],
                textposition='outside'
            ))
            
            fig.update_layout(
                barmode='group',
                title=f'Metric Comparison: {verdict} → {new_verdict}',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show verdict change
            verdict_changed = new_verdict != verdict
            
            if verdict_changed:
                st.balloons()
                st.success(f"✨ **Verdict Changed!** {verdict} → {new_verdict}")
                
                # Fun counterfactual insight
                changes = {'pe_change': pe_change, 'price_change_pct': price_change_pct}
                cf_insight = get_counterfactual_insight(verdict, new_verdict, changes, 'equity')
                st.info(cf_insight)
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            # Metric changes
            st.markdown("### 📉 Metric Changes:")
            change_col1, change_col2 = st.columns(2)
            with change_col1:
                st.metric("P/E Ratio", f"{new_pe:.1f}x", f"{pe_change:+.1f}")
                st.metric("P/B Ratio", f"{new_pb:.1f}x", f"{new_pb - original_pb:+.1f}")
            with change_col2:
                st.metric("EV/EBITDA", f"{new_ev:.1f}x", f"{new_ev - original_ev:+.1f}")
                st.metric("Tobin's Q", f"{new_tq:.2f}", f"{new_tq - original_tq:+.2f}")
    
    elif inst_type == 'bond':
        bond_data = r.get('bond', {})
        original_yield = bond_data.get('yield', 5.0)
        original_duration = bond_data.get('duration', 5.0)
        original_spread = bond_data.get('spread', 200)
        
        with cf_col1:
            new_yield = st.slider("💰 Yield (%)", 0.5, 15.0, float(original_yield), 0.1)
            new_duration = st.slider("⏱️ Duration (years)", 1.0, 30.0, float(original_duration), 0.5)
        
        with cf_col2:
            new_spread = st.slider("📏 Spread (bps)", 10, 1000, int(original_spread), 10)
        
        if st.button("🔄 Recalculate Verdict", key="bond_recalc"):
            # Simple bond scoring
            if new_yield > 10 or new_spread > 600:
                new_verdict = "JUNK_HIGH_YIELD"
                new_confidence = 90
            elif new_yield > 7 or new_spread > 400:
                new_verdict = "HIGH_YIELD_RISKY"
                new_confidence = 80
            elif new_yield < 3 and new_spread < 100:
                new_verdict = "PREMIUM_SAFE"
                new_confidence = 85
            else:
                new_verdict = "FAIRLY_VALUED"
                new_confidence = 75
            
            yield_change = new_yield - original_yield
            
            # ========== COUNTERFACTUAL COMPARISON GRAPH ==========
            st.markdown("### 📊 Before vs After Comparison")
            
            metrics = ['Yield (%)', 'Duration (yrs)', 'Spread (bps/10)']
            original_values = [original_yield, original_duration, original_spread/10]
            new_values = [new_yield, new_duration, new_spread/10]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Original',
                x=metrics,
                y=original_values,
                marker_color='#667eea',
                text=[f"{original_yield:.2f}%", f"{original_duration:.1f}y", f"{original_spread}bps"],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='What-If',
                x=metrics,
                y=new_values,
                marker_color='#f093fb',
                text=[f"{new_yield:.2f}%", f"{new_duration:.1f}y", f"{new_spread}bps"],
                textposition='outside'
            ))
            
            fig.update_layout(
                barmode='group',
                title=f'Metric Comparison: {verdict} → {new_verdict}',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            verdict_changed = new_verdict != verdict
            
            if verdict_changed:
                st.balloons()
                st.success(f"✨ **Verdict Changed!** {verdict} → {new_verdict}")
                
                changes = {'yield_change': yield_change}
                cf_insight = get_counterfactual_insight(verdict, new_verdict, changes, 'bond')
                st.info(cf_insight)
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            st.metric("New Yield", f"{new_yield:.2f}%", f"{yield_change:+.2f}%")
    
    else:  # Derivatives
        deriv_data = r.get('derivative', {})
        original_iv = deriv_data.get('iv', 0.5)
        original_hv = deriv_data.get('historical_vol', 0.3)
        
        with cf_col1:
            new_iv = st.slider("📈 Implied Volatility", 0.1, 2.0, float(original_iv), 0.05)
        
        with cf_col2:
            new_hv = st.slider("📊 Historical Volatility", 0.1, 1.0, float(original_hv), 0.05)
        
        if st.button("🔄 Recalculate Verdict", key="deriv_recalc"):
            iv_premium = new_iv / new_hv if new_hv > 0 else 1
            
            if iv_premium > 3:
                new_verdict = "MASSIVELY_OVERPRICED"
                new_confidence = 95
            elif iv_premium > 2:
                new_verdict = "OVERPRICED"
                new_confidence = 85
            elif iv_premium > 1.2:
                new_verdict = "SLIGHTLY_OVERPRICED"
                new_confidence = 70
            elif iv_premium < 0.8:
                new_verdict = "UNDERPRICED"
                new_confidence = 80
            else:
                new_verdict = "FAIRLY_PRICED"
                new_confidence = 75
            
            iv_change = new_iv - original_iv
            
            # ========== COUNTERFACTUAL COMPARISON GRAPH ==========
            st.markdown("### 📊 Before vs After Comparison")
            
            original_ratio = original_iv / original_hv if original_hv > 0 else 1
            new_ratio = iv_premium
            
            fig = go.Figure()
            
            # IV vs HV comparison
            fig.add_trace(go.Bar(
                name='Original',
                x=['IV', 'Historical Vol', 'IV/HV Ratio'],
                y=[original_iv * 100, original_hv * 100, original_ratio],
                marker_color='#667eea',
                text=[f"{original_iv*100:.1f}%", f"{original_hv*100:.1f}%", f"{original_ratio:.2f}x"],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='What-If',
                x=['IV', 'Historical Vol', 'IV/HV Ratio'],
                y=[new_iv * 100, new_hv * 100, new_ratio],
                marker_color='#f093fb',
                text=[f"{new_iv*100:.1f}%", f"{new_hv*100:.1f}%", f"{new_ratio:.2f}x"],
                textposition='outside'
            ))
            
            fig.update_layout(
                barmode='group',
                title=f'Volatility Comparison: {verdict} → {new_verdict}',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            verdict_changed = new_verdict != verdict
            
            if verdict_changed:
                st.balloons()
                st.success(f"✨ **Verdict Changed!** {verdict} → {new_verdict}")
                
                changes = {'iv_change': iv_change}
                cf_insight = get_counterfactual_insight(verdict, new_verdict, changes, 'derivative')
                st.info(cf_insight)
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            st.metric("IV/HV Ratio", f"{iv_premium:.2f}x", f"{iv_premium - original_ratio:+.2f}x")
    
    # Technical details expander
    with st.expander("🔍 Technical Analysis Details"):
        st.json(r)

# Footer with features when no analysis yet
else:
    st.markdown("---")
    st.markdown("### ✨ Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **🎯 Zero Hallucinations**
        
        All calculations are deterministic
        """)
    
    with col2:
        st.markdown("""
        **⚡ Sub-Second Analysis**
        
        Financial engine runs in <100ms
        """)
    
    with col3:
        st.markdown("""
        **🔍 Fully Auditable**
        
        Every verdict traces back to transparent calculations
        """)
    
    with col4:
        st.markdown("""
        **📊 Multi-Asset Support**
        
        Bonds, equities, and derivatives
        """)
    
    # Demo suggestion
    st.markdown("---")
    st.markdown("### 🎮 Try These Demo Examples:")
    
    demo_col1, demo_col2, demo_col3 = st.columns(3)
    
    with demo_col1:
        st.info("**NVDA** (Equity)\n\nExpected: 🔴 EXTREMELY OVERVALUED\n\nP/E of 115.3 is way above sector average")
    
    with demo_col2:
        st.info("**Junk Inc 2030** (Bond)\n\nExpected: 🟠 JUNK_HIGH_YIELD\n\n12.5% yield with B- rating")
    
    with demo_col3:
        st.info("**SCAM_call_10** (Option)\n\nExpected: 🔴 MASSIVELY OVERPRICED\n\nIV of 1.85 vs historical 0.35")
