"""
Page 8: Emergency Contacts Directory — Full state-wise searchable directory
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME, get_ui_string
from modules.emergency_handler import load_emergency_contacts, get_cities_by_state, get_states

st.set_page_config(page_title=f"Emergency Contacts — {APP_NAME}", page_icon="📞", layout="wide")

if 'lang' not in st.session_state:
    st.session_state.lang = "en"
lang = st.session_state.lang
t = lambda key: get_ui_string(key, lang)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #030712 0%, #0f172a 50%, #1e1b4b 100%); }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        border-right: 1px solid rgba(99,102,241,0.12);
    }
    .page-hdr { text-align:center; padding:1rem 0 1.5rem; }
    .page-ttl {
        font-family:'Space Grotesk',sans-serif;
        font-size:2.2rem; font-weight:700;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .contact-card {
        background: rgba(30,41,59,0.45);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 0.6rem;
        transition: all 0.3s;
    }
    .contact-card:hover { border-color: rgba(139,92,246,0.3); transform: translateX(4px); }
    .cc-city { color: #e2e8f0; font-weight: 700; font-size: 1.05rem; }
    .cc-hosp { color: #a78bfa; font-size: 0.88rem; }
    .cc-phone { color: #94a3b8; font-size: 0.9rem; }
    .cc-nums { display:flex; gap:0.75rem; margin-top:0.5rem; flex-wrap:wrap; }
    .cc-num { background:rgba(30,41,59,0.5); border:1px solid rgba(99,102,241,0.1); color:#e2e8f0; padding:3px 10px; border-radius:8px; font-size:0.8rem; font-weight:600; }
    .stButton > button { background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="page-hdr">
    <div class="page-ttl">📞 {t('emergency_contacts')}</div>
    <div style="color:#64748b; font-size:0.92rem; margin-top:6px;">Complete emergency directory for South India</div>
</div>
""", unsafe_allow_html=True)

df = load_emergency_contacts()

if df is not None:
    # Search
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search city or hospital...", key="ec_search")
    with col2:
        states = ["All States"] + get_states()
        sel_state = st.selectbox("Filter by State", states, key="ec_state")

    # Filter
    filtered = df.copy()
    if sel_state != "All States":
        filtered = filtered[filtered['State'] == sel_state]
    if search:
        mask = (
            filtered['City'].str.lower().str.contains(search.lower(), na=False) |
            filtered['Hospital_Name'].str.lower().str.contains(search.lower(), na=False)
        )
        filtered = filtered[mask]

    st.caption(f"📍 Showing {len(filtered)} of {len(df)} cities")

    # Display
    for _, row in filtered.iterrows():
        st.markdown(f"""
        <div class="contact-card">
            <div class="cc-city">📍 {row['City']}</div>
            <div class="cc-hosp">🏥 {row['Hospital_Name']} — {row.get('Type', 'Government')}</div>
            <div class="cc-phone">📞 {row['Emergency_Phone']}</div>
            <div class="cc-nums">
                <span class="cc-num">🚑 {row.get('Ambulance', '108')}</span>
                <span class="cc-num">👮 {row.get('Police', '100')}</span>
                <span class="cc-num">🔥 {row.get('Fire', '101')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Download
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Full Directory (CSV)", csv, "emergency_contacts.csv", "text/csv", use_container_width=True)
else:
    st.error("❌ Emergency contacts not available.")

st.markdown(f"""
<div style="text-align:center; color:#475569; font-size:0.8rem; padding:1rem;">
    {t('disclaimer')}
</div>
""", unsafe_allow_html=True)
