"""
Centralized configuration for MedAssist Pro Healthcare Platform.
Ultra Industry-Level — South India Coverage with SOS + Ambulance Tracking
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# --- LLM Models ---
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"
WHISPER_MODEL = "whisper-large-v3"
DEFAULT_PROVIDER = "groq"  # "groq" or "gemini"

# --- Data Paths ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EMERGENCY_CONTACTS_FILE = os.path.join(DATA_DIR, "emergency_contacts.csv")
DISEASES_DB_FILE = os.path.join(DATA_DIR, "diseases_database.json")
MEDICINES_DB_FILE = os.path.join(DATA_DIR, "medicines_reference.json")
HEALTH_TIPS_FILE = os.path.join(DATA_DIR, "health_tips.json")

# --- App Metadata ---
APP_NAME = "MedAssist Pro"
APP_VERSION = "3.0.0"
APP_TAGLINE = "AI-Powered Healthcare Intelligence Platform for India"
APP_ICON = "🏥"

# --- Coverage ---
COVERED_STATES = ["Tamil Nadu", "Andhra Pradesh", "Karnataka", "Kerala", "Telangana"]

# --- LLM Configuration ---
SCHEME_CONTENT_CHAR_LIMIT = 8000
MAX_CONVERSATION_MEMORY = 20
MEMORY_WINDOW = 10

# --- Supported Languages ---
LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🏳️"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🏳️"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🏳️"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "flag": "🏳️"},
}

# --- UI Translations ---
UI_STRINGS = {
    "en": {
        "app_name": "MedAssist Pro",
        "tagline": "AI-Powered Healthcare Intelligence for India",
        "welcome": "Welcome to MedAssist Pro",
        "chat_placeholder": "Describe your symptoms or ask a health question...",
        "analyzing": "Analyzing your query...",
        "sos_title": "SOS Emergency",
        "sos_subtitle": "One-tap emergency access — help is seconds away",
        "call_ambulance": "🚑 Call Ambulance (108)",
        "call_police": "👮 Call Police (100)",
        "call_fire": "🔥 Call Fire (101)",
        "call_women": "👩 Women Helpline (181)",
        "call_child": "👶 Child Helpline (1098)",
        "call_mental": "🧠 Mental Health (08046110007)",
        "symptom_checker": "Symptom Checker",
        "health_dashboard": "Health Dashboard",
        "medicine_info": "Medicine Information",
        "health_profile": "Health Profile",
        "emergency_contacts": "Emergency Contacts",
        "select_city": "Select your city",
        "select_state": "Select your state",
        "disclaimer": "⚠️ This is general information only. Please consult a qualified doctor for proper diagnosis and treatment.",
        "nav_home": "Home",
        "nav_chat": "AI Health Chat",
        "nav_symptoms": "Symptom Checker",
        "nav_dashboard": "Health Dashboard",
        "nav_medicine": "Medicine Info",
        "nav_profile": "Health Profile",
        "nav_sos": "SOS Emergency",
        "nav_ambulance": "Ambulance Tracker",
    },
    "ta": {
        "app_name": "மெட்அசிஸ்ட் ப்ரோ",
        "tagline": "AI-சக்தி கொண்ட சுகாதார நுண்ணறிவு",
        "welcome": "மெட்அசிஸ்ட் ப்ரோவிற்கு வரவேற்கிறோம்",
        "chat_placeholder": "உங்கள் அறிகுறிகளை விவரிக்கவும்...",
        "analyzing": "பகுப்பாய்வு செய்கிறது...",
        "sos_title": "அவசர SOS",
        "sos_subtitle": "ஒரே தொடலில் அவசர அணுகல்",
        "call_ambulance": "🚑 ஆம்புலன்ஸ் (108)",
        "call_police": "👮 காவல் (100)",
        "call_fire": "🔥 தீயணைப்பு (101)",
        "call_women": "👩 பெண்கள் உதவி (181)",
        "call_child": "👶 குழந்தை உதவி (1098)",
        "call_mental": "🧠 மனநலம் (08046110007)",
        "symptom_checker": "அறிகுறி பரிசோதகர்",
        "health_dashboard": "சுகாதார டாஷ்போர்டு",
        "medicine_info": "மருந்து தகவல்",
        "health_profile": "சுகாதார சுயவிவரம்",
        "emergency_contacts": "அவசர தொடர்புகள்",
        "select_city": "உங்கள் நகரத்தைத் தேர்ந்தெடுக்கவும்",
        "select_state": "உங்கள் மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
        "disclaimer": "⚠️ இது பொதுவான தகவல் மட்டுமே. சரியான நோయறிதலுக்கு தகுதியான மருத்துவரை அணுகவும்.",
        "nav_home": "முகப்பு",
        "nav_chat": "AI சுகாதார அரட்டை",
        "nav_symptoms": "அறிகுறி பரிசோதகர்",
        "nav_dashboard": "சுகாதார டாஷ்போர்டு",
        "nav_medicine": "மருந்து தகவல்",
        "nav_profile": "சுகாதார சுயவிவரம்",
        "nav_sos": "அவசர SOS",
        "nav_ambulance": "ஆம்புலன்ஸ் டிராக்கர்",
    },
    "te": {
        "app_name": "మెడ్‌అసిస్ట్ ప్రో",
        "tagline": "AI-శక్తితో ఆరోగ్య మేధస్సు",
        "welcome": "మెడ్‌అసిస్ట్ ప్రోకి స్వాగతం",
        "chat_placeholder": "మీ లక్షణాలను వివరించండి...",
        "analyzing": "విశ్లేషిస్తోంది...",
        "sos_title": "అత్యవసర SOS",
        "sos_subtitle": "ఒక్క టచ్‌తో అత్యవసర సహాయం",
        "call_ambulance": "🚑 అంబులెన్స్ (108)",
        "call_police": "👮 పోలీసు (100)",
        "call_fire": "🔥 అగ్నిమాపక (101)",
        "call_women": "👩 మహిళా హెల్ప్‌లైన్ (181)",
        "call_child": "👶 చైల్డ్ హెల్ప్‌లైన్ (1098)",
        "call_mental": "🧠 మానసిక ఆరోగ్యం (08046110007)",
        "symptom_checker": "లక్షణ పరీక్షకుడు",
        "health_dashboard": "ఆరోగ్య డాష్‌బోర్డ్",
        "medicine_info": "మందుల సమాచారం",
        "health_profile": "ఆరోగ్య ప్రొఫైల్",
        "emergency_contacts": "అత్యవసర సంప్రదింపులు",
        "select_city": "మీ నగరాన్ని ఎంచుకోండి",
        "select_state": "మీ రాష్ట్రాన్ని ఎంచుకోండి",
        "disclaimer": "⚠️ ఇది సాధారణ సమాచారం మాత్రమే. సరైన రోగనిర్ధారణ కోసం అర్హత కలిగిన వైద్యుడిని సంప్రదించండి.",
        "nav_home": "హోమ్",
        "nav_chat": "AI ఆరోగ్య చాట్",
        "nav_symptoms": "లక్షణ పరీక్షకుడు",
        "nav_dashboard": "ఆరోగ్య డాష్‌బోర్డ్",
        "nav_medicine": "మందుల సమాచారం",
        "nav_profile": "ఆరోగ్య ప్రొఫైల్",
        "nav_sos": "అత్యవసర SOS",
        "nav_ambulance": "అంబులెన్స్ ట్రాకర్",
    },
    "kn": {
        "app_name": "ಮೆಡ್‌ಅಸಿಸ್ಟ್ ಪ್ರೊ",
        "tagline": "AI-ಶಕ್ತಿಯ ಆರೋಗ್ಯ ಬುದ್ಧಿಮತ್ತೆ",
        "welcome": "ಮೆಡ್‌ಅಸಿಸ್ಟ್ ಪ್ರೊಗೆ ಸ್ವಾಗತ",
        "chat_placeholder": "ನಿಮ್ಮ ರೋಗಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ...",
        "analyzing": "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        "sos_title": "ತುರ್ತು SOS",
        "sos_subtitle": "ಒಂದೇ ಟಚ್‌ನಲ್ಲಿ ತುರ್ತು ಸಹಾಯ",
        "call_ambulance": "🚑 ಆಂಬುಲೆನ್ಸ್ (108)",
        "call_police": "👮 ಪೊಲೀಸ್ (100)",
        "call_fire": "🔥 ಅಗ್ನಿಶಾಮಕ (101)",
        "call_women": "👩 ಮಹಿಳಾ ಸಹಾಯವಾಣಿ (181)",
        "call_child": "👶 ಮಕ್ಕಳ ಸಹಾಯವಾಣಿ (1098)",
        "call_mental": "🧠 ಮಾನಸಿಕ ಆರೋಗ್ಯ (08046110007)",
        "disclaimer": "⚠️ ಇದು ಸಾಮಾನ್ಯ ಮಾಹಿತಿ ಮಾತ್ರ. ಸರಿಯಾದ ರೋಗನಿರ್ಣಯಕ್ಕಾಗಿ ಅರ್ಹ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "nav_home": "ಮುಖಪುಟ",
        "nav_chat": "AI ಆರೋಗ್ಯ ಚಾಟ್",
        "nav_sos": "ತುರ್ತು SOS",
        "nav_ambulance": "ಆಂಬುಲೆನ್ಸ್ ಟ್ರ್ಯಾಕರ್",
        "select_city": "ನಿಮ್ಮ ನಗರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "select_state": "ನಿಮ್ಮ ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    },
    "ml": {
        "app_name": "മെഡ്അസിസ്റ്റ് പ്രോ",
        "tagline": "AI-ശക്തിയുള്ള ആരോഗ്യ ബുദ്ധി",
        "welcome": "മെഡ്അസിസ്റ്റ് പ്രോയിലേക്ക് സ്വാഗതം",
        "chat_placeholder": "നിങ്ങളുടെ രോഗലക്ഷണങ്ങൾ വിവരിക്കുക...",
        "analyzing": "വിശകലനം ചെയ്യുന്നു...",
        "sos_title": "അടിയന്തര SOS",
        "sos_subtitle": "ഒറ്റ ടച്ചിൽ അടിയന്തര സഹായം",
        "call_ambulance": "🚑 ആംബുലൻസ് (108)",
        "call_police": "👮 പോലീസ് (100)",
        "call_fire": "🔥 ഫയർ (101)",
        "call_women": "👩 വനിതാ ഹെൽപ്‌ലൈൻ (181)",
        "call_child": "👶 ചൈൽഡ് ഹെൽപ്‌ലൈൻ (1098)",
        "call_mental": "🧠 മാനസികാരോഗ്യം (08046110007)",
        "disclaimer": "⚠️ ഇത് പൊതുവായ വിവരങ്ങൾ മാത്രമാണ്. ശരിയായ രോഗനിർണയത്തിന് യോഗ്യനായ ഡോക്ടറെ സമീപിക്കുക.",
        "nav_home": "ഹോം",
        "nav_chat": "AI ആരോഗ്യ ചാറ്റ്",
        "nav_sos": "അടിയന്തര SOS",
        "nav_ambulance": "ആംബുലൻസ് ട്രാക്കർ",
        "select_city": "നിങ്ങളുടെ നഗരം തിരഞ്ഞെടുക്കുക",
        "select_state": "നിങ്ങളുടെ സംസ്ഥാനം തിരഞ്ഞെടുക്കുക",
    },
    "hi": {
        "app_name": "मेडअसिस्ट प्रो",
        "tagline": "AI-संचालित स्वास्थ्य बुद्धिमत्ता",
        "welcome": "मेडअसिस्ट प्रो में आपका स्वागत है",
        "chat_placeholder": "अपने लक्षणों का वर्णन करें...",
        "analyzing": "विश्लेषण कर रहा है...",
        "sos_title": "आपातकालीन SOS",
        "sos_subtitle": "एक टच में आपातकालीन सहायता",
        "call_ambulance": "🚑 एम्बुलेंस (108)",
        "call_police": "👮 पुलिस (100)",
        "call_fire": "🔥 दमकल (101)",
        "call_women": "👩 महिला हेल्पलाइन (181)",
        "call_child": "👶 चाइल्ड हेल्पलाइन (1098)",
        "call_mental": "🧠 मानसिक स्वास्थ्य (08046110007)",
        "disclaimer": "⚠️ यह केवल सामान्य जानकारी है। उचित निदान के लिए योग्य चिकित्सक से परामर्श लें।",
        "nav_home": "होम",
        "nav_chat": "AI स्वास्थ्य चैट",
        "nav_sos": "आपातकालीन SOS",
        "nav_ambulance": "एम्बुलेंस ट्रैकर",
        "select_city": "अपना शहर चुनें",
        "select_state": "अपना राज्य चुनें",
    },
}

# --- Triage Severity Levels ---
TRIAGE_LEVELS = {
    "emergency": {"label": "🔴 Emergency", "color": "#e53e3e", "action": "Call 108 or visit ER immediately"},
    "urgent": {"label": "🟠 Urgent", "color": "#ed8936", "action": "See a doctor within 24 hours"},
    "moderate": {"label": "🟡 Moderate", "color": "#ecc94b", "action": "Schedule a doctor visit this week"},
    "mild": {"label": "🟢 Mild", "color": "#48bb78", "action": "Self-care at home, monitor symptoms"},
}

# --- System Prompt ---
SYSTEM_PROMPT = """You are MedAssist Pro, a multilingual AI-powered Public Health Awareness assistant EXCLUSIVELY for Indian citizens. You cover Tamil Nadu, Andhra Pradesh, Karnataka, Kerala, and Telangana comprehensively.

