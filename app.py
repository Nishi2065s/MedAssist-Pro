"""
MedAssist Pro v3.0 — Ultra Industry-Level AI Healthcare Platform
Main Landing Page with Multilingual Support & Premium UI
"""
import streamlit as st
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import (
    APP_NAME, APP_VERSION, APP_TAGLINE, APP_ICON,
    LANGUAGES, COVERED_STATES, get_ui_string
)
from modules.health_data import load_health_tips
from modules.llm_engine import is_api_configured
from modules.emergency_handler import load_emergency_contacts

# --- Page Configuration ---
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Init ---
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
if 'user_state' not in st.session_state:
    st.session_state.user_state = None
if 'user_city' not in st.session_state:
    st.session_state.user_city = None

# --- GLOBAL PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, #030712 0%, #0f172a 40%, #1e1b4b 70%, #0f172a 100%);
    }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 50%, #1e1b4b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.12);
    }

    /* ===== HERO ===== */
    .hero-wrap {
        text-align: center;
        padding: 1.5rem 1rem 0.5rem;
        animation: fadeUp 0.8s ease-out;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.18));
        border: 1px solid rgba(139,92,246,0.3);
        color: #c4b5fd;
        padding: 6px 18px;
        border-radius: 24px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .hero-badge .live-dot {
        display: inline-block;
        width: 8px; height: 8px;
        background: #22c55e;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.5s infinite;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 25%, #c084fc 50%, #e879f9 75%, #818cf8 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite;
        letter-spacing: -2px;
        line-height: 1.1;
    }
    @keyframes shimmer {
        to { background-position: 200% center; }
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0.75rem auto 0;
        max-width: 600px;
        line-height: 1.6;
    }
    .hero-states {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1.25rem;
    }
    .state-tag {
        background: rgba(30,41,59,0.6);
        border: 1px solid rgba(99,102,241,0.15);
        color: #a78bfa;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ===== STAT CARDS ===== */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
        margin: 2rem 0;
    }
    @media (max-width: 768px) {
        .stats-row { grid-template-columns: repeat(2, 1fr); }
        .hero-title { font-size: 2.4rem; }
        .feature-grid { grid-template-columns: 1fr !important; }
    }
    .stat-box {
        background: linear-gradient(145deg, rgba(30,41,59,0.7), rgba(15,23,42,0.85));
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    }
    .stat-box:hover {
        border-color: rgba(139,92,246,0.35);
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(99,102,241,0.12);
    }
    .stat-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-lbl { color: #64748b; font-size: 0.78rem; font-weight: 500; margin-top: 2px; }

    /* ===== FEATURE CARDS ===== */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feat-card {
        background: linear-gradient(145deg, rgba(30,41,59,0.5), rgba(15,23,42,0.75));
        border: 1px solid rgba(99,102,241,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
    }
    .feat-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a78bfa, #e879f9);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .feat-card:hover {
        border-color: rgba(139,92,246,0.3);
        transform: translateY(-8px);
        box-shadow: 0 24px 64px rgba(99,102,241,0.1);
    }
    .feat-card:hover::after { opacity: 1; }
    .feat-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .feat-title { color: #e2e8f0; font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem; }
    .feat-desc { color: #64748b; font-size: 0.82rem; line-height: 1.5; }

    /* ===== SOS BANNER ===== */
    .sos-banner {
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(220,38,38,0.08));
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .sos-icon { font-size: 3rem; animation: pulse 1.2s infinite; }
    .sos-text { flex: 1; }
    .sos-title { color: #fca5a5; font-size: 1.2rem; font-weight: 700; }
    .sos-nums {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .sos-num {
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.2);
        color: #f87171;
        padding: 4px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    /* ===== HEALTH TIP ===== */
    .tip-card {
        background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(52,211,153,0.04));
        border: 1px solid rgba(16,185,129,0.18);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
    }
    .tip-cat { color: #6ee7b7; font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
    .tip-text { color: #a7f3d0; font-size: 0.92rem; line-height: 1.6; margin-top: 4px; }

    /* ===== FOOTER ===== */
    .main-footer {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
        border-top: 1px solid rgba(99,102,241,0.08);
        margin-top: 2rem;
    }
    .footer-disc { color: #475569; font-size: 0.82rem; margin-bottom: 0.5rem; }
    .footer-copy { color: #334155; font-size: 0.72rem; }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        box-shadow: 0 8px 30px rgba(99,102,241,0.3) !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)


# === SIDEBAR ===
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:0.75rem 0;">
        <div style="font-size:2.8rem;">🏥</div>
        <h2 style="margin:0.3rem 0 0; color:#e2e8f0; font-family:'Space Grotesk',sans-serif; font-size:1.4rem;">MedAssist Pro</h2>
        <p style="color:#6366f1; font-size:0.7rem; font-weight:600; letter-spacing:1px;">INDUSTRY EDITION v3.0</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Language Selector
    st.markdown("### 🌐 Language / மொழி / భాష")
    lang_options = {v["native"]: k for k, v in LANGUAGES.items()}
    selected_lang_name = st.selectbox(
        "Choose Language",
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(st.session_state.lang) if st.session_state.lang in lang_options.values() else 0,
        key="lang_selector"
    )
    st.session_state.lang = lang_options[selected_lang_name]
    lang = st.session_state.lang

    st.markdown("---")

    # Location
    st.markdown(f"### 📍 {get_ui_string('select_state', lang)}")
    df = load_emergency_contacts()
    if df is not None:
        states = sorted(df['State'].unique().tolist())
        sel_state = st.selectbox("State", ["-- All States --"] + states, key="state_sel")
        if sel_state != "-- All States --":
            st.session_state.user_state = sel_state
            cities = sorted(df[df['State'] == sel_state]['City'].tolist())
            sel_city = st.selectbox(get_ui_string("select_city", lang), ["-- Select --"] + cities, key="city_sel")
            if sel_city != "-- Select --":
                st.session_state.user_city = sel_city

    st.markdown("---")

    # System Status
    st.markdown("### ⚡ System Status")
    if is_api_configured():
        st.success("✅ AI Engine: Online")
    else:
        st.error("❌ AI Engine: No API Key")

    if df is not None:
        st.info(f"📍 {len(df)} cities loaded across {len(df['State'].unique())} states")

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:0.5rem 0;">
        <p style="color:#334155; font-size:0.7rem;">Built with ❤️ for India</p>
        <p style="color:#1e293b; font-size:0.65rem;">Powered by Gemini AI + Groq</p>
    </div>
    """, unsafe_allow_html=True)


# === HERO SECTION ===
t = get_ui_string
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-badge"><span class="live-dot"></span>AI-POWERED HEALTHCARE PLATFORM</div>
    <div class="hero-title">{t('app_name', lang)}</div>
    <div class="hero-sub">{t('tagline', lang)}</div>
    <div class="hero-states">
        <span class="state-tag">🏛️ Tamil Nadu</span>
        <span class="state-tag">🏛️ Andhra Pradesh</span>
        <span class="state-tag">🏛️ Karnataka</span>
        <span class="state-tag">🏛️ Kerala</span>
        <span class="state-tag">🏛️ Telangana</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === STATS ROW ===
total_cities = len(df) if df is not None else 150
st.markdown(f"""
<div class="stats-row">
    <div class="stat-box">
        <div class="stat-num">{total_cities}+</div>
        <div class="stat-lbl">Cities Covered</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">5</div>
        <div class="stat-lbl">States</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">6</div>
        <div class="stat-lbl">Languages</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">20+</div>
        <div class="stat-lbl">Diseases DB</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">24/7</div>
        <div class="stat-lbl">Always On</div>
    </div>
</div>
""", unsafe_allow_html=True)

# === FEATURE GRID ===
st.markdown(f"""
<div class="feature-grid">
    <div class="feat-card">
        <div class="feat-icon">💬</div>
        <div class="feat-title">{t('nav_chat', lang)}</div>
        <div class="feat-desc">Multilingual AI — Tamil, Telugu, Kannada, Malayalam, Hindi & English</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🩺</div>
        <div class="feat-title">{t('nav_symptoms', lang) if lang != 'en' else 'Symptom Checker'}</div>
        <div class="feat-desc">Interactive body-map symptom assessment with AI triage</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🚨</div>
        <div class="feat-title">{t('nav_sos', lang)}</div>
        <div class="feat-desc">One-tap SOS alerts — ambulance, police, fire, helplines</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🚑</div>
        <div class="feat-title">{t('nav_ambulance', lang)}</div>
        <div class="feat-desc">Real-time ambulance tracking & nearest hospital finder</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📊</div>
        <div class="feat-title">{t('nav_dashboard', lang) if lang != 'en' else 'Health Dashboard'}</div>
        <div class="feat-desc">India health statistics, seasonal alerts, disease tracking</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">💊</div>
        <div class="feat-title">Medicine Lookup</div>
        <div class="feat-desc">Drug info, generic alternatives, Indian brand names & prices</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📋</div>
        <div class="feat-title">Health Profile</div>
        <div class="feat-desc">BMI calculator, screening checklist, wellness score</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📞</div>
        <div class="feat-title">{t('emergency_contacts', lang)}</div>
        <div class="feat-desc">{total_cities}+ cities with hospital, police & fire numbers</div>
    </div>
</div>
""", unsafe_allow_html=True)


# === SOS EMERGENCY BANNER ===
st.markdown(f"""
<div class="sos-banner">
    <div class="sos-icon">🚨</div>
    <div class="sos-text">
        <div class="sos-title">{t('sos_title', lang)} — Immediate Help</div>
        <div class="sos-nums">
            <span class="sos-num">🚑 108 Ambulance</span>
            <span class="sos-num">👮 100 Police</span>
            <span class="sos-num">🔥 101 Fire</span>
            <span class="sos-num">👩 181 Women</span>
            <span class="sos-num">👶 1098 Child</span>
            <span class="sos-num">🧠 08046110007 Mental Health</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# === DAILY HEALTH TIP ===
tips_data = load_health_tips()
if tips_data and 'daily_tips' in tips_data:
    tip = random.choice(tips_data['daily_tips'])
    st.markdown(f"""
    <div class="tip-card">
        <div class="tip-cat">{tip.get('icon', '💡')} Daily Health Tip — {tip.get('category', 'Wellness')}</div>
        <div class="tip-text">{tip.get('tip', '')}</div>
    </div>
    """, unsafe_allow_html=True)


# === COVERED STATES INFO ===
if df is not None:
    st.markdown("---")
    st.markdown("### 🗺️ Coverage Map")
    state_counts = df.groupby('State').size().reset_index(name='Cities')
    cols = st.columns(len(state_counts))
    for i, (_, row) in enumerate(state_counts.iterrows()):
        with cols[i]:
            st.metric(row['State'], f"{row['Cities']} cities")


# === FOOTER ===
st.markdown(f"""
<div class="main-footer">
    <div class="footer-disc">{t('disclaimer', lang)}</div>
    <div class="footer-copy">{APP_NAME} v{APP_VERSION} • © 2026 • Made with ❤️ in India • Industry Edition</div>
</div>
""", unsafe_allow_html=True)