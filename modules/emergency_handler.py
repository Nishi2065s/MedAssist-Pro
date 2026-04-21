"""
Emergency Handler — Ultra-level city-based emergency contact lookup.
Supports 150+ cities across Tamil Nadu, Andhra Pradesh, Karnataka, Kerala, Telangana.
"""
import re
import os
import pandas as pd
import streamlit as st
from config.settings import EMERGENCY_CONTACTS_FILE


def load_emergency_contacts():
    """Load emergency contacts from CSV file into session state."""
    if st.session_state.get('emergency_data') is not None:
        return st.session_state.emergency_data

    try:
        if not os.path.exists(EMERGENCY_CONTACTS_FILE):
            return None
        df = pd.read_csv(EMERGENCY_CONTACTS_FILE)
        df.columns = df.columns.str.strip()
        st.session_state.emergency_data = df
        return df
    except Exception:
        return None


def get_cities_by_state(state_name=None):
    """Get list of cities, optionally filtered by state."""
    df = st.session_state.get('emergency_data')
    if df is None:
        return []
    if state_name:
        return sorted(df[df['State'].str.lower() == state_name.lower()]['City'].tolist())
    return sorted(df['City'].tolist())


def get_states():
    """Get list of unique states."""
    df = st.session_state.get('emergency_data')
    if df is None:
        return []
    return sorted(df['State'].unique().tolist())


def extract_city_from_query(query):
    """Extract city name from user query with multilingual pattern matching."""
    patterns = [
        r'(?:in|for|at|of|near|around|में|के लिए|की|का|இல்|ல|లో|ನಲ್ಲಿ|ൽ)\s+([A-Za-z\s]+?)(?:\s+city|\s+emergency|\s+contact|\s+number|\s+hospital|\?|$)',
        r'([A-Za-z\s]+?)\s+(?:emergency|contact|phone|number|helpline|hospital|ambulance)',
        r'emergency\s+(?:in|for|at|of|near)\s+([A-Za-z\s]+)',
        r'hospital\s+(?:in|for|at|of|near)\s+([A-Za-z\s]+)',
        r'ambulance\s+(?:in|for|at|of|near)\s+([A-Za-z\s]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            city = re.sub(
                r'\b(city|emergency|contact|phone|number|the|helpline|hospital|ambulance)\b',
                '', city, flags=re.IGNORECASE
            ).strip()
            if city and len(city) > 2:
                return city

    # Direct city name match from database
    df = st.session_state.get('emergency_data')
    if df is not None:
        for city_name in df['City']:
            if str(city_name).lower() in query.lower():
                return city_name

    return None


def get_emergency_contact(city_name):
    """Lookup full emergency info for a city."""
    df = st.session_state.get('emergency_data')
    if df is None:
        return None

    city_match = df[df['City'].str.lower().str.strip() == city_name.lower().strip()]

    if not city_match.empty:
        row = city_match.iloc[0]
        return {
            "city": row['City'],
            "state": row['State'],
            "phone": row['Emergency_Phone'],
            "hospital": row['Hospital_Name'],
            "type": row.get('Type', 'Government'),
            "ambulance": row.get('Ambulance', '108'),
            "police": row.get('Police', '100'),
            "fire": row.get('Fire', '101'),
            "formatted": (
                f"📍 **{row['City']}, {row['State']}**\n\n"
                f"🏥 **Hospital:** {row['Hospital_Name']} ({row.get('Type', 'Government')})\n"
                f"📞 **Emergency Phone:** {row['Emergency_Phone']}\n"
                f"🚑 **Ambulance:** {row.get('Ambulance', '108')}\n"
                f"👮 **Police:** {row.get('Police', '100')}\n"
                f"🔥 **Fire:** {row.get('Fire', '101')}\n\n"
                f"🆘 **National Helplines:**\n"
                f"- 🚑 Ambulance: **108**\n"
                f"- 👩 Women Helpline: **181**\n"
                f"- 👶 Child Helpline: **1098**\n"
                f"- 🧠 Mental Health (iCall): **08046110007**\n"
                f"- 🚭 Quit Smoking: **1800-11-2356**"
            )
        }

    # Partial match
    partial = df[df['City'].str.lower().str.contains(city_name.lower(), na=False)]
    if not partial.empty:
        results = []
        for _, row in partial.head(5).iterrows():
            results.append(f"📞 **{row['City']}** ({row['State']}): {row['Emergency_Phone']} — {row['Hospital_Name']}")
        return {
            "city": city_name,
            "formatted": (
                "Could not find an exact match. Here are similar results:\n\n"
                + "\n".join(results)
                + "\n\n🚑 **National Ambulance: 108**"
            )
        }

    return None


def get_nearby_hospitals(city_name, limit=5):
    """Get hospitals near a city (same state)."""
    df = st.session_state.get('emergency_data')
    if df is None:
        return []

    city_match = df[df['City'].str.lower().str.strip() == city_name.lower().strip()]
    if city_match.empty:
        return []

    state = city_match.iloc[0]['State']
    state_hospitals = df[df['State'] == state]
    # Exclude the city itself
    nearby = state_hospitals[state_hospitals['City'].str.lower() != city_name.lower()]
    return nearby.head(limit).to_dict('records')


def is_emergency_query(query):
    """Detect if the query is asking for emergency contacts."""
    keywords = [
        'emergency', 'contact', 'phone', 'number', 'helpline', 'ambulance',
        'hospital number', 'sos', 'urgent', 'help',
        'आपातकालीन', 'संपर्क', 'नंबर', 'हेल्पलाइन',
        'அவசர', 'தொடர்பு', 'எண்',
        'అత్యవసర', 'సంప్రదింపు', 'నంబర్',
        'ತುರ್ತು', 'ಸಂಪರ್ಕ', 'ನಂಬರ್',
        'അടിയന്തര', 'ബന്ധപ്പെടുക', 'നമ്പർ',
    ]
    return any(k in query.lower() for k in keywords)
