import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(
    page_title="Glow Studio | AI Booking",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --cream: #FAF7F2;
    --blush: #E8C4B8;
    --rose: #C4736A;
    --charcoal: #2C2C2C;
    --muted: #8A7F7A;
    --gold: #BFA07A;
    --white: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream);
    color: var(--charcoal);
}

h1, h2, h3 { font-family: 'Cormorant Garamond', serif; }

section[data-testid="stSidebar"] {
    background: var(--charcoal) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--cream) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: var(--cream) !important;
}

.stButton > button {
    background: var(--charcoal);
    color: var(--cream);
    border: none;
    border-radius: 2px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.6rem 1.5rem;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: var(--rose);
    color: white;
}

.stChatMessage {
    background: white !important;
    border-radius: 4px !important;
    border: 1px solid #EDE8E3 !important;
}

div[data-testid="stChatInput"] textarea {
    border: 1px solid var(--blush) !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    background: white !important;
}

.stFileUploader {
    border: 1px dashed var(--blush) !important;
    border-radius: 4px !important;
    background: white !important;
}

.stDataFrame { border-radius: 4px; }

.metric-card {
    background: white;
    border: 1px solid #EDE8E3;
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-card .number {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    color: var(--rose);
    line-height: 1;
}
.metric-card .label {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

from app.chat_logic import chat_page
from app.admin_dashboard import admin_page

with st.sidebar:
    st.markdown("""
    <div style='padding: 1.5rem 0 2rem 0; text-align: center;'>
        <div style='font-family: Cormorant Garamond, serif; font-size: 1.8rem; color: #FAF7F2; letter-spacing: 0.05em;'>✨ Glow Studio</div>
        <div style='font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #BFA07A; margin-top: 0.3rem;'>Salon & Spa</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["💬 Book / Chat", "🛠 Admin Dashboard"], index=0)
    
    st.markdown("<div style='margin-top: 2rem; border-top: 1px solid #3C3C3C; padding-top: 1rem;'></div>", unsafe_allow_html=True)
    
    if page == "💬 Book / Chat":
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.booking_state = {}
            st.rerun()
        
        st.markdown("""
        <div style='margin-top: 2rem; font-size: 0.72rem; color: #8A7F7A; line-height: 1.8;'>
        📎 Upload a PDF to ask questions about services, pricing, or policies.<br><br>
        📅 Say <em>"I'd like to book"</em> to start a reservation.
        </div>
        """, unsafe_allow_html=True)

if page == "💬 Book / Chat":
    chat_page()
else:
    admin_page()
