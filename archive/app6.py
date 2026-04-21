import streamlit as st
import pandas as pd
from google import genai 
from google.genai import types # Import types for configuration
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# --- CONFIGURATION CONSTANTS (UPDATED) ---
# CHANGED: Use a Google Gemini Model
LLM_MODEL = "gemini-2.5-flash"

# CHANGED: Use GOOGLE_API_KEY as the primary API key
API_KEY = os.getenv("GOOGLE_API_KEY", "PLACEHOLDER_FOR_GOOGLE_KEY") 
EMERGENCY_CONTACTS_FILE = "emergency_contacts.csv" 
# CRITICAL FIX: Limit injected text to prevent context overflow
SCHEME_CONTENT_CHAR_LIMIT = 8000 

# 4. AGGRESSIVELY REFINED SYSTEM PROMPT (UPDATED with new scheme topic)
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
6. **GOVERNMENT HEALTH SCHEMES/INSURANCE (Information is provided in the context when available)**

**STRICT RULES - YOU MUST FOLLOW:**
❌ If asked about ANYTHING other than health/medical topics, you MUST respond ONLY with the standard non-health response, translated ENTIRELY into the user's language:
"I am a health awareness chatbot for Indian citizens. I can only help with health-related queries such as symptoms, diseases, remedies, and emergency contacts. Please ask me a health-related question."

❌ NEVER provide phone numbers from your knowledge. If asked for emergency contacts, you MUST say "Please specify the city name so I can look up the emergency contact from the database," translated into the user's language.

✅ Always add the following disclaimer at the end of every helpful response. You MUST translate the ENTIRE disclaimer into the user's language: "⚠️ This is general information only. Please consult a qualified doctor for proper diagnosis and treatment."

✅ For emergencies: Direct to call 108 (National Ambulance) or visit nearest hospital immediately, translated into the user's language."""
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

# Initialize session state (UPDATED)
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# CHANGED: Renamed groq_client to llm_client
if 'llm_client' not in st.session_state:
    st.session_state.llm_client = None
    
if 'emergency_data' not in st.session_state:
    st.session_state.emergency_data = None
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = []
if 'scheme_data' not in st.session_state:
    st.session_state.scheme_data = None
if 'scheme_file_name' not in st.session_state:
    st.session_state.scheme_file_name = None


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

# --- NEW FUNCTION FOR PDF READING (PLACEHOLDER) ---
def read_uploaded_file(uploaded_file):
    """
    Reads the content of an uploaded file.
    ⚠️ IMPORTANT: You MUST implement actual PDF-to-Text conversion here 
    if using PDF files (e.g., using 'PyPDF2' or 'pymupdf').
    """
    try:
        if uploaded_file.name.lower().endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
            return content
        
        # You need to uncomment and install the required PDF library (e.g., pip install pypdf)
        # if uploaded_file.name.lower().endswith(".pdf"):
        #     import pypdf
        #     reader = pypdf.PdfReader(uploaded_file)
        #     text = ""
        #     for page in reader.pages:
        #         text += page.extract_text() if page.extract_text() else ""
        #     return text
        
        st.warning("Assuming Text or using simple read for non-TXT file. Install PDF reading libraries (PyPDF2/pymupdf) for reliable PDF support.")
        # Fallback: Read as raw text/bytes (might not work well for complex PDFs)
        return uploaded_file.read().decode("utf-8", errors="ignore") 
        
    except Exception as e:
        st.error(f"Failed to read file content: {e}")
        return None
# ----------------------------------------------------


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
    """Check if query is health-related (Updated with insurance keywords)"""
    health_keywords = [
        'symptom', 'pain', 'ache', 'fever', 'cough', 'cold', 'headache', 'nausea', 'vomit', 'rash', 'itch',
        'बीमारी', 'दर्द', 'बुखार', 'खाँसी', 'ठंड', 'सिरदर्द', 'उल्टी', 'मतली', 'दाने', 'खुजली',
        'stomach', 'chest', 'throat', 'mouth', 'heart', 'lung', 'liver', 'kidney', 'brain', 'hand',
        'पेट', 'सीने', 'गले', 'मुँह', 'दिल', 'फेफड़े', 'जिगर', 'गुर्दा', 'मस्तिष्क', 'हाथ',
        'medical', 'health', 'doctor', 'hospital', 'medicine', 'treatment', 'vaccine', 'remedy',
        'स्वास्थ्य', 'डॉक्टर', 'अस्पताल', 'दवा', 'इलाज', 'टीका', 'उपचार',
        'emergency', 'urgent', 'ambulance', 'helpline', 'contact', 'phone number', 'red', 'colour', 'color',
        'आपातकालीन', 'जरूरी', 'एम्बुलेंस', 'हेल्पलाइन', 'संपर्क', 'नंबर', 'लाल', 'रंग', '2 days', '2days', 'days', 'since',
        # <--- NEW KEYWORDS for scheme --->
        'insurance', 'scheme', 'yojana', 'policy', 'premium', 'benefit', 'claim', 'आयुष्मान', 'भारत', 'योजना', 'बीमा', 'स्कीम', 'health care'
    ]
    
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in health_keywords):
        return True
    
    # Check for follow-up context (Memory Fix)
    if st.session_state.conversation_memory:
        last_assistant_query = st.session_state.conversation_memory[-1].get("assistant", "").lower()
        if any(k in last_assistant_query for k in ['itchy', 'painful', 'red', 'inflamed', 'how long', 'more about', 'tell me more', 'please provide details']):
            return True 
            
    health_patterns = [
        r'\bhow to (treat|cure|prevent|manage)', r'\bwhat (causes|is)', r'\bfeeling (unwell|sick|ill)',
        r'\b(home|natural) remed(y|ies)', r'\bside effects', r'\bcan (i|you) (take|use|eat)',
    ]
    
    for pattern in health_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

