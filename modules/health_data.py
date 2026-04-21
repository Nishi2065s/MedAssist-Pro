"""
Health Data — Loader for diseases, medicines, health tips, and hospitals databases.
"""
import json
import os
import streamlit as st
from config.settings import DISEASES_DB_FILE, MEDICINES_DB_FILE, HEALTH_TIPS_FILE


@st.cache_data
def load_diseases_db():
    """Load the diseases database."""
    try:
        if os.path.exists(DISEASES_DB_FILE):
            with open(DISEASES_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


@st.cache_data
def load_medicines_db():
    """Load the medicines reference database."""
    try:
        if os.path.exists(MEDICINES_DB_FILE):
            with open(MEDICINES_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


@st.cache_data
def load_health_tips():
    """Load daily health tips."""
    try:
        if os.path.exists(HEALTH_TIPS_FILE):
            with open(HEALTH_TIPS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def search_diseases(query, diseases_db):
    """Search diseases database by symptom or disease name."""
    results = []
    query_lower = query.lower()

    for disease_name, info in diseases_db.items():
        # Match by disease name
        if query_lower in disease_name.lower():
            results.append({"name": disease_name, "match_type": "name", **info})
            continue

        # Match by symptoms
        symptoms = info.get("symptoms", [])
        matched_symptoms = [s for s in symptoms if query_lower in s.lower()]
        if matched_symptoms:
            results.append({
                "name": disease_name,
                "match_type": "symptom",
                "matched": matched_symptoms,
                **info
            })

    return results


def search_medicines(query, medicines_db):
    """Search medicines database by name or condition."""
    results = []
    query_lower = query.lower()

    for med_name, info in medicines_db.items():
        if query_lower in med_name.lower():
            results.append({"name": med_name, "match_type": "name", **info})
            continue

        uses = info.get("uses", [])
        if any(query_lower in use.lower() for use in uses):
            results.append({"name": med_name, "match_type": "use", **info})

    return results
