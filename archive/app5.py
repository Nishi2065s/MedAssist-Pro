import streamlit as st
import pandas as pd
from groq import Groq
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# --- CONFIGURATION CONSTANTS ---
# 1. LLM Model: Using the model specified by the user.
#LLM_MODEL = "llama-3.3-70b-versatile" 
#LLM_MODEL = "gemma2-9b-it"
#LLM_MODEL = "groq/compound-mini"
LLM_MODEL = "openai/gpt-oss-20b"
# 2. API Key Configuration: Reads from environment variable 'GROQ_API_KEY'.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "PLACEHOLDER_FOR_GROQ_KEY") 

# 3. Default CSV file path
EMERGENCY_CONTACTS_FILE = "emergency_contacts.csv" 

# 4. AGGRESSIVELY REFINED SYSTEM PROMPT
SYSTEM_PROMPT = f"""You are a multilingual Public Health Awareness Chatbot EXCLUSIVELY for Indian citizens. You are currently running the {LLM_MODEL} model.

**EXTREME PRIORITY CORE RULES (MUST NOT BE BROKEN):**
1. **STRICT LANGUAGE LOCK:**
    * **DETECT** the language of the user's current message (e.g., English, Hindi, Tamil).
    * **RESPOND 100%** ENTIRELY in that exact language.
    * **NEVER MIX LANGUAGES.**
    * If the user asks in English, your entire reply, including the disclaimer, MUST be in English.

2. **CONTEXTUAL MEMORY:**
    * If the user's message is short (e.g., "its itchy", "red colour", "2 days"), it is almost certainly a **FOLLOW-UP** to a previous question you asked about their symptoms.
    * You **MUST** accept all short, symptomatic follow-ups as valid health queries.

3. **NEVER SELF-REFERENCE:** NEVER, under any circumstance, mention your internal logic, language detection, memory usage, or your model name ({LLM_MODEL}).

**YOUR ONLY ALLOWED TOPICS:**
1. Medical symptoms and health conditions
2. Disease information and prevention
3. Home remedies and health tips
4. When to seek medical help
5. Emergency contacts for Indian cities (ONLY from provided database - NEVER make up phone numbers)

**STRICT RULES - YOU MUST FOLLOW:**
❌ If asked about ANYTHING other than health/medical topics, you MUST respond ONLY with the standard non-health response, translated ENTIRELY into the user's language:
"I am a health awareness chatbot for Indian citizens. I can only help with health-related queries such as symptoms, diseases, remedies, and emergency contacts. Please ask me a health-related question."

❌ NEVER provide phone numbers from your knowledge. If asked for emergency contacts, you MUST say "Please specify the city name so I can look up the emergency contact from the database," translated into the user's language.

✅ Always add the following disclaimer at the end of every helpful response. You MUST translate the ENTIRE disclaimer into the user's language: "⚠️ This is general information only. Please consult a qualified doctor for proper diagnosis and treatment."

✅ For emergencies: Direct to call 108 (National Ambulance) or visit nearest hospital immediately, translated into the user's language.

✅ Responses should be less than hundred words."""

# --------------------------------------------------