def chat_with_bot(user_message):
    """Send message to Google GenAI API and get multilingual response (Updated for scheme context and truncation)"""
    try:
        # Check for API key and initialize client
        if st.session_state.llm_client is None:
            if API_KEY == "PLACEHOLDER_FOR_GOOGLE_KEY" or not API_KEY:
                return "❌ Error: The Google API key is not set. Please ensure GOOGLE_API_KEY is defined in your .env file or environment variables."
            # The genai.Client() automatically picks up the key from the GOOGLE_API_KEY environment variable.
            st.session_state.llm_client = genai.Client(api_key=API_KEY)
        
        # 1. Non-Health Rejection 
        if not is_health_related(user_message):
            
            rejection_message = f"Please provide ONLY the standard non-health rejection message, translated ENTIRELY into the language of my query: '{user_message}'"
            
            rejection_config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.0
            )
            
            response = st.session_state.llm_client.models.generate_content(
                model=LLM_MODEL,
                # FIXED: Pass contents as a list of dictionaries with role and parts (list of strings)
                contents=[{"role": "user", "parts": [rejection_message]}], 
                config=rejection_config
            )
            return response.text 

        # 2. Emergency Contact Handling 
        emergency_keywords = ['emergency', 'contact', 'phone', 'number', 'helpline', 'ambulance', 'hospital number', 'आपातकालीन', 'संपर्क', 'नंबर', 'हेल्पलाइन']
        is_emergency_query = any(keyword in user_message.lower() for keyword in emergency_keywords)
        emergency_context = ""
        
        if is_emergency_query and st.session_state.emergency_data is not None:
            city = extract_city_from_query(user_message)
            
            if city:
                emergency_info_en = get_emergency_contact(city, st.session_state.emergency_data)
                
                if emergency_info_en:
                    # Logic to bypass LLM translation for English queries
                    is_english_query = not any(char in user_message for char in 'ंिीुूृेैोौकखगघङचछजझञटठडढणतथदधनपफबभमयरलव')
                    
                    if is_english_query:
                        response_content = emergency_info_en
                    else:
                        # Use LLM to translate only if the query is not English (Hindi/other Indian language)
                        translation_prompt = (
                            "The user asked for emergency contact. The English data found is: "
                            f"'{emergency_info_en}'. The user's original query was: '{user_message}'. "
                            "You **MUST** translate the English data and **MUST** respond **ENTIRELY** "
                            "in the language of the user's original query. DO NOT revert to English. KEEP all numbers and city names clear."
                        )
                        
                        translation_config = types.GenerateContentConfig(
                            system_instruction=translation_prompt,
                            temperature=0.0
                        )
                        
                        response = st.session_state.llm_client.models.generate_content(
                            model=LLM_MODEL,
                            # FIXED: Pass contents as a list of strings/parts
                            contents=[user_message],
                            config=translation_config
                        )
                        response_content = response.text
                    
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


        # 3. Standard Health Query (Multilingual) with Scheme Context (NEW LOGIC)
        
        is_scheme_query = any(k in user_message.lower() for k in ['insurance', 'scheme', 'yojana', 'policy', 'आयुष्मान', 'बीमा'])
        
        scheme_context = ""
        if is_scheme_query:
            if st.session_state.scheme_data:
                # --- FIX: TRUNCATE SCHEME DATA TO PREVENT OVERFLOW ---
                scheme_data_to_inject = st.session_state.scheme_data
                if len(scheme_data_to_inject) > SCHEME_CONTENT_CHAR_LIMIT:
                    scheme_data_to_inject = scheme_data_to_inject[:SCHEME_CONTENT_CHAR_LIMIT] + "\n\n...[SCHEME DATA TRUNCATED DUE TO LENGTH LIMIT]..."

                # If scheme content is loaded, inject it into the prompt
                scheme_context = (
                    "\n\n[GOVERNMENT HEALTH SCHEME DOCUMENT CONTENT START]\n"
                    f"{scheme_data_to_inject}\n"
                    "[GOVERNMENT HEALTH SCHEME DOCUMENT CONTENT END]\n\n"
                    "INSTRUCTION: Use ONLY the provided scheme content to answer the user's question about insurance. You MUST translate the relevant details into the user's language."
                )
            else:
                # If no scheme data is loaded
                scheme_context = (
                    "\n\n[INSTRUCTION]: The user is asking about insurance schemes. The scheme document is NOT loaded. "
                    "Inform the user: 'To answer your query about government health insurance schemes, please upload the relevant PDF/Text document using the file uploader in the sidebar.' You must translate this message to the user's language."
                )

        # Append scheme context and emergency context to the system prompt
        full_system_prompt = SYSTEM_PROMPT + scheme_context 
        
        # CHANGED: Convert conversation memory to simple list of dictionaries (role/parts)
        contents = []
        memory_limit = min(10, len(st.session_state.conversation_memory))
        
        # Build conversation history in Gemini format
        for mem in st.session_state.conversation_memory[-memory_limit:]:
            # FIXED: Use simple dictionary/list format to avoid Part.from_text error
            contents.append({"role": "user", "parts": [mem["user"]]})
            contents.append({"role": "model", "parts": [mem["assistant"]]})
        
        current_message = user_message + emergency_context
        # Append current user message
        contents.append({"role": "user", "parts": [current_message]}) # FIXED: Simple list format

        
        # NEW FIX: Use config object for system instruction
        main_config = types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            temperature=0.7
        )

        # CHANGED: Use GenAI API call with config
        response = st.session_state.llm_client.models.generate_content(
            model=LLM_MODEL,
            contents=contents,
            config=main_config
        )
        
        # CHANGED: Response parsing
        bot_response = response.text
        
        st.session_state.conversation_memory.append({
            "user": user_message,
            "assistant": bot_response
        })
        
        if len(st.session_state.conversation_memory) > 20:
            st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
        
        return bot_response
    
    except Exception as e:
        # CHANGED: Update error message
        return f"❌ Error: {str(e)}. Please check your GOOGLE_API_KEY and ensure the 'google-genai' library is installed. Model: {LLM_MODEL}"

