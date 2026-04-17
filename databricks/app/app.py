import streamlit as st
import time
import uuid
import pandas as pd
# import databricks.sql as dbsql # Real DB connection

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClauseBreaker AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# PRODUCTION DESIGN SYSTEM (CSS)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono&display=swap');

/* Global Reset */
:root {
    --bg-deep: #080809;
    --glass-bg: rgba(255, 255, 255, 0.03);
    --border: rgba(255, 255, 255, 0.08);
    --accent: #D4AF37; /* Burnished Gold */
    --accent-glow: rgba(212, 175, 55, 0.15);
    --text-dim: #8B8B92;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, #151518 0%, var(--bg-deep) 100%);
    color: #F4F4F5;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hide Streamlit Chrome */
header, footer, [data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding: 2rem 3rem !important; }

/* Dashboard HUD Layout */
.hud-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 32px;
    height: 85vh;
    position: sticky;
    top: 2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

/* Chat Bubbles */
.chat-ai-row {
    margin-bottom: 2rem;
    padding: 24px;
    background: rgba(255,255,255,0.02);
    border-left: 3px solid var(--accent);
    border-radius: 4px 20px 20px 20px;
    line-height: 1.6;
    animation: fadeIn 0.4s ease-out;
}

.chat-user-row {
    background: #1C1C1E;
    color: #FFFFFF;
    padding: 14px 22px;
    border-radius: 20px 20px 4px 20px;
    margin-left: 20%;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    font-size: 0.95rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Metadata Fonts */
.meta-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Risk Metrics */
.risk-gauge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 36px;
    font-weight: 700;
    color: var(--accent);
    text-shadow: 0 0 15px var(--accent-glow);
}

/* Styled Uploader */
[data-testid="stFileUploader"] {
    background: #000;
    border-radius: 12px;
    padding: 10px;
}

/* Input Area Fixed Bottom */
.stChatInputContainer {
    padding: 1.5rem 0 !important;
    background: var(--bg-deep) !important;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# BACKEND INTEGRATION (REAL SQL PLACEHOLDERS)
# ─────────────────────────────────────────────────────────────
def fetch_history_from_db():
    # query = "SELECT title, risk_score FROM contract_sessions ORDER BY created_at DESC LIMIT 5"
    # return pd.read_sql(query, db_connection)
    return [{"name": "Master Services v2", "score": "84%"}, {"name": "NDA Template", "score": "12%"}]

def log_message_to_db(role, content):
    # session_id = st.session_state.session_id
    # execute("INSERT INTO logs (session_id, role, content) VALUES (%s, %s, %s)", ...)
    pass

# ─────────────────────────────────────────────────────────────
# UI ARCHITECTURE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Using columns for the industry "HUD" look
col_hud, col_terminal = st.columns([1, 1.8], gap="large")

with col_hud:
    st.markdown('<div class="hud-panel">', unsafe_allow_html=True)
    st.markdown('<div class="meta-label">CORE SYSTEMS ACTIVE</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='margin-top:0; font-weight:700; color:#fff;'>ClauseBreaker</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    
    # File Management
    st.markdown('<div class="meta-label">DOCUMENT FEED</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Contract Upload", type=["pdf", "docx"], label_visibility="collapsed")
    
    if uploaded_file:
        st.info(f"Loaded: {uploaded_file.name}")
        # Logic here: OCR/Extract text and store in session state
    
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

    # Real-time Metrics
    st.markdown('<div class="meta-label">AUDIT SCORE</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="risk-gauge">84%</div>', unsafe_allow_html=True)
        st.caption("Risk Probability")
    with c2:
        st.markdown('<div class="risk-gauge">12</div>', unsafe_allow_html=True)
        st.caption("Active Flags")

    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)

    # Database History
    st.markdown('<div class="meta-label">PREVIOUS AUDITS</div>', unsafe_allow_html=True)
    history = fetch_history_from_db()
    for item in history:
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); padding:10px 15px; border-radius:8px; border:1px solid var(--border); margin-bottom:8px; font-size:12px;">
                <span style="color:var(--accent); font-family:JetBrains Mono;">{item['score']}</span> 
                <span style="margin-left:10px; color:#A1A1AA;">{item['name']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_terminal:
    st.markdown('<div class="meta-label">AI COMMAND TERMINAL</div>', unsafe_allow_html=True)
    
    # Chat Height-Adjusted Container
    terminal_container = st.container(height=620, border=False)

    with terminal_container:
        if not st.session_state.messages:
            st.markdown("""
                <div style="text-align:center; padding-top:150px; opacity:0.1;">
                    <h1 style="font-size:80px;">⚖️</h1>
                    <p>Terminal Ready for Document Stream</p>
                </div>
            """, unsafe_allow_html=True)
        
        for m in st.session_state.messages:
            if m["role"] == "user":
                st.markdown(f'<div class="chat-user-row">{m["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-ai-row">
                        <div class="meta-label">ANALYSIS OUTPUT</div>
                        {m["content"]}
                    </div>
                """, unsafe_allow_html=True)

    # Persistent Input Bar
    if prompt := st.chat_input("Enter legal query or scan command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        log_message_to_db("user", prompt)
        
        with st.spinner("Executing Inference..."):
            time.sleep(1.2)
            # This is where your actual ML call goes
            response = """
The **Indemnification** section (Clause 4.2) is critically unbalanced. 

- **Issue:** One-sided defense obligation for third-party claims.
- **Precedent:** Typical MSA standards require mutual carve-outs.
- **Action:** Request a liability cap equivalent to 12 months of service fees.
"""
            st.session_state.messages.append({"role": "assistant", "content": response})
            log_message_to_db("assistant", response)
            st.rerun()