"""
Symptom Analyzer — Interactive symptom checker with triage classification.
Uses a rule-based decision tree enhanced by LLM for nuanced analysis.
"""
import re
import streamlit as st


# Body regions for the interactive symptom selector
BODY_REGIONS = {
    "🧠 Head & Neurological": {
        "symptoms": [
            "Headache", "Migraine", "Dizziness", "Fainting", "Blurred vision",
            "Memory loss", "Confusion", "Seizures", "Numbness (face)", "Ear pain"
        ],
        "icon": "🧠"
    },
    "🫁 Chest & Respiratory": {
        "symptoms": [
            "Chest pain", "Shortness of breath", "Cough (dry)", "Cough (with phlegm)",
            "Wheezing", "Rapid heartbeat", "Palpitations", "Chest tightness"
        ],
        "icon": "🫁"
    },
    "🫄 Abdomen & Digestive": {
        "symptoms": [
            "Stomach pain", "Nausea", "Vomiting", "Diarrhea", "Constipation",
            "Bloating", "Acid reflux", "Blood in stool", "Loss of appetite", "Jaundice"
        ],
        "icon": "🫄"
    },
    "🦴 Musculoskeletal": {
        "symptoms": [
            "Joint pain", "Back pain", "Muscle cramps", "Swelling (joints)",
            "Stiffness", "Weakness", "Fracture concern", "Neck pain"
        ],
        "icon": "🦴"
    },
    "🩺 Skin & External": {
        "symptoms": [
            "Rash", "Itching", "Skin redness", "Boils/sores", "Fungal infection",
            "Hives", "Bruising", "Hair loss", "Wound not healing", "Skin darkening"
        ],
        "icon": "🩺"
    },
    "🤒 General / Systemic": {
        "symptoms": [
            "Fever", "Fatigue", "Weight loss (unexplained)", "Night sweats",
            "Chills", "Dehydration", "Swollen lymph nodes", "Frequent infections"
        ],
        "icon": "🤒"
    },
    "🧘 Mental Health": {
        "symptoms": [
            "Anxiety", "Depression", "Insomnia", "Panic attacks",
            "Mood swings", "Loss of interest", "Irritability", "Stress"
        ],
        "icon": "🧘"
    },
    "👁️ Eyes, Ears, Nose, Throat": {
        "symptoms": [
            "Sore throat", "Runny nose", "Nasal congestion", "Ear infection",
            "Tinnitus", "Eye redness", "Watery eyes", "Difficulty swallowing"
        ],
        "icon": "👁️"
    }
}

# Emergency symptoms that trigger immediate triage
EMERGENCY_SYMPTOMS = {
    "Chest pain", "Seizures", "Fainting", "Blood in stool",
    "Shortness of breath", "Rapid heartbeat"
}

URGENT_SYMPTOMS = {
    "Fever", "Vomiting", "Fracture concern", "Jaundice",
    "Palpitations", "Confusion", "Wound not healing", "Panic attacks"
}


def classify_triage(selected_symptoms, severity, duration):
    """
    Classify the triage level based on symptoms, severity, and duration.
    Returns: (level_key, confidence_score)
    """
    score = 0

    # Check for emergency symptoms
    emergency_count = len(set(selected_symptoms) & EMERGENCY_SYMPTOMS)
    urgent_count = len(set(selected_symptoms) & URGENT_SYMPTOMS)

    score += emergency_count * 40
    score += urgent_count * 20
    score += len(selected_symptoms) * 5

    # Severity multiplier
    severity_multipliers = {
        "Mild (1-3)": 1.0,
        "Moderate (4-6)": 1.5,
        "Severe (7-8)": 2.5,
        "Very Severe (9-10)": 4.0
    }
    score *= severity_multipliers.get(severity, 1.0)

    # Duration factor
    duration_factors = {
        "Just started (< 24 hours)": 1.0,
        "1-3 days": 1.2,
        "4-7 days": 1.5,
        "1-2 weeks": 1.8,
        "More than 2 weeks": 2.0,
        "Chronic (months/years)": 1.3
    }
    score *= duration_factors.get(duration, 1.0)

    # Classify
    if score >= 100 or emergency_count > 0:
        return "emergency", min(score / 150 * 100, 99)
    elif score >= 60 or urgent_count >= 2:
        return "urgent", min(score / 100 * 100, 95)
    elif score >= 30:
        return "moderate", min(score / 60 * 100, 90)
    else:
        return "mild", min(score / 30 * 100, 85)