# --- Main Logic and UI ---

# Load CSV file automatically
if st.session_state.emergency_data is None:
    st.session_state.emergency_data = load_emergency_contacts(EMERGENCY_CONTACTS_FILE)

st.title("🏥 Public Health Awareness Chatbot")
st.subheader("Healthcare Assistant for Indian Citizens")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # CHANGED: Update model display
    st.markdown(f"**Selected LLM:** `{LLM_MODEL}` (Gemini 2.5 Flash)")
    
    # CHANGED: Update API Key Status Check to reflect GOOGLE_API_KEY usage
    if API_KEY == "PLACEHOLDER_FOR_GOOGLE_KEY":
        st.error("⚠️ **Google API Key:** NOT SET (Check .env file)")
    else:
        st.success("✅ **Google API Key:** Loaded")

    st.header("📞 Emergency Contacts")
    if st.session_state.emergency_data is not None:
        st.success(f"✅ Loaded {len(st.session_state.emergency_data)} cities from `{EMERGENCY_CONTACTS_FILE}`")
        with st.expander("Preview Emergency Contacts"):
            st.dataframe(st.session_state.emergency_data.head(10))
    else:
        st.warning(f"⚠️ Could not load data from `{EMERGENCY_CONTACTS_FILE}`. Ensure the file is present.")
    
    st.markdown("---")
    
    # <--- NEW FILE UPLOADER SECTION --->
    st.header("📄 Health Scheme Document")
    uploaded_scheme_file = st.file_uploader(
        "Upload Government Health Scheme PDF/Text File", 
        type=["pdf", "txt"], 
        accept_multiple_files=False,
        key="scheme_uploader"
    )

    if uploaded_scheme_file is not None and (st.session_state.scheme_data is None or uploaded_scheme_file.name != st.session_state.scheme_file_name):
        with st.spinner(f"Reading {uploaded_scheme_file.name}..."):
            file_content = read_uploaded_file(uploaded_scheme_file)
            if file_content:
                st.session_state.scheme_data = file_content
                st.session_state.scheme_file_name = uploaded_scheme_file.name
                st.success(f"✅ Loaded content from {uploaded_scheme_file.name}.")
                st.rerun()
            else:
                st.session_state.scheme_data = None
                st.session_state.scheme_file_name = None
    
    if st.session_state.scheme_data:
        st.success(f"✅ Scheme content loaded from {st.session_state.scheme_file_name}")
        with st.expander("Preview Scheme Content (first 500 chars)"):
            st.code(st.session_state.scheme_data[:500] + "...")
    else:
        st.warning("⚠️ No scheme document loaded.")
        
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
    - Get scheme details (if PDF/Text loaded)
    
    **Note:** This is not a replacement for professional medical advice.
    """)
    
    if st.button("Clear Chat History and Data"): 
        st.session_state.messages = []
        st.session_state.conversation_memory = []
        st.session_state.scheme_data = None
        st.session_state.scheme_file_name = None
        st.rerun()

# Main chat area
if API_KEY == "PLACEHOLDER_FOR_GOOGLE_KEY":
    st.warning("⚠️ The Google API Key is not loaded. Please ensure you have run `pip install google-genai python-dotenv` and your `.env` file contains `GOOGLE_API_KEY='your_key'`.")
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