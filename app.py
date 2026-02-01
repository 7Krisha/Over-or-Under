import streamlit as st
import pandas as pd
from agents import Bond007, Stonker, CallMeMaybe, InsightGenerator

st.set_page_config(page_title="Over or Under", page_icon="🎯", layout="wide")

st.title("🎯 Over or Under")
st.markdown("**Multi-Agent Financial Valuation System**")
st.markdown("Bond007 🕶️ | Stonker 📈 | CallMeMaybe 📞")

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
        'equity': {'label': 'Assets', 'subcategory': 'Equities (Stocks)', 'agent': 'Stonker'},
        'bond': {'label': 'Debt', 'subcategory': 'Bonds (Fixed Income)', 'agent': 'Bond007'},
        'derivative': {'label': 'Derivatives', 'subcategory': 'Options', 'agent': 'CallMeMaybe'}
    }
    
    instrument_type = st.selectbox(
        "Select Asset Category:",
        ["equity", "bond", "derivative"],
        format_func=lambda x: f"{asset_categories[x]['label']} > {asset_categories[x]['subcategory']}"
    )
    
    selected_category = asset_categories[instrument_type]
    st.caption(f"Agent: {selected_category['agent']}")
    
    if instrument_type == 'bond':
        options = agents['bond007'].bonds_df['issuer'].tolist()
    elif instrument_type == 'equity':
        options = agents['stonker'].equities_df['ticker'].tolist()
    else:
        deriv_df = agents['call_me_maybe'].derivatives_df
        options = [f"{row['underlying']}_{row['type']}_{int(row['strike'])}" 
                  for _, row in deriv_df.iterrows()]
    
    selected = st.selectbox("Choose Instrument:", options)
    analyze_button = st.button("🚀 Analyze Now", type="primary", use_container_width=True)

if analyze_button:
    with st.spinner(f"{selected_category['agent']} is analyzing..."):
        try:
            if instrument_type == 'bond':
                result = agents['bond007'].analyze(selected)
            elif instrument_type == 'equity':
                result = agents['stonker'].analyze(selected)
            else:
                result = agents['call_me_maybe'].analyze(selected)
            
            explanation = agents['insight_gen'].generate_explanation(result)
            result['explanation'] = explanation
            
            st.session_state.result = result
            st.success(f"✅ Analysis complete!")
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
    
    st.markdown(f"## {verdict_emoji} {r['verdict'].replace('_', ' ')}")
    st.markdown(f"**Confidence:** {r['confidence']}%")
    
    st.info(f"**{r['agent']} says:** {r['explanation']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Agent", r['agent'])
    
    with col2:
        if r['instrument_type'] == 'bond':
            st.metric("Yield", f"{r['bond']['yield_pct']:.2f}%")
        elif r['instrument_type'] == 'equity':
            st.metric("Tobin's Q", f"{r.get('tobins_q', 0):.2f}")
        else:
            st.metric("IV Premium", f"{((r['derivative']['implied_vol'] - r['derivative']['historical_vol']) / r['derivative']['historical_vol'] * 100):.1f}%")
    
    with col3:
        st.metric("Peer Count", len(r['peers']))
    
    with st.expander("🔍 Technical Details"):
        st.json(r)

else:
    st.info("👈 Select an instrument from the sidebar to begin analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🕶️ Bond007")
        st.markdown("**Specialty:** Fixed Income")
        st.markdown("Credit spread analysis, yield curve positioning")
    
    with col2:
        st.markdown("### 📈 Stonker")
        st.markdown("**Specialty:** Equity Valuation")
        st.markdown("Tobin's Q, peer multiples, intrinsic value")
    
    with col3:
        st.markdown("### 📞 CallMeMaybe")
        st.markdown("**Specialty:** Options Analysis")
        st.markdown("Implied volatility, Greeks comparison")