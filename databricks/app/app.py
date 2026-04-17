import streamlit as st
import time
import uuid
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI | Neural Command",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THE "DARK ELEGANCE" DESIGN SYSTEM ───────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono&display=swap');

    /* Global Dark Theme Overrides */
    :root {
        --bg-main: #0D0D0E;
        --bg-sidebar: #050505;
        --bg-card: #161618;
        --border: rgba(255, 255, 255, 0.08);
        --text-main: #E4E4E7;
        --text-muted: #A1A1AA;
        --accent: #C8A96E;
    }

    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar - Sleek Obsidian */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* Centered Chat Column */
    .chat-container {
        max-width: 850px;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 10rem;
    }

    /* Message Bubbles */
    .ai-row {
        margin-bottom: 2.5rem;
        padding-bottom: 2rem;
        border-bottom: 1px solid var(--border);
        animation: fadeIn 0.4s ease-out;
    }
    
    .user-row {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 2rem;
    }

    .user-bubble {
        background: #27272A;
        color: #FFFFFF;
        padding: 0.8rem 1.2rem;
        border-radius: 1.2rem 1.2rem 0.2rem 1.2rem;
        max-width: 80%;
        font-size: 0.95rem;
        border: 1px solid var(--border);
    }

    /* Minimalist File Uploader */
    [data-testid="stFileUploader"] {
        background-color: var(--bg-card);
        border: 1px dashed var(--border);
        border-radius: 12px;
        padding: 2rem;
    }

    /* Analysis Report Card */
    .report-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Sidebar Items */
    .history-card {
        padding: 0.7rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        font-size: 0.85rem;
        color: var(--text-muted);
        transition: all 0.2s;
        cursor: pointer;
    }
    .history-card:hover {
        background: #1A1A1B;
        color: white;
    }

    /* Input HUD */
    .stChatInputContainer {
        padding: 1.5rem 0 !important;
        background-color: var(--bg-main) !important;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE MOCK FETCH ─────────────────────────────────────────────────────
if "db_history" not in st.session_state:
    st.session_state.db_history = [
        {"id": "1", "title": "Service Master Audit", "date": "18 Apr"},
        {"id": "2", "title": "IP Clause Rewrite", "date": "17 Apr"}
    ]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-family:Inter; font-weight:700; color:white; margin-bottom:1.5rem;'>LexAI</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.active_file = None
        st.rerun()

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; font-weight:700; color:#555; letter-spacing:1px;'>HISTORY</p>", unsafe_allow_html=True)
    
    for chat in st.session_state.db_history:
        st.markdown(f"""
            <div class="history-card">
                <span style="color:#C8A96E; margin-right:8px;">📄</span> {chat['title']}
            </div>
        """, unsafe_allow_html=True)

# ─── MAIN CHAT AREA ──────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Start State
if not st.session_state.chat_history:
    st.markdown("""
        <div style="text-align: center; margin-top: 10vh; margin-bottom: 3rem;">
            <h1 style="font-size: 2.5rem; font-weight: 600; color: white;">Contract Command.</h1>
            <p style="color: #71717A; font-size: 1.1rem;">Upload a document to identify risk vectors and legal gaps.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Styled File Upload
    up = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
    if up:
        with st.status("Analyzing Legal Structure...", expanded=False):
            time.sleep(1.5)
            # DATABASE ACTION: Save new chat title
            st.session_state.db_history.insert(0, {"id": str(uuid.uuid4()), "title": up.name[:20], "date": "Today"})
            st.session_state.chat_history.append({"role": "user", "content": f"Audit {up.name}"})
            st.session_state.chat_history.append({
                "role": "ai", 
                "content": f"Analysis complete for **{up.name}**. I've identified **3 high-exposure** clauses in the Liability section.",
                "type": "report"
            })
            st.rerun()

# Message Stream
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-row"><div class="user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-row">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:JetBrains Mono; font-size:10px; color:#555; margin-bottom:0.8rem;">LEXAI ENGINE v.2.0</p>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        
        if msg.get("type") == "report":
            st.markdown("""
                <div class="report-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                        <span style="color:#FF4B4B; font-size:11px; font-weight:700;">CRITICAL RISK</span>
                        <span style="color:#555; font-size:11px; font-family:JetBrains Mono;">REF_ID: 8099</span>
                    </div>
                    <div style="font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;">Uncapped Indemnification</div>
                    <div style="color:#A1A1AA; font-size:0.9rem; line-height:1.5;">
                        Clause 12.1 places an unlimited liability burden for indirect claims. This should be capped at 100% of the annual contract value to meet industry standards.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── INPUT SYSTEM ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question or request a clause rewrite..."):
    # If starting fresh via text, add to DB
    if not st.session_state.chat_history:
        st.session_state.db_history.insert(0, {"id": str(uuid.uuid4()), "title": prompt[:15], "date": "Today"})
        
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        time.sleep(1)
        st.session_state.chat_history.append({
            "role": "ai", 
            "content": f"I've cross-referenced your request regarding **'{prompt}'**. I recommend adding a 'Force Majeure' carve-out to protect your delivery timelines during supply chain disruptions."
        })
    st.rerun()