def build_symptom_prompt(selected_symptoms, severity, duration, age, gender, additional_info=""):
    """Build a structured prompt for LLM-based symptom analysis."""
    symptom_list = ", ".join(selected_symptoms)
    prompt = f"""Analyze the following patient symptoms and provide a structured medical assessment:

**Patient Profile:**
- Age: {age}
- Gender: {gender}

**Reported Symptoms:** {symptom_list}
**Severity Level:** {severity}
**Duration:** {duration}
{'**Additional Notes:** ' + additional_info if additional_info else ''}

**Please provide:**
1. **Possible Conditions** (top 3, with confidence indicators)
2. **Recommended Actions** (immediate steps)
3. **Home Remedies** (if applicable)
4. **When to See a Doctor** (red flags to watch for)
5. **Preventive Measures**

Format your response professionally with markdown headers, bullet points, and emojis.
End with the standard medical disclaimer."""

    return prompt


def is_health_related(query):
    """Enhanced health query detection with NLU patterns."""
    health_keywords = [
        # English
        'symptom', 'pain', 'ache', 'fever', 'cough', 'cold', 'headache', 'nausea',
        'vomit', 'rash', 'itch', 'stomach', 'chest', 'throat', 'mouth', 'heart',
        'lung', 'liver', 'kidney', 'brain', 'medical', 'health', 'doctor', 'hospital',
        'medicine', 'treatment', 'vaccine', 'remedy', 'emergency', 'urgent', 'ambulance',
        'helpline', 'contact', 'phone number', 'insurance', 'scheme', 'yojana', 'policy',
        'pregnancy', 'diabetes', 'blood pressure', 'sugar', 'cholesterol', 'thyroid',
        'cancer', 'asthma', 'allergy', 'infection', 'wound', 'injury', 'fracture',
        'anxiety', 'depression', 'stress', 'insomnia', 'mental health', 'nutrition',
        'diet', 'exercise', 'yoga', 'bmi', 'weight', 'obesity', 'anemia', 'vitamin',
        'supplement', 'drug', 'dosage', 'side effect', 'wellness', 'fitness',
        'ayurveda', 'homeopathy', 'health care', 'diagnosis', 'test', 'x-ray', 'scan',
        # Hindi
        'बीमारी', 'दर्द', 'बुखार', 'खाँसी', 'ठंड', 'सिरदर्द', 'उल्टी', 'मतली',
        'दाने', 'खुजली', 'पेट', 'सीने', 'गले', 'मुँह', 'दिल', 'फेफड़े', 'जिगर',
        'गुर्दा', 'मस्तिष्क', 'हाथ', 'स्वास्थ्य', 'डॉक्टर', 'अस्पताल', 'दवा',
        'इलाज', 'टीका', 'उपचार', 'आपातकालीन', 'जरूरी', 'एम्बुलेंस', 'हेल्पलाइन',
        'संपर्क', 'नंबर', 'लाल', 'रंग', 'आयुष्मान', 'भारत', 'योजना', 'बीमा', 'स्कीम',
        # Tamil
        'வலி', 'காய்ச்சல்', 'மருத்துவம்', 'மருத்துவர்',
        # Telugu
        'నొప్పి', 'జ్వరం', 'వైద్యం',
    ]

    query_lower = query.lower()

    if any(keyword in query_lower for keyword in health_keywords):
        return True

    # Follow-up context check
    if 'conversation_memory' in st.session_state and st.session_state.conversation_memory:
        last = st.session_state.conversation_memory[-1].get("assistant", "").lower()
        follow_up_cues = [
            'itchy', 'painful', 'red', 'inflamed', 'how long', 'more about',
            'tell me more', 'please provide details', 'describe', 'which area',
            'how severe', 'any other symptoms'
        ]
        if any(k in last for k in follow_up_cues):
            return True

    health_patterns = [
        r'\bhow to (treat|cure|prevent|manage|heal|reduce)',
        r'\bwhat (causes|is|are the symptoms)',
        r'\bfeeling (unwell|sick|ill|dizzy|tired|weak)',
        r'\b(home|natural|ayurvedic) remed(y|ies)',
        r'\bside effects?\b',
        r'\bcan (i|you) (take|use|eat|drink)',
        r'\bis .+ (dangerous|harmful|safe|normal)',
        r'\b(should i|do i need to) (see|visit|consult) (a |the )?(doctor|hospital)',
    ]

    for pattern in health_patterns:
        if re.search(pattern, query_lower):
            return True

    return False
