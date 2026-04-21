"""
Page 5: Health Profile — BMI Calculator, Health Screening Checklist, Wellness Score
"""
import streamlit as st
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME

# --- Page Config ---
st.set_page_config(page_title=f"Health Profile — {APP_NAME}", page_icon="📋", layout="wide")

# --- Premium CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0f1c 0%, #111827 50%, #0d1321 100%); }
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    
    .page-header { text-align: center; padding: 1rem 0 2rem; }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem; font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .page-subtitle { color: #64748b; font-size: 0.95rem; margin-top: 6px; }
    
    /* BMI Result */
    .bmi-result {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .bmi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
    }
    .bmi-category { font-size: 1.3rem; font-weight: 600; margin-top: 0.5rem; }
    .bmi-range { font-size: 0.85rem; opacity: 0.7; margin-top: 0.5rem; }
    
    /* Profile Card */
    .profile-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .profile-title { color: #e2e8f0; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.75rem; }
    
    /* Screening Item */
    .screening-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(99, 102, 241, 0.06);
    }
    .screening-icon { font-size: 1.5rem; margin-right: 12px; }
    .screening-text { flex: 1; }
    .screening-name { color: #e2e8f0; font-weight: 500; font-size: 0.95rem; }
    .screening-freq { color: #64748b; font-size: 0.8rem; }
    
    /* Wellness Score */
    .wellness-score {
        text-align: center;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    .score-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4rem;
        font-weight: 800;
    }
    .score-label { color: #94a3b8; font-size: 1rem; margin-top: 0.5rem; }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white; border: none; border-radius: 10px; font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="page-header">
    <div class="page-title">📋 Health Profile & Wellness</div>
    <div class="page-subtitle">BMI calculator, health screening checklist, and personalized wellness assessment</div>
</div>
""", unsafe_allow_html=True)

# --- Section 1: BMI Calculator ---
st.markdown("### 📐 BMI Calculator")

col1, col2, col3 = st.columns(3)
with col1:
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5, key="weight")
with col2:
    height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5, key="height")
with col3:
    age = st.number_input("Age", min_value=5, max_value=120, value=30, key="bmi_age")

gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="bmi_gender")

if st.button("📊 Calculate BMI", use_container_width=True, type="primary"):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)

    # Classify BMI
    if bmi < 18.5:
        category = "Underweight"
        color = "#60a5fa"
        bg = "rgba(96, 165, 250, 0.1)"
        border = "rgba(96, 165, 250, 0.25)"
        advice = [
            "🍚 Increase calorie intake with nutrient-rich foods",
            "🥛 Include milk, ghee, nuts, and dried fruits in diet",
            "💪 Focus on strength training exercises",
            "🍌 Eat 5-6 small meals throughout the day",
            "🧈 Add healthy fats like peanut butter, avocado, cheese"
        ]
    elif bmi < 25:
        category = "Normal Weight"
        color = "#4ade80"
        bg = "rgba(74, 222, 128, 0.1)"
        border = "rgba(74, 222, 128, 0.25)"
        advice = [
            "✅ Maintain your current healthy lifestyle",
            "🏃 Continue regular exercise (30 min/day)",
            "🥗 Eat a balanced diet with all food groups",
            "💧 Stay well hydrated (8+ glasses water)",
            "🩺 Get annual health checkups"
        ]
    elif bmi < 30:
        category = "Overweight"
        color = "#fbbf24"
        bg = "rgba(251, 191, 36, 0.1)"
        border = "rgba(251, 191, 36, 0.25)"
        advice = [
            "🏃 Increase physical activity to 45 min/day",
            "🥗 Reduce processed food and sugar intake",
            "🚰 Drink water before meals to reduce appetite",
            "🍽️ Practice portion control",
            "🧘 Consider yoga for stress-related eating"
        ]
    elif bmi < 35:
        category = "Obese (Class I)"
        color = "#f97316"
        bg = "rgba(249, 115, 22, 0.1)"
        border = "rgba(249, 115, 22, 0.25)"
        advice = [
            "🩺 Consult a doctor for a weight management plan",
            "🏃 Start with walking 20 min/day, gradually increase",
            "🥗 Follow a structured diet plan (consult dietician)",
            "📉 Aim to lose 0.5-1 kg per week (safe rate)",
            "🧪 Get blood sugar, thyroid, and cholesterol checked"
        ]
    else:
        category = "Obese (Class II+)"
        color = "#ef4444"
        bg = "rgba(239, 68, 68, 0.1)"
        border = "rgba(239, 68, 68, 0.25)"
        advice = [
            "🚨 Please consult a doctor urgently",
            "🩺 Get comprehensive blood work done",
            "📋 Medical supervision for weight loss is recommended",
            "🏥 Ask doctor about bariatric assessment if BMI > 40",
            "🧘 Address mental health aspects of eating"
        ]

    st.markdown(f"""
    <div class="bmi-result" style="background: {bg}; border: 2px solid {border};">
        <div class="bmi-value" style="color: {color};">{bmi:.1f}</div>
        <div class="bmi-category" style="color: {color};">{category}</div>
        <div class="bmi-range" style="color: {color};">
            Underweight &lt; 18.5 | Normal 18.5–24.9 | Overweight 25–29.9 | Obese ≥ 30
        </div>
    </div>
    """, unsafe_allow_html=True)

    # BMI Advice
    st.markdown("#### 💡 Personalized Recommendations")
    for a in advice:
        st.markdown(a)

    # Ideal Weight Range
    ideal_low = 18.5 * (height_m ** 2)
    ideal_high = 24.9 * (height_m ** 2)
    st.info(f"🎯 **Your ideal weight range:** {ideal_low:.1f} kg – {ideal_high:.1f} kg (for height {height_cm} cm)")

# --- Section 2: Health Screening Checklist ---
st.markdown("---")
st.markdown("### 🩺 Recommended Health Screenings (India)")

# Determine screenings based on age and gender
screenings = [
    {"name": "Blood Pressure Check", "freq": "Every 6 months", "icon": "🩸", "min_age": 18},
    {"name": "Blood Sugar (Fasting)", "freq": "Annually after 35", "icon": "🍬", "min_age": 35},
    {"name": "Complete Blood Count (CBC)", "freq": "Annually", "icon": "🧪", "min_age": 18},
    {"name": "Lipid Profile (Cholesterol)", "freq": "Every 2 years after 30", "icon": "❤️", "min_age": 30},
    {"name": "Thyroid Panel (TSH)", "freq": "Every 2-3 years", "icon": "🦋", "min_age": 25},
    {"name": "Eye Examination", "freq": "Every 2 years", "icon": "👁️", "min_age": 20},
    {"name": "Dental Checkup", "freq": "Every 6 months", "icon": "🦷", "min_age": 5},
    {"name": "Vitamin D Level", "freq": "Annually", "icon": "☀️", "min_age": 20},
    {"name": "Kidney Function Test (KFT)", "freq": "Annually after 40", "icon": "🫘", "min_age": 40},
    {"name": "Liver Function Test (LFT)", "freq": "Annually after 35", "icon": "🫁", "min_age": 35},
    {"name": "Bone Density (DEXA Scan)", "freq": "Every 2 years after 50", "icon": "🦴", "min_age": 50},
    {"name": "ECG / Heart Checkup", "freq": "Annually after 40", "icon": "💓", "min_age": 40},
]

# Gender-specific
if gender == "Female":
    screenings.extend([
        {"name": "Pap Smear / Cervical Screening", "freq": "Every 3 years (21-65)", "icon": "🎀", "min_age": 21},
        {"name": "Mammogram", "freq": "Every 2 years after 40", "icon": "🩺", "min_age": 40},
        {"name": "Hemoglobin / Anemia Check", "freq": "Every 6 months", "icon": "🩸", "min_age": 15},
    ])
elif gender == "Male":
    screenings.extend([
        {"name": "PSA Test (Prostate)", "freq": "Annually after 50", "icon": "🔬", "min_age": 50},
    ])

applicable = [s for s in screenings if age >= s["min_age"]]

for s in applicable:
    st.markdown(f"""
    <div class="screening-item">
        <span class="screening-icon">{s['icon']}</span>
        <div class="screening-text">
            <div class="screening-name">{s['name']}</div>
            <div class="screening-freq">📅 {s['freq']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Section 3: Quick Wellness Assessment ---
st.markdown("---")
st.markdown("### 🌟 Quick Wellness Assessment")
st.caption("Answer honestly to get your wellness score")

q1 = st.select_slider("🏃 How often do you exercise?", options=["Never", "Rarely", "1-2 days/week", "3-4 days/week", "Daily"], key="q1")
q2 = st.select_slider("🥗 How would you rate your diet?", options=["Very Poor", "Poor", "Average", "Good", "Excellent"], key="q2")
q3 = st.select_slider("😴 Average hours of sleep per night?", options=["< 4 hours", "4-5 hours", "6-7 hours", "7-8 hours", "8+ hours"], key="q3")
q4 = st.select_slider("💧 Glasses of water per day?", options=["1-2", "3-4", "5-6", "7-8", "8+"], key="q4")
q5 = st.select_slider("😰 How stressed are you?", options=["Extremely", "Very", "Moderately", "Slightly", "Not at all"], key="q5")
q6 = st.select_slider("🚬 Do you smoke or consume tobacco?", options=["Regularly", "Occasionally", "Rarely", "Quit", "Never"], key="q6")

if st.button("📊 Calculate Wellness Score", use_container_width=True):
    score_map_5 = {0: 0, 1: 5, 2: 10, 3: 15, 4: 20}

    exercise_map = {"Never": 0, "Rarely": 1, "1-2 days/week": 2, "3-4 days/week": 3, "Daily": 4}
    diet_map = {"Very Poor": 0, "Poor": 1, "Average": 2, "Good": 3, "Excellent": 4}
    sleep_map = {"< 4 hours": 0, "4-5 hours": 1, "6-7 hours": 2, "7-8 hours": 4, "8+ hours": 3}
    water_map = {"1-2": 0, "3-4": 1, "5-6": 2, "7-8": 4, "8+": 3}
    stress_map = {"Extremely": 0, "Very": 1, "Moderately": 2, "Slightly": 3, "Not at all": 4}
    smoke_map = {"Regularly": 0, "Occasionally": 1, "Rarely": 2, "Quit": 3, "Never": 4}

    total = sum([
        score_map_5[exercise_map[q1]],
        score_map_5[diet_map[q2]],
        score_map_5[sleep_map[q3]],
        score_map_5[water_map[q4]],
        score_map_5[stress_map[q5]],
        score_map_5[smoke_map[q6]],
    ])

    # Max possible = 120, normalize to 100
    score = min(int((total / 120) * 100), 100)

    if score >= 80:
        grade = "Excellent"
        color = "#4ade80"
        msg = "Outstanding! You're on the right track. Keep up the healthy lifestyle! 🎉"
    elif score >= 60:
        grade = "Good"
        color = "#a78bfa"
        msg = "Good job! A few improvements in exercise or diet can make it excellent. 💪"
    elif score >= 40:
        grade = "Needs Improvement"
        color = "#fbbf24"
        msg = "There's room for improvement. Focus on exercise, sleep, and hydration. 📝"
    else:
        grade = "At Risk"
        color = "#f87171"
        msg = "Your wellness needs attention. Consider consulting a healthcare professional. 🩺"

    st.markdown(f"""
    <div class="wellness-score">
        <div class="score-number" style="color: {color};">{score}/100</div>
        <div style="color: {color}; font-size: 1.3rem; font-weight: 600;">{grade}</div>
        <div class="score-label">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(score / 100)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #475569; font-size: 0.8rem; padding: 1rem;">
    ⚠️ BMI and wellness scores are approximate indicators. Individual health varies.<br>
    Always consult a healthcare professional for personalized medical advice.
</div>
""", unsafe_allow_html=True)
