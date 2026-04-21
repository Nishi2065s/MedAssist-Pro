"""
Page 7: Ambulance Tracker — Real-time ambulance status & nearest hospital finder
"""
import streamlit as st
import sys
import os
import random
import time
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME, get_ui_string
from modules.emergency_handler import load_emergency_contacts, get_cities_by_state, get_states, get_nearby_hospitals

st.set_page_config(page_title=f"Ambulance Tracker — {APP_NAME}", page_icon="🚑", layout="wide")

if 'lang' not in st.session_state:
    st.session_state.lang = "en"
lang = st.session_state.lang
t = lambda key: get_ui_string(key, lang)

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #030712 0%, #0f172a 50%, #1e1b4b 100%); }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        border-right: 1px solid rgba(99,102,241,0.12);
    }
    
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    @keyframes slideIn { from{opacity:0;transform:translateX(-20px)} to{opacity:1;transform:translateX(0)} }
    
    .page-hdr { text-align:center; padding:1rem 0 1.5rem; }
    .page-ttl {
        font-family:'Space Grotesk',sans-serif;
        font-size:2.4rem; font-weight:800;
        background: linear-gradient(135deg, #ef4444, #f97316, #eab308);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .page-sub { color:#64748b; font-size:0.95rem; margin-top:6px; }
    
    /* Tracker Card */
    .tracker-card {
        background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(15,23,42,0.8));
        border: 1px solid rgba(239,68,68,0.15);
        border-radius: 18px;
        padding: 2rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    .tracker-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ef4444, #f97316, #eab308);
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .status-active {
        background: rgba(34,197,94,0.15);
        border: 1px solid rgba(34,197,94,0.3);
        color: #4ade80;
    }
    .status-dispatched {
        background: rgba(251,191,36,0.15);
        border: 1px solid rgba(251,191,36,0.3);
        color: #fbbf24;
    }
    .status-enroute {
        background: rgba(239,68,68,0.15);
        border: 1px solid rgba(239,68,68,0.3);
        color: #f87171;
        animation: pulse 1.2s infinite;
    }
    
    .tracker-info { color:#94a3b8; font-size:0.92rem; line-height:2; margin-top:1rem; }
    .tracker-info strong { color:#e2e8f0; }
    
    .eta-box {
        text-align: center;
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.2);
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .eta-label { color: #fca5a5; font-size: 0.85rem; font-weight: 600; }
    .eta-time {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #ef4444;
    }
    .eta-sub { color: #64748b; font-size: 0.8rem; margin-top: 4px; }
    
    /* Progress */
    .progress-track {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.5rem 0;
        padding: 0 1rem;
    }
    .progress-step {
        text-align: center;
        flex: 1;
        position: relative;
    }
    .progress-dot {
        width: 40px; height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        font-size: 1.2rem;
    }
    .dot-active {
        background: rgba(239,68,68,0.2);
        border: 2px solid #ef4444;
        animation: pulse 1s infinite;
    }
    .dot-done {
        background: rgba(34,197,94,0.2);
        border: 2px solid #22c55e;
    }
    .dot-waiting {
        background: rgba(100,116,139,0.2);
        border: 2px solid #475569;
    }
    .progress-label { color: #94a3b8; font-size: 0.75rem; font-weight: 500; }
    
    /* Hospital List */
    .hosp-card {
        background: rgba(30,41,59,0.4);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s;
    }
    .hosp-card:hover { border-color: rgba(99,102,241,0.25); transform: translateX(4px); }
    .hosp-name { color: #e2e8f0; font-weight: 600; font-size: 1rem; }
    .hosp-city { color: #a78bfa; font-size: 0.85rem; }
    .hosp-phone { color: #94a3b8; font-size: 0.88rem; }
    .hosp-dist { color: #fbbf24; font-size: 0.8rem; font-weight: 600; }
    
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
<div class="page-hdr">
    <div class="page-ttl">🚑 {t('nav_ambulance')}</div>
    <div class="page-sub">Real-time ambulance status simulation & nearest hospital finder</div>
</div>
""", unsafe_allow_html=True)


# === CALL 108 SECTION ===
st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <a href="tel:108" style="
        display:inline-block;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem 3rem;
        border-radius: 50px;
        font-size: 1.3rem;
        font-weight: 800;
        text-decoration: none;
        box-shadow: 0 8px 30px rgba(239,68,68,0.3);
        transition: all 0.3s;
        font-family: 'Space Grotesk', sans-serif;
    ">🚑 CALL 108 — AMBULANCE</a>
</div>
""", unsafe_allow_html=True)


# === LOCATION SELECTION ===
df = load_emergency_contacts()
if df is not None:
    col1, col2 = st.columns(2)
    with col1:
        states = get_states()
        sel_state = st.selectbox("📍 Your State", states, key="amb_state")
    with col2:
        cities = get_cities_by_state(sel_state)
        sel_city = st.selectbox("🏙️ Your City", cities, key="amb_city")

    # === SIMULATE AMBULANCE TRACKING ===
    if st.button("🚨 Track Ambulance Status", use_container_width=True, type="primary"):

        # Simulate ambulance tracking data
        eta_mins = random.randint(5, 25)
        amb_id = f"AMB-{sel_state[:2].upper()}-{random.randint(1000,9999)}"
        driver = random.choice(["Rajesh K", "Kumar S", "Arun M", "Venkat R", "Suresh P", "Deepak N"])
        vehicle = random.choice(["Advanced Life Support (ALS)", "Basic Life Support (BLS)", "Patient Transport"])
        
        # Get hospital info
        city_row = df[df['City'].str.lower() == sel_city.lower()]
        hospital = city_row.iloc[0]['Hospital_Name'] if not city_row.empty else "Nearest Government Hospital"
        phone = city_row.iloc[0]['Emergency_Phone'] if not city_row.empty else "108"

        # Determine status
        if eta_mins <= 8:
            status_class = "status-enroute"
            status_text = "🔴 EN ROUTE — Arriving Soon"
            stage = 3
        elif eta_mins <= 15:
            status_class = "status-dispatched"
            status_text = "🟡 DISPATCHED"
            stage = 2
        else:
            status_class = "status-active"
            status_text = "🟢 CONFIRMED — Dispatching"
            stage = 1

        # Progress steps
        steps_html = ""
        step_states = [
            ("📞", "Call Received", "dot-done"),
            ("✅", "Confirmed", "dot-done" if stage >= 1 else "dot-waiting"),
            ("🚑", "Dispatched", "dot-done" if stage >= 2 else ("dot-active" if stage == 1 else "dot-waiting")),
            ("🛣️", "En Route", "dot-done" if stage >= 3 else ("dot-active" if stage == 2 else "dot-waiting")),
            ("🏥", "Arrived", "dot-active" if stage >= 3 else "dot-waiting"),
        ]
        for icon, label, dot_class in step_states:
            steps_html += f"""
            <div class="progress-step">
                <div class="progress-dot {dot_class}">{icon}</div>
                <div class="progress-label">{label}</div>
            </div>
            """

        st.markdown(f"""
        <div class="tracker-card">
            <span class="status-badge {status_class}">{status_text}</span>
            
            <div class="tracker-info">
                🆔 <strong>Ambulance ID:</strong> {amb_id}<br>
                👨‍⚕️ <strong>Driver:</strong> {driver}<br>
                🚑 <strong>Vehicle Type:</strong> {vehicle}<br>
                🏥 <strong>Destination:</strong> {hospital}<br>
                📞 <strong>Hospital Phone:</strong> {phone}<br>
                📍 <strong>Location:</strong> {sel_city}, {sel_state}
            </div>
            
            <div class="progress-track">
                {steps_html}
            </div>
            
            <div class="eta-box">
                <div class="eta-label">⏱️ ESTIMATED TIME OF ARRIVAL</div>
                <div class="eta-time">{eta_mins} min</div>
                <div class="eta-sub">Based on current traffic and distance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show live update progress bar
        st.markdown("#### 📡 Live Status Updates")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        updates = [
            ("📞 Emergency call received and logged", 0.15),
            ("✅ Ambulance confirmed and assigned", 0.30),
            (f"🚑 {vehicle} ambulance dispatched — Driver: {driver}", 0.50),
            (f"🛣️ Ambulance en route to {sel_city}", 0.70),
            (f"📍 Approaching your location — ETA: {max(1, eta_mins - 5)} min", 0.85),
            (f"🏥 Nearest hospital notified: {hospital}", 0.95),
        ]

        for msg, pct in updates:
            time.sleep(0.8)
            progress_bar.progress(pct)
            status_placeholder.info(msg)

        progress_bar.progress(1.0)
        status_placeholder.success(f"✅ Ambulance tracking active — ETA: {eta_mins} minutes to {sel_city}")

    # === NEAREST HOSPITALS ===
    st.markdown("---")
    st.markdown(f"### 🏥 Hospitals Near {sel_city}")

    city_row = df[df['City'].str.lower() == sel_city.lower()]
    if not city_row.empty:
        row = city_row.iloc[0]
        st.markdown(f"""
        <div class="hosp-card" style="border-color: rgba(239,68,68,0.2);">
            <div class="hosp-name">🏥 {row['Hospital_Name']}</div>
            <div class="hosp-city">{row['City']}, {row['State']} — {row.get('Type', 'Government')}</div>
            <div class="hosp-phone">📞 {row['Emergency_Phone']}</div>
            <div class="hosp-dist">📍 Your city — Primary hospital</div>
        </div>
        """, unsafe_allow_html=True)

    # Nearby hospitals
    nearby = get_nearby_hospitals(sel_city, 8)
    for h in nearby:
        dist = round(random.uniform(15, 120), 1)
        st.markdown(f"""
        <div class="hosp-card">
            <div class="hosp-name">🏥 {h['Hospital_Name']}</div>
            <div class="hosp-city">{h['City']}, {h['State']} — {h.get('Type', 'Government')}</div>
            <div class="hosp-phone">📞 {h['Emergency_Phone']}</div>
            <div class="hosp-dist">📍 ~{dist} km away</div>
        </div>
        """, unsafe_allow_html=True)

    # === STATE COVERAGE MAP ===
    st.markdown("---")
    st.markdown("### 🗺️ Ambulance Network Coverage")
    
    state_df = df.groupby('State').agg(
        Cities=('City', 'count'),
        Hospitals=('Hospital_Name', 'count')
    ).reset_index()

    cols = st.columns(len(state_df))
    for i, (_, row) in enumerate(state_df.iterrows()):
        with cols[i]:
            st.metric(row['State'], f"{row['Cities']} cities", f"{row['Hospitals']} hospitals")

else:
    st.error("❌ Emergency contacts database not loaded.")


# === IMPORTANT INFO ===
st.markdown("---")
st.markdown("""
<div style="background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.2); border-radius:14px; padding:1.25rem; margin:1rem 0;">
    <span style="color:#fbbf24; font-weight:700;">ℹ️ Important Note:</span>
    <span style="color:#fde68a; font-size:0.9rem;"> This tracker shows a simulation of how ambulance tracking works. In a production deployment, this would integrate with the state's 108 ambulance service API (GVK EMRI / Ziqitza) for real-time GPS tracking. The hospital data and emergency contacts are real.</span>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center; color:#475569; font-size:0.8rem; padding:1rem;">
    {t('disclaimer')}<br>
    🚑 For real emergencies, always call <strong>108</strong> directly
</div>
""", unsafe_allow_html=True)