# Page configuration
st.set_page_config(
    page_title="Health Awareness Chatbot - India",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS... (no changes)
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state... (no changes)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None
if 'emergency_data' not in st.session_state:
    st.session_state.emergency_data = None
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = []

def load_emergency_contacts(file_path):
    """Load emergency contacts from CSV file"""
    try:
        if not os.path.exists(file_path):
            return None
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

def extract_city_from_query(query):
    """Extract city name from user query (Multilingual support)"""
    patterns = [
        r'(?:in|for|at|of|में|के लिए|में|की|का)\s+([A-Za-z\s]+?)(?:\s+city|\s+emergency|\s+contact|\s+number|\s+शहर|\s+आपातकालीन|\s+संपर्क|\s+नंबर|\?|$)',
        r'([A-Za-z\s]+?)\s+(?:emergency|contact|phone|number|helpline|आपातकालीन|संपर्क|नंबर|हेल्पलाइन)',
        r'emergency\s+(?:in|for|at|of|में|के लिए|में|की|का)\s+([A-Za-z\s]+)',
        r'helpline\s+(?:in|for|at|of|number in|में|के लिए|में|की|का|नंबर)\s+([A-Za-z\s]+)',
        r'number\s+(?:in|for|at|of|में|के लिए|में|की|का)\s+([A-Za-z\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            city = re.sub(r'\b(city|emergency|contact|phone|number|the|helpline|शहर|आपातकालीन|संपर्क|नंबर)\b', '', city, flags=re.IGNORECASE).strip()
            if city and len(city) > 2:
                return city
    
    if st.session_state.emergency_data is not None:
        for city_name in st.session_state.emergency_data.iloc[:, 0]:
            if city_name.lower() in query.lower():
                return city_name
    
    return None

def get_emergency_contact(city_name, df):
    """Get emergency contact for a specific city from database (English-only output for LLM translation)"""
    if df is None:
        return None
    
    city_match = df[df.iloc[:, 0].str.lower().str.strip() == city_name.lower().strip()]
    
    if not city_match.empty:
        city = city_match.iloc[0, 0]
        phone = city_match.iloc[0, 1]
        return f"📞 **Emergency Contact for {city}:** {phone}\n\n🚑 You can also call the National Ambulance Service: **108** (available across India)"
    else:
        partial_match = df[df.iloc[:, 0].str.lower().str.contains(city_name.lower(), na=False)]
        if not partial_match.empty:
            results = []
            for _, row in partial_match.head(3).iterrows():
                results.append(f"📞 **{row.iloc[0]}:** {row.iloc[1]}")
            return "Could not find an exact match, but here are some related city contacts:\n\n" + "\n".join(results) + "\n\n🚑 National Ambulance Service: **108**"
        
        return None

def is_health_related(query):
    """Check if query is health-related (Improved memory check for short follow-ups)"""
    health_keywords = [
        'symptom', 'pain', 'ache', 'fever', 'cough', 'cold', 'headache', 'nausea', 'vomit', 'rash', 'itch',
        'बीमारी', 'दर्द', 'बुखार', 'खाँसी', 'ठंड', 'सिरदर्द', 'उल्टी', 'मतली', 'दाने', 'खुजली',
        'stomach', 'chest', 'throat', 'mouth', 'heart', 'lung', 'liver', 'kidney', 'brain', 'hand',
        'पेट', 'सीने', 'गले', 'मुँह', 'दिल', 'फेफड़े', 'जिगर', 'गुर्दा', 'मस्तिष्क', 'हाथ',
        'medical', 'health', 'doctor', 'hospital', 'medicine', 'treatment', 'vaccine', 'remedy',
        'स्वास्थ्य', 'डॉक्टर', 'अस्पताल', 'दवा', 'इलाज', 'टीका', 'उपचार',
        'emergency', 'urgent', 'ambulance', 'helpline', 'contact', 'phone number', 'red', 'colour', 'color',
        'आपातकालीन', 'जरूरी', 'एम्बुलेंस', 'हेल्पलाइन', 'संपर्क', 'नंबर', 'लाल', 'रंग', '2 days', '2days', 'days', 'since'
    ]
    
    query_lower = query.lower()
    
    # 1. Check for direct keywords
    if any(keyword in query_lower for keyword in health_keywords):
        return True
    
    # 2. Check for follow-up context (This is the primary fix for the rejection issue)
    if st.session_state.conversation_memory:
        # Check if the last assistant message was a clarifying question
        last_assistant_query = st.session_state.conversation_memory[-1].get("assistant", "").lower()
        if any(k in last_assistant_query for k in ['itchy', 'painful', 'red', 'inflamed', 'how long', 'more about', 'tell me more', 'please provide details']):
            return True # Treat as health-related follow-up to a clarifying question
            
    # 3. Check for common health patterns
    health_patterns = [
        r'\bhow to (treat|cure|prevent|manage)', r'\bwhat (causes|is)', r'\bfeeling (unwell|sick|ill)',
        r'\b(home|natural) remed(y|ies)', r'\bside effects', r'\bcan (i|you) (take|use|eat)',
    ]
    
    for pattern in health_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

def chat_with_bot(user_message):
    """Send message to Groq API and get multilingual response"""
    try:
        # Check for API key and initialize client
        if st.session_state.groq_client is None:
            if GROQ_API_KEY == "PLACEHOLDER_FOR_GROQ_KEY" or not GROQ_API_KEY:
                return "❌ Error: The Groq API key is not set. Please ensure GROQ_API_KEY is defined in your .env file or environment variables."
            st.session_state.groq_client = Groq(api_key=GROQ_API_KEY)
        
        # 1. Non-Health Rejection
        if not is_health_related(user_message):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            # Instruct the LLM to provide ONLY the translated rejection message
            messages.append({"role": "user", "content": f"Please provide ONLY the standard non-health rejection message, translated ENTIRELY into the language of my query: '{user_message}'"})
            
            response = st.session_state.groq_client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=256,
            )
            return response.choices[0].message.content
        
        # 2. Emergency Contact Handling (with new, more robust logic)
        emergency_keywords = ['emergency', 'contact', 'phone', 'number', 'helpline', 'ambulance', 'hospital number', 'आपातकालीन', 'संपर्क', 'नंबर', 'हेल्पलाइन']
        is_emergency_query = any(keyword in user_message.lower() for keyword in emergency_keywords)
        
        emergency_context = ""
        if is_emergency_query and st.session_state.emergency_data is not None:
            city = extract_city_from_query(user_message)
            if city:
                emergency_info_en = get_emergency_contact(city, st.session_state.emergency_data)
                
                if emergency_info_en:
                    # New Logic: Detect if the user's query is in English.
                    # This bypasses the LLM translation step if not needed, preventing language mix-ups.
                    is_english_query = not any(char in user_message for char in 'ंिीुूृेैोौकखगघङचछजझञटठडढणतथदधनपफबभमयरलव')
                    
                    if is_english_query:
                        response_content = emergency_info_en
                    else:
                        # Use the LLM to translate only if the query is not English
                        translation_prompt = (
                            "The user asked for emergency contact. The English data found is: "
                            f"'{emergency_info_en}'. The user's original query was: '{user_message}'. "
                            "You **MUST** translate the English data and **MUST** respond **ENTIRELY** "
                            "in the language of the user's original query. DO NOT revert to English. KEEP all numbers and city names clear."
                        )
                        
                        messages = [{"role": "system", "content": translation_prompt}]
                        messages.append({"role": "user", "content": user_message})
                        
                        response = st.session_state.groq_client.chat.completions.create(
                            model=LLM_MODEL,
                            messages=messages,
                            temperature=0.0,
                            max_tokens=512,
                        )
                        response_content = response.choices[0].message.content
                    
                    st.session_state.conversation_memory.append({
                        "user": user_message,
                        "assistant": response_content
                    })
                    return response_content
                else:
                    available_cities = ", ".join(st.session_state.emergency_data.iloc[:, 0].head(10).tolist())
                    emergency_context = f"\n\n[INSTRUCTION]: The city was not found in the database. Ask the user to specify a city name (in Roman script). You must respond in the user's language. Available examples: {available_cities}"
            else:
                available_cities = ", ".join(st.session_state.emergency_data.iloc[:, 0].head(10).tolist())
                emergency_context = f"\n\n[INSTRUCTION]: Ask the user to specify the city name clearly from the database (in Roman script). You must respond in the user's language. Available examples: {available_cities}"
        
        # 3. Standard Health Query (Multilingual)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation memory
        memory_limit = min(10, len(st.session_state.conversation_memory))
        for mem in st.session_state.conversation_memory[-memory_limit:]:
            messages.append({"role": "user", "content": mem["user"]})
            messages.append({"role": "assistant", "content": mem["assistant"]})
        
        current_message = user_message + emergency_context
        messages.append({"role": "user", "content": current_message})
        
        response = st.session_state.groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        bot_response = response.choices[0].message.content
        
        st.session_state.conversation_memory.append({
            "user": user_message,
            "assistant": bot_response
        })
        
        if len(st.session_state.conversation_memory) > 20:
            st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
        
        return bot_response
    
    except Exception as e:
        return f"❌ Error: {str(e)}. Please check your API key and try again. Model: {LLM_MODEL}"

# --- Main Logic and UI ---

# Load CSV file automatically
if st.session_state.emergency_data is None:
    st.session_state.emergency_data = load_emergency_contacts(EMERGENCY_CONTACTS_FILE)

st.title("🏥 Public Health Awareness Chatbot")
st.subheader("Healthcare Assistant for Indian Citizens")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.markdown(f"**Selected LLM:** `{LLM_MODEL}` (Gemma 2 9B)")
    
    # API Key Status Check
    if GROQ_API_KEY == "PLACEHOLDER_FOR_GROQ_KEY":
        st.error("⚠️ **API Key Status:** NOT SET (Check .env file)")
    else:
        st.success("✅ **API Key Status:** Loaded (From .env file)")

    st.header("📞 Emergency Contacts")
    if st.session_state.emergency_data is not None:
        st.success(f"✅ Loaded {len(st.session_state.emergency_data)} cities from `{EMERGENCY_CONTACTS_FILE}`")
        with st.expander("Preview Emergency Contacts"):
            st.dataframe(st.session_state.emergency_data.head(10))
    else:
        st.warning(f"⚠️ Could not load data from `{EMERGENCY_CONTACTS_FILE}`. Ensure the file is present.")
    
    st.markdown("---")
    st.header("💾 Conversation Memory")
    st.info(f"Remembered exchanges: {len(st.session_state.conversation_memory)}")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    This chatbot helps you:
    - Analyze symptoms
    - Understand possible diseases
    - Get health remedies
    - Find emergency contacts
    
    **Note:** This is not a replacement for professional medical advice.
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.conversation_memory = []
        st.rerun()

# Main chat area
if GROQ_API_KEY == "PLACEHOLDER_FOR_GROQ_KEY":
    st.warning("⚠️ The Groq API Key is not loaded. Please ensure you have run `pip install python-dotenv` and your `.env` file contains `GROQ_API_KEY='your_key'`.")
else:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Describe your symptoms or ask a health question...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
          
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                bot_response = chat_with_bot(user_input) 
            st.write(bot_response)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>⚠️ Medical Disclaimer:</strong> This chatbot provides general health information only. 
    Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.</p>
    <p>🚑 <strong>In case of emergency, call 108 (National Ambulance Service)</strong></p>
</div>
""", unsafe_allow_html=True)