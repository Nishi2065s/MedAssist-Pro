"""
Shared UI utilities — Common CSS and theme functions to avoid duplication.
Import this on every page instead of repeating CSS.
"""
import streamlit as st

# Compact global CSS — loaded once, cached by Streamlit
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');
*{font-family:'Inter',sans-serif}
.stApp{background:linear-gradient(135deg,#030712 0%,#0f172a 50%,#1e1b4b 100%)}
#MainMenu,header,footer{visibility:hidden}
.stDeployButton{display:none}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#020617,#0f172a);border-right:1px solid rgba(99,102,241,.12)}
.stButton>button{background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#fff!important;border:none!important;border-radius:12px!important;font-weight:600!important;transition:all .3s!important}
.stButton>button:hover{background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;box-shadow:0 8px 25px rgba(99,102,241,.3)!important;transform:translateY(-2px)!important}
[data-testid="stChatMessage"]{background:rgba(30,41,59,.45)!important;border:1px solid rgba(99,102,241,.06)!important;border-radius:16px!important;margin-bottom:.6rem!important}
[data-testid="stChatMessageContent"] p{color:#e2e8f0!important;line-height:1.7!important}
[data-testid="stChatInput"] textarea{background:rgba(30,41,59,.5)!important;border:1px solid rgba(99,102,241,.18)!important;border-radius:14px!important;color:#e2e8f0!important}
.page-hdr{text-align:center;padding:1rem 0 1.5rem}
.page-ttl{font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.page-sub{color:#64748b;font-size:.92rem;margin-top:6px}
</style>
"""


def apply_theme():
    """Apply the global theme CSS. Call this once at the top of each page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon, title, subtitle=""):
    """Render a consistent page header."""
    st.markdown(f"""
    <div class="page-hdr">
        <div class="page-ttl">{icon} {title}</div>
        <div class="page-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
