"""
Page 3: India Health Dashboard — Statistics, Seasonal Alerts, and Disease Tracking
"""
import streamlit as st
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME
from modules.health_data import load_health_tips, load_diseases_db

# --- Page Config ---
st.set_page_config(page_title=f"Health Dashboard — {APP_NAME}", page_icon="📊", layout="wide")

# --- Premium CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0f1c 0%, #111827 50%, #0d1321 100%); }
    #MainMenu, header, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    
    .page-header {
        text-align: center;
        padding: 1rem 0 2rem;
    }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-subtitle { color: #64748b; font-size: 0.95rem; margin-top: 6px; }

    /* Dashboard Cards */
    .dash-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s;
    }
    .dash-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    .dash-metric {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .dash-label { color: #94a3b8; font-size: 0.85rem; font-weight: 500; margin-top: 4px; }
    
    /* Season Card */
    .season-card {
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .season-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }
    .season-alert {
        padding: 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Disease Card */
    .disease-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(99, 102, 241, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s;
    }
    .disease-card:hover {
        border-color: rgba(99, 102, 241, 0.25);
    }
    .disease-name { color: #e2e8f0; font-weight: 600; font-size: 1rem; }
    .disease-severity {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="page-header">
    <div class="page-title">📊 India Health Dashboard</div>
    <div class="page-subtitle">Real-time health intelligence, disease tracking, and seasonal alerts</div>
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
tips_data = load_health_tips()
diseases_db = load_diseases_db()

# --- Key Statistics ---
if tips_data and 'india_health_stats' in tips_data:
    stats = tips_data['india_health_stats']

    st.markdown("### 🇮🇳 India Health Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="dash-card">
            <div class="dash-metric">{stats.get('life_expectancy', 'N/A')}</div>
            <div class="dash-label">Life Expectancy</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="dash-card">
            <div class="dash-metric">{stats.get('infant_mortality', 'N/A')}</div>
            <div class="dash-label">Infant Mortality (per 1000)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        infra = stats.get('healthcare_infrastructure', {})
        st.markdown(f"""
        <div class="dash-card">
            <div class="dash-metric">{infra.get('Doctors per 1000 people', 'N/A')}</div>
            <div class="dash-label">Doctors per 1000 People</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="dash-card">
            <div class="dash-metric">{infra.get('Government Hospitals', 'N/A')}</div>
            <div class="dash-label">Government Hospitals</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Top Causes of Death ---
    st.markdown("---")
    st.markdown("### ⚠️ Leading Causes of Death in India")

    causes = stats.get('top_causes_of_death', [])
    for i, cause in enumerate(causes):
        parts = cause.split("(")
        name = parts[0].strip()
        pct = parts[1].replace(")", "").strip() if len(parts) > 1 else "N/A"
        pct_num = float(pct.replace("%", "")) if "%" in pct else 0

        st.markdown(f"**{i+1}. {name}**")
        st.progress(min(pct_num / 30, 1.0))
        st.caption(f"{pct} of all deaths")

    # --- Disease Burden ---
    st.markdown("---")
    st.markdown("### 📈 Disease Burden — Key Numbers")

    burden = stats.get('disease_burden', {})
    cols = st.columns(len(burden))
    for i, (disease, count) in enumerate(burden.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="dash-card" style="text-align: center;">
                <div style="color: #a78bfa; font-weight: 700; font-size: 1.1rem;">{disease}</div>
                <div style="color: #e2e8f0; font-size: 1.3rem; font-weight: 600; margin-top: 8px;">{count}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- Healthcare Infrastructure ---
    st.markdown("---")
    st.markdown("### 🏥 Healthcare Infrastructure")

    infra_cols = st.columns(len(infra))
    for i, (key, val) in enumerate(infra.items()):
        with infra_cols[i]:
            st.metric(key, val)

# --- Seasonal Health Alerts ---
st.markdown("---")
st.markdown("### 🌤️ Seasonal Health Alerts")

if tips_data and 'seasonal_alerts' in tips_data:
    alerts = tips_data['seasonal_alerts']

    # Determine current season
    month = datetime.datetime.now().month
    if 3 <= month <= 6:
        current_season = "Summer (March-June)"
        season_color = "rgba(251, 191, 36, 0.1)"
        season_border = "rgba(251, 191, 36, 0.25)"
        text_color = "#fbbf24"
    elif 7 <= month <= 9:
        current_season = "Monsoon (July-September)"
        season_color = "rgba(59, 130, 246, 0.1)"
        season_border = "rgba(59, 130, 246, 0.25)"
        text_color = "#60a5fa"
    else:
        current_season = "Winter (October-February)"
        season_color = "rgba(156, 163, 175, 0.1)"
        season_border = "rgba(156, 163, 175, 0.25)"
        text_color = "#9ca3af"

    for season_name, season_alerts in alerts.items():
        is_current = season_name == current_season
        bg = season_color if is_current else "rgba(30, 41, 59, 0.3)"
        border = season_border if is_current else "rgba(99, 102, 241, 0.08)"
        color = text_color if is_current else "#94a3b8"

        badge = ' <span style="background: rgba(99, 102, 241, 0.3); color: #a78bfa; padding: 2px 10px; border-radius: 10px; font-size: 0.75rem; font-weight: 600;">CURRENT</span>' if is_current else ""

        alerts_html = "".join([f'<div class="season-alert" style="color: {color};">{a}</div>' for a in season_alerts])

        st.markdown(f"""
        <div class="season-card" style="background: {bg}; border: 1px solid {border};">
            <div class="season-title" style="color: {color};">{season_name}{badge}</div>
            {alerts_html}
        </div>
        """, unsafe_allow_html=True)

# --- Disease Database Explorer ---
st.markdown("---")
st.markdown("### 🔍 Disease Database Explorer")

if diseases_db:
    search = st.text_input("Search diseases by name or symptom...", placeholder="e.g., dengue, headache, fever")

    if search:
        from modules.health_data import search_diseases
        results = search_diseases(search, diseases_db)
        if results:
            for r in results[:8]:
                severity_colors = {
                    "mild": ("rgba(72, 187, 120, 0.15)", "#48bb78"),
                    "moderate": ("rgba(236, 201, 75, 0.15)", "#ecc94b"),
                    "urgent": ("rgba(237, 137, 54, 0.15)", "#ed8936"),
                    "emergency": ("rgba(239, 68, 68, 0.15)", "#e53e3e"),
                }
                sev = r.get("severity", "mild")
                bg, color = severity_colors.get(sev, ("rgba(99, 102, 241, 0.1)", "#a78bfa"))

                with st.expander(f"📋 {r['name']}"):
                    st.markdown(f"**Severity:** :{['green', 'orange', 'red', 'red'][['mild', 'moderate', 'urgent', 'emergency'].index(sev)]}[{sev.upper()}]")
                    st.markdown(f"**Symptoms:** {', '.join(r.get('symptoms', []))}")
                    st.markdown(f"**Causes:** {r.get('causes', 'N/A')}")
                    st.markdown(f"**Risk Factors:** {', '.join(r.get('risk_factors', []))}")
                    st.markdown(f"**Home Remedies:** {', '.join(r.get('home_remedies', []))}")
                    st.markdown(f"**When to See Doctor:** {r.get('when_to_see_doctor', 'N/A')}")
                    st.markdown(f"**Prevention:** {', '.join(r.get('prevention', []))}")
        else:
            st.info("No diseases found matching your search.")
    else:
        st.caption(f"📚 {len(diseases_db)} diseases in database — start typing to search")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #475569; font-size: 0.8rem; padding: 1rem;">
    Data sources: WHO, National Health Portal India, IDSP, Census 2024<br>
    ⚠️ Statistics are approximate and for informational purposes only
</div>
""", unsafe_allow_html=True)