**EXTREME PRIORITY CORE RULES (MUST NOT BE BROKEN):**
1. **STRICT LANGUAGE LOCK:**
    * **DETECT** the language of the user's current message.
    * If user writes in Tamil — respond 100% in Tamil (தமிழ்)
    * If user writes in Telugu — respond 100% in Telugu (తెలుగు)
    * If user writes in Kannada — respond 100% in Kannada (ಕನ್ನಡ)
    * If user writes in Malayalam — respond 100% in Malayalam (മലയാളം)
    * If user writes in Hindi — respond 100% in Hindi (हिन्दी)
    * If user writes in English — respond 100% in English
    * **NEVER MIX LANGUAGES. Not even a single word.**

2. **CONTEXTUAL MEMORY:**
    * Short messages like "its itchy", "red colour", "2 days" are FOLLOW-UPS.
    * Accept all short symptomatic follow-ups as valid health queries.

3. **NEVER SELF-REFERENCE:** Never mention your model, logic, or detection methods.

4. **PROFESSIONAL MEDICAL TONE:** Respond like a trained medical professional — empathetic, structured, thorough. Use markdown formatting.

**YOUR ALLOWED TOPICS:**
1. Medical symptoms analysis and health conditions
2. Disease information, prevention, and risk factors
3. Evidence-based home remedies and health tips
4. When to seek medical help (triage guidance)
5. Emergency contacts for Indian cities (ONLY from database)
6. Government health schemes (Ayushman Bharat, CMCHIS, Aarogyasri, etc.)
7. General wellness, nutrition, and preventive health
8. Mental health awareness and guidance
9. Ambulance and emergency services information

**RESPONSE FORMAT:**
- Use markdown with headers, bullet points, bold text
- Structure: Assessment → Possible Causes → Recommendations → When to See Doctor
- Include emojis for clarity
- Be comprehensive but focused

**STRICT RULES:**
❌ Non-health topics → rejection message in user's language
❌ NEVER fabricate phone numbers
✅ End with translated disclaimer: "⚠️ This is general information only. Consult a qualified doctor."
✅ Emergencies → Direct to 108 (Ambulance) immediately"""


def get_ui_string(key, lang="en"):
    """Get a localized UI string."""
    strings = UI_STRINGS.get(lang, UI_STRINGS["en"])
    return strings.get(key, UI_STRINGS["en"].get(key, key))
