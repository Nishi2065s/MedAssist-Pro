"""
Page 4: Medicine Information Lookup — Drug reference with Indian brand names
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import APP_NAME
from modules.health_data import load_medicines_db, search_medicines

# --- Page Config ---
st.set_page_config(page_title=f"Medicine Info — {APP_NAME}", page_icon="💊", layout="wide")

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
    
    .page-header { text-align: center; padding: 1rem 0 2rem; }
    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-subtitle { color: #64748b; font-size: 0.95rem; margin-top: 6px; }
    
    /* Medicine Card */
    .med-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: all 0.3s;
    }
    .med-card:hover {
        border-color: rgba(99, 102, 241, 0.25);
        transform: translateY(-2px);
    }
    .med-name {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .med-generic { color: #a78bfa; font-size: 0.85rem; font-weight: 500; margin-top: 2px; }
    .med-category {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a78bfa;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .med-otc {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-left: 6px;
    }
    .med-section-title { color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin: 1rem 0 0.5rem; }
    .med-content { color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; }
    .med-brand { color: #6ee7b7; }
    .med-warning { color: #fbbf24; }
    .med-price { color: #a78bfa; font-weight: 600; font-size: 1rem; }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white; border: none; border-radius: 10px; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="page-header">
    <div class="page-title">💊 Medicine Reference Guide</div>
    <div class="page-subtitle">Search medicines, check dosages, find generic alternatives & Indian brand names</div>
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
medicines_db = load_medicines_db()

# --- Safety Warning ---
st.markdown("""
<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
    <span style="color: #f87171; font-weight: 600;">⚠️ Important:</span>
    <span style="color: #fca5a5; font-size: 0.9rem;"> This is a reference guide only. Never self-medicate. Always consult a doctor before taking any medication, especially antibiotics and prescription drugs.</span>
</div>
""", unsafe_allow_html=True)

# --- Search ---
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "🔍 Search medicines or conditions",
        placeholder="e.g., paracetamol, fever, headache, acidity...",
        key="med_search"
    )
with col2:
    search_mode = st.selectbox("Search by", ["Medicine Name", "Condition/Use"], key="search_mode")

if medicines_db:
    if search_query:
        results = search_medicines(search_query, medicines_db)

        if results:
            st.markdown(f"### 🔍 Found {len(results)} result(s)")

            for med in results:
                otc = med.get('otc', True)
                otc_style = 'background: rgba(72, 187, 120, 0.15); color: #48bb78;' if otc else 'background: rgba(239, 68, 68, 0.15); color: #f87171;'
                otc_text = "OTC" if otc else "Rx ONLY"

                brand_names = ", ".join(med.get('brand_names', []))
                uses = ", ".join(med.get('uses', []))
                side_effects = ", ".join(med.get('side_effects', []))
                precautions = ", ".join(med.get('precautions', []))

                st.markdown(f"""
                <div class="med-card">
                    <div class="med-name">{med['name']}</div>
                    <div class="med-generic">Generic: {med.get('generic_name', 'N/A')}</div>
                    <span class="med-category">{med.get('category', 'General')}</span>
                    <span class="med-otc" style="{otc_style}">{otc_text}</span>
                    
                    <div class="med-section-title">🏷️ Indian Brand Names</div>
                    <div class="med-content med-brand">{brand_names}</div>
                    
                    <div class="med-section-title">💊 Uses</div>
                    <div class="med-content">{uses}</div>
                    
                    <div class="med-section-title">📏 Recommended Dosage</div>
                    <div class="med-content">{med.get('dosage', 'Consult doctor')}</div>
                    
                    <div class="med-section-title">⚡ Side Effects</div>
                    <div class="med-content med-warning">{side_effects}</div>
                    
                    <div class="med-section-title">⚠️ Precautions</div>
                    <div class="med-content">{precautions}</div>
                    
                    <div class="med-section-title">💰 Price Range</div>
                    <div class="med-price">{med.get('price_range', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 No medicines found matching your search. Try a different term.")
    else:
        # Show all medicines as browsable list
        st.markdown("### 📋 All Available Medicines")
        st.caption(f"📚 {len(medicines_db)} medicines in database")

        for med_name, med_info in medicines_db.items():
            otc = med_info.get('otc', True)
            otc_icon = "🟢" if otc else "🔴"
            brands = ", ".join(med_info.get('brand_names', [])[:3])

            with st.expander(f"{otc_icon} **{med_name}** — {med_info.get('category', '')} | Brands: {brands}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Generic Name:** {med_info.get('generic_name', 'N/A')}")
                    st.markdown(f"**Category:** {med_info.get('category', 'N/A')}")
                    st.markdown(f"**Brand Names:** {', '.join(med_info.get('brand_names', []))}")
                    st.markdown(f"**Uses:** {', '.join(med_info.get('uses', []))}")
                    st.markdown(f"**Price:** {med_info.get('price_range', 'N/A')}")
                with col2:
                    st.markdown(f"**Dosage:** {med_info.get('dosage', 'Consult doctor')}")
                    st.markdown(f"**Side Effects:** {', '.join(med_info.get('side_effects', []))}")
                    st.markdown(f"**Precautions:** {', '.join(med_info.get('precautions', []))}")
                    st.markdown(f"**OTC Available:** {'✅ Yes' if otc else '❌ Prescription Required'}")
else:
    st.warning("⚠️ Medicine database not found. Ensure `data/medicines_reference.json` exists.")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #475569; font-size: 0.8rem; padding: 1rem;">
    ⚠️ Medicine information is for reference only. Always follow your doctor's prescription.<br>
    Never self-medicate with antibiotics or prescription drugs.
</div>
""", unsafe_allow_html=True)
