"""
Page 6: SOS Emergency — One-tap emergency access with city-specific contacts
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME, get_ui_string, LANGUAGES
from modules.emergency_handler import load_emergency_contacts, get_cities_by_state, get_states, get_emergency_contact, get_nearby_hospitals

st.set_page_config(page_title=f"SOS Emergency — {APP_NAME}", page_icon="🚨", layout="wide")

# Session state
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
lang = st.session_state.lang
t = lambda key: get_ui_string(key, lang)

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #1a0000 0%, #2d0a0a 30%, #0f172a 70%, #0a0f1c 100%); }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a0505 0%, #0f172a 100%);
        border-right: 1px solid rgba(239,68,68,0.15);
    }

    @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

    .sos-header {
        text-align: center;
        padding: 1.5rem 0;
    }
    .sos-icon { font-size: 4rem; animation: pulse 1s infinite; }
    .sos-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: #ef4444;
        text-shadow: 0 0 40px rgba(239,68,68,0.3);
        margin: 0.5rem 0;
    }
    .sos-subtitle { color: #fca5a5; font-size: 1rem; }

    /* Emergency Buttons */
    .sos-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    @media (max-width: 768px) { .sos-grid { grid-template-columns: repeat(2, 1fr); } }
    
    .sos-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        text-decoration: none;
    }
    .sos-btn:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .sos-btn-icon { font-size: 3rem; margin-bottom: 0.75rem; }
    .sos-btn-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem; }
    .sos-btn-num { font-size: 2rem; font-weight: 900; font-family: 'Space Grotesk', sans-serif; }
    .sos-btn-sub { font-size: 0.75rem; margin-top: 0.5rem; opacity: 0.7; }
    
    .btn-ambulance {
        background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(220,38,38,0.1));
        border: 2px solid rgba(239,68,68,0.4);
        color: #fca5a5;
    }
    .btn-ambulance:hover { border-color: #ef4444; background: rgba(239,68,68,0.25); }
    .btn-police {
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(37,99,235,0.1));
        border: 2px solid rgba(59,130,246,0.4);
        color: #93c5fd;
    }
    .btn-police:hover { border-color: #3b82f6; }
    .btn-fire {
        background: linear-gradient(135deg, rgba(249,115,22,0.2), rgba(234,88,12,0.1));
        border: 2px solid rgba(249,115,22,0.4);
        color: #fdba74;
    }
    .btn-fire:hover { border-color: #f97316; }
    .btn-women {
        background: linear-gradient(135deg, rgba(236,72,153,0.2), rgba(219,39,119,0.1));
        border: 2px solid rgba(236,72,153,0.4);
        color: #f9a8d4;
    }
    .btn-women:hover { border-color: #ec4899; }
    .btn-child {
        background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(22,163,74,0.1));
        border: 2px solid rgba(34,197,94,0.4);
        color: #86efac;
    }
    .btn-child:hover { border-color: #22c55e; }
    .btn-mental {
        background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(124,58,237,0.1));
        border: 2px solid rgba(139,92,246,0.4);
        color: #c4b5fd;
    }
    .btn-mental:hover { border-color: #8b5cf6; }

    /* City Info Card */
    .city-card {
        background: rgba(30,41,59,0.5);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .city-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .city-state { color: #a78bfa; font-size: 0.9rem; font-weight: 500; }
    .city-info { color: #94a3b8; font-size: 0.9rem; margin-top: 1rem; line-height: 1.8; }
    .city-info strong { color: #e2e8f0; }

    /* Nearby hospital */
    .nearby-card {
        background: rgba(30,41,59,0.3);
        border: 1px solid rgba(99,102,241,0.08);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
    }
    .nearby-name { color: #e2e8f0; font-weight: 600; }
    .nearby-phone { color: #a78bfa; font-size: 0.9rem; }
    
    .stButton > button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; font-weight: 700 !important;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 30px rgba(239,68,68,0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown(f"""
<div class="sos-header">
    <div class="sos-icon">🚨</div>
    <div class="sos-title">{t('sos_title')}</div>
    <div class="sos-subtitle">{t('sos_subtitle')}</div>
