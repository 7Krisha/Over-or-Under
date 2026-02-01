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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metrics styling */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
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
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Agent cards */
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
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
    if 'OVERVALUED' in verdict or 'OVERPRICED' in verdict:
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
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    if inst_type == 'equity':
        equity_data = r.get('equity', {})
        col1.metric("P/E Ratio", f"{equity_data.get('pe_ratio', 'N/A'):.1f}")
        col2.metric("P/B Ratio", f"{equity_data.get('pb_ratio', 'N/A'):.1f}")
        col3.metric("EV/EBITDA", f"{equity_data.get('ev_ebitda', 'N/A'):.1f}")
        col4.metric("Tobin's Q", f"{equity_data.get('tobins_q', 'N/A'):.2f}")
    elif inst_type == 'bond':
        bond_data = r.get('bond', {})
        col1.metric("Yield", f"{bond_data.get('yield', 0):.2f}%")
        col2.metric("Rating", bond_data.get('rating', 'N/A'))
        col3.metric("Duration", f"{bond_data.get('duration', 0):.1f} yrs")
        col4.metric("Spread", f"{bond_data.get('spread', 0):.0f} bps")
    else:
        deriv_data = r.get('derivative', {})
        col1.metric("IV", f"{deriv_data.get('iv', 0):.2f}")
        col2.metric("Historical Vol", f"{deriv_data.get('historical_vol', 0):.2f}")
        col3.metric("Delta", f"{deriv_data.get('delta', 0):.2f}")
        col4.metric("Theta", f"{deriv_data.get('theta', 0):.4f}")
    
    st.markdown("---")
    
    # AI Insight
    st.subheader("🤖 AI Insight")
    insight = r.get('insight', 'No insight available.')
    st.info(insight)
    
    # Peer Comparison Chart
    st.subheader("📊 Peer Comparison")
    
    if inst_type == 'equity':
        # Create peer comparison for equities
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
        # Create yield comparison for bonds
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
        # Create IV comparison for derivatives
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
    
    # ========== COUNTERFACTUAL ANALYSIS ==========
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
            new_pe = st.slider("P/E Ratio", 5.0, 150.0, float(original_pe), 0.5)
            new_pb = st.slider("P/B Ratio", 0.5, 50.0, float(original_pb), 0.1)
        
        with cf_col2:
            new_ev = st.slider("EV/EBITDA", 5.0, 100.0, float(original_ev), 0.5)
            new_tq = st.slider("Tobin's Q", 0.5, 5.0, float(original_tq), 0.05)
        
        # Recalculate verdict
        if st.button("🔄 Recalculate Verdict"):
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
            
            # Show comparison
            if new_verdict != verdict:
                st.success(f"✨ **Verdict Changed!**")
                st.markdown(f"**Original:** {verdict} ({confidence}% confidence)")
                st.markdown(f"**New:** {new_verdict} ({new_confidence}% confidence)")
                st.balloons()
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            # Show metric changes
            st.markdown("### 📉 Metric Changes:")
            change_col1, change_col2 = st.columns(2)
            with change_col1:
                st.metric("P/E Ratio", f"{new_pe:.1f}", f"{new_pe - original_pe:+.1f}")
                st.metric("P/B Ratio", f"{new_pb:.1f}", f"{new_pb - original_pb:+.1f}")
            with change_col2:
                st.metric("EV/EBITDA", f"{new_ev:.1f}", f"{new_ev - original_ev:+.1f}")
                st.metric("Tobin's Q", f"{new_tq:.2f}", f"{new_tq - original_tq:+.2f}")
    
    elif inst_type == 'bond':
        bond_data = r.get('bond', {})
        original_yield = bond_data.get('yield', 5.0)
        original_duration = bond_data.get('duration', 5.0)
        original_spread = bond_data.get('spread', 200)
        
        with cf_col1:
            new_yield = st.slider("Yield (%)", 0.5, 15.0, float(original_yield), 0.1)
            new_duration = st.slider("Duration (years)", 1.0, 30.0, float(original_duration), 0.5)
        
        with cf_col2:
            new_spread = st.slider("Spread (bps)", 10, 1000, int(original_spread), 10)
        
        if st.button("🔄 Recalculate Verdict"):
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
            
            if new_verdict != verdict:
                st.success(f"✨ **Verdict Changed!**")
                st.markdown(f"**Original:** {verdict} ({confidence}% confidence)")
                st.markdown(f"**New:** {new_verdict} ({new_confidence}% confidence)")
                st.balloons()
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            st.metric("New Yield", f"{new_yield:.2f}%", f"{new_yield - original_yield:+.2f}%")
    
    else:  # Derivatives
        deriv_data = r.get('derivative', {})
        original_iv = deriv_data.get('iv', 0.5)
        original_hv = deriv_data.get('historical_vol', 0.3)
        
        with cf_col1:
            new_iv = st.slider("Implied Volatility", 0.1, 2.0, float(original_iv), 0.05)
        
        with cf_col2:
            new_hv = st.slider("Historical Volatility", 0.1, 1.0, float(original_hv), 0.05)
        
        if st.button("🔄 Recalculate Verdict"):
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
            
            if new_verdict != verdict:
                st.success(f"✨ **Verdict Changed!**")
                st.markdown(f"**Original:** {verdict} ({confidence}% confidence)")
                st.markdown(f"**New:** {new_verdict} ({new_confidence}% confidence)")
                st.balloons()
            else:
                st.info(f"📊 Verdict remains: **{new_verdict}** ({new_confidence}% confidence)")
            
            st.metric("IV/HV Ratio", f"{iv_premium:.2f}x", f"{iv_premium - (original_iv/original_hv):+.2f}x")
    
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
