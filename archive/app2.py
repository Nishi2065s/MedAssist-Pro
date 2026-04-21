import streamlit as st
import pandas as pd
from groq import Groq
import os
import re

# Page configuration
st.set_page_config(
    page_title="Health Awareness Chatbot - India",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
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

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None
if 'emergency_data' not in st.session_state:
    st.session_state.emergency_data = None
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = []

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a Public Health Awareness Chatbot EXCLUSIVELY for Indian citizens. You have STRICT limitations:

**YOUR ONLY ALLOWED TOPICS:**
1. Medical symptoms and health conditions
2. Disease information and prevention
3. Home remedies and health tips
4. When to seek medical help
5. Emergency contacts for Indian cities (ONLY from provided database - NEVER make up phone numbers)
6. Nutrition and healthy lifestyle relevant to India
7. Common illnesses, first aid, and healthcare guidance

**STRICT RULES - YOU MUST FOLLOW:**
❌ If asked about ANYTHING other than health/medical topics, you MUST respond ONLY with:
"I am a health awareness chatbot for Indian citizens. I can only help with health-related queries such as symptoms, diseases, remedies, and emergency contacts. Please ask me a health-related question."

❌ DO NOT answer questions about: weather, sports, entertainment, politics, general knowledge, coding, math problems, recipes (unless health-related), or ANY non-health topic.

❌ NEVER provide phone numbers from your knowledge. If asked for emergency contacts, you MUST say "Please specify the city name so I can look up the emergency contact from the database."

❌ NEVER make up or hallucinate phone numbers.

✅ When analyzing symptoms: Ask clarifying questions, suggest possible conditions, recommend when to see a doctor.

✅ Always add: "⚠️ This is general information only. Please consult a qualified doctor for proper diagnosis and treatment."

✅ For emergencies: Direct to call 108 (National Ambulance) or visit nearest hospital immediately.

**REMEMBER:** You are a HEALTH-ONLY assistant. Reject all non-health queries politely but firmly."""

def load_emergency_contacts(uploaded_file):
    """Load emergency contacts from CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        # Ensure column names are clean
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading emergency contacts: {str(e)}")
        return None

def extract_city_from_query(query):
    """Extract city name from user query"""
    # Common patterns for asking about cities
    patterns = [
        r'(?:in|for|at|of)\s+([A-Za-z\s]+?)(?:\s+city|\s+emergency|\s+contact|\s+number|\?|$)',
        r'([A-Za-z\s]+?)\s+(?:emergency|contact|phone|number|helpline)',
        r'emergency\s+(?:in|for|at|of)\s+([A-Za-z\s]+)',
        r'helpline\s+(?:in|for|at|of|number in)\s+([A-Za-z\s]+)',
        r'number\s+(?:in|for|at|of)\s+([A-Za-z\s]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            # Clean up common words
            city = re.sub(r'\b(city|emergency|contact|phone|number|the|helpline)\b', '', city, flags=re.IGNORECASE).strip()
            if city and len(city) > 2:
                return city
    
    # If no pattern matched, try to find any city name directly
    # Check against loaded cities if available
    if st.session_state.emergency_data is not None:
        for city_name in st.session_state.emergency_data.iloc[:, 0]:
            if city_name.lower() in query.lower():
                return city_name
    
    return None

def get_emergency_contact(city_name, df):
    """Get emergency contact for a specific city from database"""
    if df is None:
        return None
    
    # Try exact match first (case-insensitive)
    city_match = df[df.iloc[:, 0].str.lower().str.strip() == city_name.lower().strip()]
    
    if not city_match.empty:
        city = city_match.iloc[0, 0]
        phone = city_match.iloc[0, 1]
        return f"📞 **Emergency Contact for {city}:** {phone}\n\n🚑 You can also call the National Ambulance Service: **108** (available across India)"
    else:
        # Partial match
        partial_match = df[df.iloc[:, 0].str.lower().str.contains(city_name.lower(), na=False)]
        if not partial_match.empty:
            results = []
            for _, row in partial_match.head(3).iterrows():
                results.append(f"📞 **{row.iloc[0]}:** {row.iloc[1]}")
            return "\n".join(results) + "\n\n🚑 National Ambulance Service: **108**"
        
        return None

def is_health_related(query):
    """Check if query is health-related"""
    health_keywords = [
        # Common symptoms
        'symptom', 'pain', 'ache', 'fever', 'cough', 'cold', 'sneeze', 'headache', 'migraine',
        'nausea', 'vomit', 'diarrhea', 'constipation', 'fatigue', 'tired', 'weakness', 'dizzy',
        'swelling', 'rash', 'itch', 'sore', 'burn', 'bleed', 'bruise', 'cramp', 'spasm',
        
        # Body parts & organs
        'stomach', 'abdomen', 'chest', 'throat', 'nose', 'ear', 'eye', 'mouth', 'tooth',
        'head', 'neck', 'back', 'shoulder', 'arm', 'hand', 'leg', 'foot', 'knee', 'joint',
        'skin', 'hair', 'nail', 'heart', 'lung', 'liver', 'kidney', 'brain', 'bone', 'muscle',
        
        # Common conditions & diseases
        'disease', 'illness', 'sick', 'infection', 'virus', 'bacteria', 'flu', 'malaria',
        'dengue', 'typhoid', 'tuberculosis', 'asthma', 'diabetes', 'hypertension', 'cancer',
        'allergy', 'allergic', 'pneumonia', 'bronchitis', 'arthritis', 'thyroid', 'anemia',
        
        # Medical terms
        'medical', 'health', 'doctor', 'hospital', 'clinic', 'medicine', 'medication', 'drug',
        'treatment', 'therapy', 'surgery', 'diagnosis', 'prescription', 'vaccine', 'injection',
        'test', 'checkup', 'consultation', 'remedy', 'cure', 'healing',
        
        # Emergency & contacts
        'emergency', 'urgent', 'ambulance', 'helpline', 'contact', 'phone number',
        
        # Health categories
        'nutrition', 'diet', 'vitamin', 'protein', 'calcium', 'blood', 'pressure', 'sugar',
        'weight', 'exercise', 'fitness', 'mental health', 'depression', 'anxiety', 'stress',
        'sleep', 'insomnia', 'pregnant', 'pregnancy', 'baby', 'child', 'infant', 'maternal',
        'injury', 'wound', 'fracture', 'sprain', 'cut', 'first aid'
    ]
    
    query_lower = query.lower()
    
    # Check for health keywords
    if any(keyword in query_lower for keyword in health_keywords):
        return True
    
    # Additional patterns for health queries
    health_patterns = [
        r'\bhow to (treat|cure|prevent|manage)',
        r'\bwhat (causes|is)',
        r'\bfeeling (unwell|sick|ill)',
        r'\b(home|natural) remed(y|ies)',
        r'\bside effects',
        r'\bcan (i|you) (take|use|eat)',
    ]
    
    for pattern in health_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

def chat_with_bot(user_message, api_key):
    """Send message to Groq API and get response"""
    try:
        if st.session_state.groq_client is None:
            st.session_state.groq_client = Groq(api_key=api_key)
        
        # First, check if it's health-related
        if not is_health_related(user_message):
            return "I am a health awareness chatbot for Indian citizens. I can only help with health-related queries such as symptoms, diseases, remedies, and emergency contacts. Please ask me a health-related question."
        
        # Check if user is asking for emergency contact
        emergency_keywords = ['emergency', 'contact', 'phone', 'number', 'helpline', 'ambulance', 'hospital number']
        is_emergency_query = any(keyword in user_message.lower() for keyword in emergency_keywords)
        
        emergency_context = ""  
        if is_emergency_query and st.session_state.emergency_data is not None:
            city = extract_city_from_query(user_message)
            if city:
                emergency_info = get_emergency_contact(city, st.session_state.emergency_data)
                if emergency_info:
                    # Append the contact info to the prompt for the LLM to use and return
                    emergency_context = f"\n\n[DATABASE RESULT - MUST RETURN THIS INFO ONLY]: {emergency_info}"
                else:
                    available_cities = ", ".join(st.session_state.emergency_data.iloc[:, 0].head(10).tolist())
                    emergency_context = f"\n\n[INSTRUCTION]: City '{city}' not found. Ask the user to specify a city from the available list or use National Ambulance 108. Available cities include: {available_cities}"
            else:
                available_cities = ", ".join(st.session_state.emergency_data.iloc[:, 0].head(10).tolist())
                # Prompt the LLM to ask for a city name
                emergency_context = f"\n\n[INSTRUCTION]: Ask user to specify city name so you can look up the emergency contact from the database. Available cities include: {available_cities}"
              
        # Build messages with conversation memory
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation memory (last 6 exchanges = 12 messages)
        memory_limit = min(6, len(st.session_state.conversation_memory))
        for mem in st.session_state.conversation_memory[-memory_limit:]:
            messages.append({"role": "user", "content": mem["user"]})
            messages.append({"role": "assistant", "content": mem["assistant"]})
        
        # Add current message
        current_message = user_message + emergency_context
        messages.append({"role": "user", "content": current_message})
        
        # Call Groq API
        response = st.session_state.groq_client.chat.completions.create(
            model="gemma2-9b-it",
            #model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        bot_response = response.choices[0].message.content
        
        # Store in conversation memory (keep last 20 exchanges maximum)
        st.session_state.conversation_memory.append({
            "user": user_message,
            "assistant": bot_response
        })
        
        # Limit memory to last 20 exchanges
        if len(st.session_state.conversation_memory) > 20:
            st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]
        
        return bot_response
    
    except Exception as e:
        return f"❌ Error: {str(e)}. Please check your API key and try again."

# Main UI
st.title("🏥 Public Health Awareness Chatbot")
st.subheader("Healthcare Assistant for Indian Citizens")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input("Enter your Groq API Key:", type="password", key="api_key_input")
    
    # Emergency contacts file upload
    st.header("📞 Emergency Contacts")
    uploaded_file = st.file_uploader("Upload Emergency Contacts CSV", type=['csv'])
    
    if uploaded_file is not None:
        st.session_state.emergency_data = load_emergency_contacts(uploaded_file)
        if st.session_state.emergency_data is not None:
            st.success(f"✅ Loaded {len(st.session_state.emergency_data)} cities")
            with st.expander("Preview Data"):
                st.dataframe(st.session_state.emergency_data.head(10))
    
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
if not api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar to start chatting.")
    st.info("""
    **How to get a Groq API Key:**
    1. Visit [https://console.groq.com](https://console.groq.com)
    2. Sign up or log in
    3. Navigate to API Keys section
    4. Create a new API key
    5. Copy and paste it in the sidebar
    """)
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
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                bot_response = chat_with_bot(user_input, api_key)
            st.write(bot_response)
        
        # Add bot response to chat
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