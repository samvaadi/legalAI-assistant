import streamlit as st
import uuid
import time
import pandas as pd
# from databricks import sql # To connect to your SQL Warehouse

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="LexAI HUD", layout="wide", initial_sidebar_state="expanded")

# ─── HIGH-DENSITY CSS (HUD THEME) ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #080808;
    --sidebar: #030303;
    --accent: #d4af6a;
    --border: rgba(255,255,255,0.05);
}

.stApp { background-color: var(--bg); color: #d1d1d6; font-family: 'Inter', sans-serif; }
header, footer { visibility: hidden; }

/* Sidebar Density */
[data-testid="stSidebar"] {
    background-color: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}

/* Chat Density */
.chat-container {
    max-width: 1000px;
    margin: 0 auto;
}

.ai-row {
    border-bottom: 1px solid var(--border);
    padding: 1.5rem 0;
    font-size: 14px;
    line-height: 1.5;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 1.5rem 0;
}

.user-bubble {
    background: #1a1a1c;
    border: 1px solid var(--border);
    padding: 10px 16px;
    border-radius: 12px 12px 2px 12px;
    font-size: 14px;
    max-width: 80%;
}

/* Metadata Labels */
.meta {
    font-family: 'JetBrains Mono';
    font-size: 9px;
    color: #444;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

/* Sidebar History Items */
.history-item {
    font-size: 12px;
    padding: 6px 10px;
    color: #888;
    border-radius: 4px;
    cursor: pointer;
}
.history-item:hover { background: #111; color: var(--accent); }

/* Compact Input */
.stChatInputContainer { padding: 1rem 0 !important; background: var(--bg) !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATABRICKS SQL LOGIC ────────────────────────────────────────────────────
# Replace with your actual Databricks Workspace details
def get_sql_history():
    """
    SQL: SELECT session_id, title FROM bronze.lex_chat_history 
    ORDER BY created_at DESC
    """
    # dummy for UI render
    return [{"id": "a", "title": "Service_Agreement_v4.pdf"}, {"id": "b", "title": "NDA_Clause_Audit"}]

def save_to_databricks(session_id, role, content):
    """
    SQL: INSERT INTO gold.lex_chat_logs (session_id, role, content, ts) 
    VALUES ('{}', '{}', '{}', CURRENT_TIMESTAMP)
    """
    pass

# ─── SIDEBAR HUD ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='font-family:JetBrains Mono; color:white;'>LEX-HUD</h3>", unsafe_allow_html=True)
    
    if st.button("＋ INIT_NEW_SESSION", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # PERMANENT COMPACT UPLOADER
    st.markdown("<div class='meta'>FILE_INPUT_STREAM</div>", unsafe_allow_html=True)
    up = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
    if up: st.caption(f"SYNCED: {up.name}")

    st.markdown("<br><div class='meta'>DATABASE_ARCHIVE</div>", unsafe_allow_html=True)
    history = get_sql_history()
    for item in history:
        st.markdown(f"<div class='history-item'>📄 {item['title']}</div>", unsafe_allow_html=True)

# ─── MAIN TERMINAL ───────────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "sid" not in st.session_state: st.session_state.sid = str(uuid.uuid4())

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="user-row"><div class="user-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-row"><div class="meta">SYSTEM_OUTPUT // NEURAL_AUDIT</div>{m["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── COMMAND INPUT ───────────────────────────────────────────────────────────
if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_databricks(st.session_state.sid, "user", prompt) # REAL SQL CALL
    
    with st.spinner("Processing..."):
        time.sleep(0.5)
        response = "Audit complete. **Section 4.1 (Liability)** detected as High Risk. No mutual carve-out found."
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_to_databricks(st.session_state.sid, "assistant", response) # REAL SQL CALL
    st.rerun()