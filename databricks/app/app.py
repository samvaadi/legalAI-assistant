import streamlit as st
import uuid
import time
import pandas as pd
# from databricks import sql # Production Connector

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI Terminal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SOBER MINIMALIST DESIGN SYSTEM ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Code+Pro&display=swap');

/* Main Colors */
:root {
    --bg-main: #0E0E10;
    --sidebar-bg: #050505;
    --text-primary: #E4E4E7;
    --text-muted: #71717A;
    --border: rgba(255, 255, 255, 0.1);
    --accent: #D4AF6A;
}

.stApp {
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

/* Sidebar - Clean Slate */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border);
}

/* Chat Layout - GPT Centered Flow */
.chat-container {
    max-width: 850px;
    margin: 0 auto;
    padding-bottom: 150px;
}

.ai-message {
    padding: 24px 0;
    border-bottom: 1px solid var(--border);
    line-height: 1.6;
    font-size: 15px;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 24px 0;
}

.user-bubble {
    background: #27272A;
    padding: 12px 20px;
    border-radius: 18px 18px 2px 18px;
    font-size: 15px;
    max-width: 80%;
    color: white;
}

/* History Items */
.history-item {
    padding: 8px 12px;
    font-size: 13px;
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    transition: 0.2s;
}
.history-item:hover {
    background: #18181B;
    color: white;
}

/* Fix Streamlit Header & Inputs */
header, footer { visibility: hidden; }
.stChatInputContainer {
    background-color: var(--bg-main) !important;
    padding-bottom: 30px !important;
}

/* Clean Labels */
.label-sm {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

# ─── DATABRICKS SQL INTEGRATION ──────────────────────────────────────────────
def fetch_history_from_databricks():
    """
    SQL Call to Databricks SQL Warehouse.
    SELECT session_id, title FROM gold.lex_chat_history ORDER BY created_at DESC
    """
    # Placeholder for the UI loop
    return [{"id": "1", "title": "MSA_Agreement_V4"}, {"id": "2", "title": "Indemnity_Rewrite"}]

def save_message_to_databricks(session_id, role, content):
    """
    INSERT INTO gold.lex_chat_history (session_id, role, content, created_at)
    VALUES ('{}', '{}', '{}', CURRENT_TIMESTAMP())
    """
    pass

# ─── SIDEBAR HUD ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='font-weight:600; padding-bottom: 10px;'>LexAI</h3>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # PERMANENT MINIMAL UPLOADER
    st.markdown('<div class="label-sm">Document Input</div>', unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
    if up: st.caption(f"✓ {up.name}")

    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    
    # HISTORY FROM SQL
    st.markdown('<div class="label-sm">History</div>', unsafe_allow_html=True)
    history = fetch_history_from_databricks()
    for chat in history:
        st.markdown(f'<div class="history-item">📄 {chat["title"]}</div>', unsafe_allow_html=True)

# ─── MAIN CONVERSATION ───────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "sid" not in st.session_state: st.session_state.sid = str(uuid.uuid4())

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Render Messages
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="user-row"><div class="user-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-message"><b>LexAI</b><br><br>{m["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── INPUT LOGIC ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about the contract..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message_to_databricks(st.session_state.sid, "user", prompt)
    
    with st.spinner("Analyzing..."):
        time.sleep(0.8) # Real ML model inference happens here
        response = "I've reviewed the **Liability** section. It currently lacks a cap for indirect damages. Recommendation: Add a cap equal to 100% of the contract value."
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message_to_databricks(st.session_state.sid, "assistant", response)
        
    st.rerun()