import streamlit as st
import time
import uuid
import base64
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LEX-COMMAND | Quantum Legal HUD",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── THE "SMTNG CRAZY" DESIGN SYSTEM (HUD ELEGANCE) ──────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-deep: #050505;
        --glass: rgba(20, 20, 25, 0.7);
        --accent: #C8A96E;
        --accent-glow: rgba(200, 169, 110, 0.2);
        --border: rgba(255, 255, 255, 0.07);
        --text-dim: #88888E;
    }

    /* Full App HUD */
    .stApp {
        background-color: var(--bg-deep) !important;
        background-image: radial-gradient(circle at 50% -20%, #1A1A1D 0%, transparent 80%);
        color: #E4E4E7;
        font-family: 'Space Grotesk', sans-serif;
    }

    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* Glass Sidebar */
    [data-testid="stSidebar"] {
        background-color: #030303 !important;
        border-right: 1px solid var(--border);
    }

    /* Persistent Chat Box Layout */
    .chat-HUD {
        max-width: 900px;
        margin: 0 auto;
        padding-bottom: 150px;
    }

    /* AI HUD Message */
    .ai-bubble {
        border-left: 2px solid var(--accent);
        background: rgba(255, 255, 255, 0.02);
        padding: 24px;
        margin-bottom: 40px;
        border-radius: 4px 20px 20px 20px;
        backdrop-filter: blur(10px);
        animation: slideUp 0.5s ease-out;
    }

    /* User Message */
    .user-bubble {
        background: var(--accent);
        color: #000;
        font-weight: 600;
        padding: 12px 20px;
        border-radius: 20px 20px 4px 20px;
        max-width: 80%;
        margin-left: auto;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px var(--accent-glow);
    }

    /* HUD Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid var(--border);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        transition: 0.3s;
    }
    .metric-card:hover { border-color: var(--accent); background: rgba(200, 169, 110, 0.05); }

    /* The "Drop Zone" */
    [data-testid="stFileUploader"] {
        background-color: var(--glass) !important;
        border: 1px dashed var(--accent) !important;
        border-radius: 16px;
        padding: 30px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }

    @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE MOCK LAYER (DYNAMIC SYNC) ──────────────────────────────────────
if "db" not in st.session_state:
    st.session_state.db = [
        {"id": "a1", "name": "Employment_Contract_V1.pdf", "score": "88/100"},
        {"id": "a2", "name": "NDA_Final.docx", "score": "94/100"}
    ]

# ─── SIDEBAR: PERSISTENT HISTORY ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-weight:700; color:white; letter-spacing:-1px;'>LEX-HUD</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#555; margin-top:-15px;'>QUANTUM-LEGAL INTELLIGENCE</p>", unsafe_allow_html=True)
    
    if st.button("＋ INITIALIZE NEW SESSION", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; font-weight:700; color:#444; letter-spacing:1px;'>HISTORY_LOG</p>", unsafe_allow_html=True)
    
    for entry in st.session_state.db:
        st.markdown(f"""
            <div style="padding: 12px; border-radius: 8px; border: 1px solid #111; background: #080808; margin-bottom: 8px; cursor: pointer;">
                <div style="font-size: 12px; color: #eee; font-weight: 500;">📄 {entry['name']}</div>
                <div style="font-size: 9px; color: #C8A96E; font-family: 'JetBrains Mono';">RISK_SCORE: {entry['score']}</div>
            </div>
        """, unsafe_allow_html=True)

# ─── MAIN APP HUD ────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown('<div class="chat-HUD">', unsafe_allow_html=True)

# 1. Start State / Dashboard
if not st.session_state.chat_history:
    st.markdown("""
        <div style="text-align: center; margin-top: 10vh; margin-bottom: 3rem;">
            <h1 style="font-size: 3.5rem; font-weight: 700; color: white; letter-spacing: -2px;">System Ready.</h1>
            <p style="color: #666; font-size: 1.1rem; font-family: 'JetBrains Mono';">FEED CONTRACT DATA FOR NEURAL MAPPING</p>
        </div>
    """, unsafe_allow_html=True)
    
    # HUD Metrics (Faking a live dashboard)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="metric-card"><div style="font-size:10px; color:#444;">ENGINE</div><div style="color:#C8A96E; font-weight:600;">ACTIVE_V.3</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><div style="font-size:10px; color:#444;">LATENCY</div><div style="color:#C8A96E; font-weight:600;">24ms</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><div style="font-size:10px; color:#444;">DATABASE</div><div style="color:#C8A96E; font-weight:600;">SYNCED</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    # Styled File Upload
    up = st.file_uploader("Drop Contract", type=['pdf', 'docx'], label_visibility="collapsed")
    if up:
        with st.status("Performing Multi-Vector Audit...", expanded=True) as status:
            time.sleep(1.2)
            st.write("Cross-referencing global precedents...")
            time.sleep(1)
            st.write("Extracting liability anchors...")
            # DATABASE ACTION: New Entry
            st.session_state.db.insert(0, {"id": str(uuid.uuid4()), "name": up.name, "score": "AUDITING..."})
            st.session_state.chat_history.append({"role": "user", "content": f"Analyze {up.name}"})
            st.session_state.chat_history.append({"role": "ai", "content": f"**Audit Complete.** Analysis of **{up.name}** reveals critical exposure in **Clause 14 (Indemnity)**. You are currently agreeing to a 100% uncapped liability window."})
            st.rerun()

# 2. Chat Feed
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-bubble">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:JetBrains Mono; font-size:10px; color:#444; margin-bottom:10px;">LEX-COMMAND > OUTPUT_STREAM</p>', unsafe_allow_html=True)
        st.write(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── INPUT SYSTEM (THE COMMAND BAR) ──────────────────────────────────────────
if prompt := st.chat_input("Input command or request rewrite..."):
    # If starting fresh via text
    if not st.session_state.chat_history:
        st.session_state.db.insert(0, {"id": str(uuid.uuid4()), "name": prompt[:15], "score": "GENERAL"})
        
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.spinner("Processing vector..."):
        time.sleep(1)
        response = f"Scanning requested vector: **'{prompt}'**. Based on the current draft, this change would reduce your liability score by **12.4%**. Shall I draft the counter-clause for your review?"
        st.session_state.chat_history.append({"role": "ai", "content": response})
    st.rerun()

# ─── HUD STATUS BAR (BOTTOM) ──────────────────────────────────────────────────
st.markdown("""
    <div style="position: fixed; bottom: 10px; left: 300px; right: 20px; display: flex; justify-content: space-between; font-family: 'JetBrains Mono'; font-size: 10px; color: #222; pointer-events: none;">
        <div>SYSTEM_STATUS: ENCRYPTED</div>
        <div>JURISDICTION: GLOBAL_MAP_v2</div>
    </div>
""", unsafe_allow_html=True)