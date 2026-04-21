"""
Page 2: Interactive Symptom Checker with Triage Classification
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME, TRIAGE_LEVELS
from modules.symptom_analyzer import BODY_REGIONS, classify_triage, build_symptom_prompt
from modules.llm_engine import generate_response, is_api_configured
from modules.health_data import load_diseases_db, search_diseases

# --- Page Config ---
st.set_page_config(page_title=f"Symptom Checker — {APP_NAME}", page_icon="🩺", layout="wide")

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
    
    /* Step cards */
    .step-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .step-number {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        text-align: center;
        line-height: 32px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 10px;
    }
    .step-title { color: #e2e8f0; font-size: 1.1rem; font-weight: 600; display: inline; }
    
    /* Triage Result */
    .triage-result {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
    }
    .triage-level {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .triage-action { font-size: 1.1rem; font-weight: 500; margin-top: 0.75rem; }
    .triage-confidence { font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.7; }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    .stMultiSelect > div { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="page-header">
    <div class="page-title">🩺 Interactive Symptom Checker</div>
    <div class="page-subtitle">Select your symptoms step by step — get AI-powered triage assessment</div>
</div>
""", unsafe_allow_html=True)

# --- Step 1: Body Region Selection ---
st.markdown("""
<div class="step-card">
    <span class="step-number">1</span>
    <span class="step-title">Select Body Region</span>
</div>
""", unsafe_allow_html=True)

region_options = list(BODY_REGIONS.keys())
selected_region = st.selectbox(
    "Which area of your body is affected?",
    options=["-- Select a region --"] + region_options,
    key="body_region"
)

# --- Step 2: Symptom Selection ---
selected_symptoms = []
if selected_region and selected_region != "-- Select a region --":
    st.markdown("""
    <div class="step-card">
        <span class="step-number">2</span>
        <span class="step-title">Select Your Symptoms</span>
    </div>
    """, unsafe_allow_html=True)

    symptoms_list = BODY_REGIONS[selected_region]["symptoms"]
    selected_symptoms = st.multiselect(
        "Select all symptoms you are experiencing:",
        options=symptoms_list,
        key="symptoms"
    )

# --- Step 3: Severity & Duration ---
if selected_symptoms:
    st.markdown("""
    <div class="step-card">
        <span class="step-number">3</span>
        <span class="step-title">Rate Severity & Duration</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        severity = st.select_slider(
            "How severe are your symptoms?",
            options=["Mild (1-3)", "Moderate (4-6)", "Severe (7-8)", "Very Severe (9-10)"],
            key="severity"
        )
    with col2:
        duration = st.selectbox(
            "How long have you had these symptoms?",
            options=[
                "Just started (< 24 hours)", "1-3 days", "4-7 days",
                "1-2 weeks", "More than 2 weeks", "Chronic (months/years)"
            ],
            key="duration"
        )

    # --- Step 4: Patient Info ---
    st.markdown("""
    <div class="step-card">
        <span class="step-number">4</span>
        <span class="step-title">Patient Information</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=30, key="age")
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender")

    additional = st.text_area(
        "Any additional information? (other conditions, medications, etc.)",
        placeholder="E.g., I have diabetes, taking metformin...",
        key="additional"
    )

    # --- Analyze Button ---
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Analyze My Symptoms", use_container_width=True, type="primary"):

        # --- Triage Classification ---
        triage_level, confidence = classify_triage(selected_symptoms, severity, duration)
        triage_info = TRIAGE_LEVELS[triage_level]

        # Color mapping for triage
        bg_colors = {
            "emergency": "rgba(239, 68, 68, 0.12)",
            "urgent": "rgba(237, 137, 54, 0.12)",
            "moderate": "rgba(236, 201, 75, 0.12)",
            "mild": "rgba(72, 187, 120, 0.12)"
        }
        border_colors = {
            "emergency": "rgba(239, 68, 68, 0.3)",
            "urgent": "rgba(237, 137, 54, 0.3)",
            "moderate": "rgba(236, 201, 75, 0.3)",
            "mild": "rgba(72, 187, 120, 0.3)"
        }

        st.markdown(f"""
        <div class="triage-result" style="
            background: {bg_colors[triage_level]};
            border: 2px solid {border_colors[triage_level]};
        ">
            <div class="triage-level" style="color: {triage_info['color']};">
                {triage_info['label']}
            </div>
            <div class="triage-action" style="color: {triage_info['color']};">
                {triage_info['action']}
            </div>
            <div class="triage-confidence" style="color: {triage_info['color']};">
                Assessment Confidence: {confidence:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        if triage_level == "emergency":
            st.error("🚨 **CALL 108 NOW** — National Ambulance Service. Go to the nearest emergency room immediately.")

        # --- Disease Database Lookup ---
        diseases_db = load_diseases_db()
        if diseases_db:
            st.markdown("---")
            st.markdown("### 📚 Database Matches")
            all_matches = []
            for symptom in selected_symptoms:
                matches = search_diseases(symptom, diseases_db)
                for m in matches:
                    if m['name'] not in [x['name'] for x in all_matches]:
                        all_matches.append(m)

            if all_matches:
                for match in all_matches[:5]:
                    with st.expander(f"📋 {match['name']} — Severity: {match.get('severity', 'N/A').title()}"):
                        st.markdown(f"**Symptoms:** {', '.join(match.get('symptoms', []))}")
                        st.markdown(f"**Causes:** {match.get('causes', 'N/A')}")
                        st.markdown(f"**Home Remedies:** {', '.join(match.get('home_remedies', []))}")
                        st.markdown(f"**⚠️ See Doctor:** {match.get('when_to_see_doctor', 'N/A')}")
                        st.markdown(f"**Prevention:** {', '.join(match.get('prevention', []))}")
            else:
                st.info("No exact database matches found. See AI analysis below.")

        # --- AI Analysis ---
        if is_api_configured():
            st.markdown("---")
            st.markdown("### 🤖 AI-Powered Analysis")
            with st.spinner("🔍 Running comprehensive symptom analysis..."):
                prompt = build_symptom_prompt(
                    selected_symptoms, severity, duration, age, gender, additional
                )
                ai_response = generate_response(prompt)
            st.markdown(ai_response)
        else:
            st.warning("⚠️ Configure your API key for AI-powered analysis.")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem;">
            ⚠️ This assessment is for informational purposes only and does not constitute medical advice.<br>
            Always consult a qualified healthcare professional for proper diagnosis and treatment.
        </div>
        """, unsafe_allow_html=True)