</div>
""", unsafe_allow_html=True)

# === SOS BUTTONS ===
st.markdown(f"""
<div class="sos-grid">
    <a href="tel:108" class="sos-btn btn-ambulance">
        <div class="sos-btn-icon">🚑</div>
        <div class="sos-btn-title">{t('call_ambulance')}</div>
        <div class="sos-btn-num">108</div>
        <div class="sos-btn-sub">National Ambulance Service</div>
    </a>
    <a href="tel:100" class="sos-btn btn-police">
        <div class="sos-btn-icon">👮</div>
        <div class="sos-btn-title">{t('call_police')}</div>
        <div class="sos-btn-num">100</div>
        <div class="sos-btn-sub">Police Emergency</div>
    </a>
    <a href="tel:101" class="sos-btn btn-fire">
        <div class="sos-btn-icon">🔥</div>
        <div class="sos-btn-title">{t('call_fire')}</div>
        <div class="sos-btn-num">101</div>
        <div class="sos-btn-sub">Fire Emergency</div>
    </a>
    <a href="tel:181" class="sos-btn btn-women">
        <div class="sos-btn-icon">👩</div>
        <div class="sos-btn-title">{t('call_women')}</div>
        <div class="sos-btn-num">181</div>
        <div class="sos-btn-sub">Women Helpline (24x7)</div>
    </a>
    <a href="tel:1098" class="sos-btn btn-child">
        <div class="sos-btn-icon">👶</div>
        <div class="sos-btn-title">{t('call_child')}</div>
        <div class="sos-btn-num">1098</div>
        <div class="sos-btn-sub">Child Emergency</div>
    </a>
    <a href="tel:08046110007" class="sos-btn btn-mental">
        <div class="sos-btn-icon">🧠</div>
        <div class="sos-btn-title">{t('call_mental')}</div>
        <div class="sos-btn-num">iCall</div>
        <div class="sos-btn-sub">08046110007</div>
    </a>
</div>
""", unsafe_allow_html=True)

# === CITY-SPECIFIC EMERGENCY INFO ===
st.markdown("---")
st.markdown("### 📍 City-Specific Emergency Information")

df = load_emergency_contacts()
if df is not None:
    col1, col2 = st.columns(2)
    with col1:
        states = get_states()
        sel_state = st.selectbox("Select State", ["-- All --"] + states, key="sos_state")
    with col2:
        if sel_state != "-- All --":
            cities = get_cities_by_state(sel_state)
        else:
            cities = sorted(df['City'].tolist())
        sel_city = st.selectbox(t('select_city'), ["-- Select --"] + cities, key="sos_city")

    if sel_city != "-- Select --":
        info = get_emergency_contact(sel_city)
        if info:
            row = df[df['City'].str.lower() == sel_city.lower()].iloc[0]
            st.markdown(f"""
            <div class="city-card">
                <div class="city-name">📍 {row['City']}</div>
                <div class="city-state">{row['State']}</div>
                <div class="city-info">
                    🏥 <strong>Hospital:</strong> {row['Hospital_Name']} ({row.get('Type', 'Government')})<br>
                    📞 <strong>Emergency Phone:</strong> {row['Emergency_Phone']}<br>
                    🚑 <strong>Ambulance:</strong> {row.get('Ambulance', '108')}<br>
                    👮 <strong>Police:</strong> {row.get('Police', '100')}<br>
                    🔥 <strong>Fire:</strong> {row.get('Fire', '101')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Nearby hospitals
            nearby = get_nearby_hospitals(sel_city, 5)
            if nearby:
                st.markdown("#### 🏥 Nearby Government Hospitals")
                for h in nearby:
                    st.markdown(f"""
                    <div class="nearby-card">
                        <span class="nearby-name">{h['Hospital_Name']}</span> — {h['City']}<br>
                        <span class="nearby-phone">📞 {h['Emergency_Phone']}</span>
                    </div>
                    """, unsafe_allow_html=True)


# === STATE-WISE FULL DIRECTORY ===
st.markdown("---")
st.markdown("### 📋 Complete Emergency Directory")

if df is not None:
    for state in sorted(df['State'].unique()):
        state_df = df[df['State'] == state]
        with st.expander(f"🏛️ {state} — {len(state_df)} cities"):
            st.dataframe(
                state_df[['City', 'Hospital_Name', 'Emergency_Phone']].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )


# === FOOTER ===
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; padding:1rem;">
    <div style="color:#ef4444; font-size:1.2rem; font-weight:700; margin-bottom:0.5rem;">
        🚨 In any emergency, DO NOT HESITATE — Call 108 immediately 🚨
    </div>
    <div style="color:#475569; font-size:0.8rem;">
        {t('disclaimer')}
    </div>
</div>
""", unsafe_allow_html=True)
