import streamlit as st
import time
import uuid
import pandas as pd
# from sqlalchemy import create_engine # For real SQL integration

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI Terminal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# THE "ELITE" DESIGN SYSTEM (DARK SLATE & CHAMPAGNE)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono&display=swap');

/* Global Reset */
:root {
    --bg-color: #0D0D0F;
    --sidebar-bg: #050505;
    --card-bg: #161618;
    --border-color: rgba(255, 255, 255, 0.08);
    --accent-color: #D4AF6A;
    --text-muted: #71717A;
}

.stApp {
    background-color: var(--bg-color);
    color: #E4E4E7;
    font-family: 'Inter', sans-serif;
}

/* Sidebar History Styling */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-color);
}

.history-pill {
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 4px;
    font-size: 13px;
    color: #A1A1AA;
    cursor: pointer;
    transition: all 0.2s;
}
.history-pill:hover {
    background: #1A1A1C;
    color: white;
}

/* Chat Layout Architecture */
.chat-wrapper {
    max-width: 850px;
    margin: 0 auto;
    padding-top: 20px;
}

/* Chat Bubbles */
.ai-bubble {
    padding: 24px;
    margin-bottom: 30px;
    border-bottom: 1px solid var(--border-color);
    line-height: 1.65;
    font-size: 16px;
    animation: fadeIn 0.4s ease-out;
}

.user-bubble {
    background-color: #27272A;
    padding: 12px 20px;
    border-radius: 18px 18px 2px 18px;
    max-width: 85%;
    margin-left: auto;
    margin-bottom: 30px;
    font-size: 15px;
    border: 1px solid var(--border-color);
}

/* The File Chip (Inside Chat) */
.file-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(212, 175, 106, 0.1);
    border: 1px solid var(--accent-color);
    padding: 6px 14px;
    border-radius: 10px;
    color: var(--accent-color);
    font-size: 12px;
    font-family: 'JetBrains Mono';
    margin-bottom: 15px;
}

/* Input Bar Fix */
.stChatInputContainer {
    background-color: var(--bg-color) !important;
    border-top: 1px solid var(--border-color) !important;
    padding-bottom: 30px !important;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Hide Streamlit Header/Footer */
header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# REAL SQL INTEGRATION BLUEPRINT
# ─────────────────────────────────────────────────────────────
def fetch_conversations():
    # Replace with: pd.read_sql("SELECT session_id, title FROM chats", engine)
    return [{"id": "1", "title": "MSA Risk Analysis"}, {"id": "2", "title": "Vendor Indemnity Audit"}]

def commit_to_sql(session_id, role, content):
    # execute("INSERT INTO chat_log (session_id, role, content) VALUES (%s, %s, %s)", (session_id, role, content))
    pass

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-weight:600; letter-spacing:-1px;'>LexAI</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.active_file = None
        st.rerun()
    
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#555; font-weight:700; letter-spacing:1px;'>CONVERSATIONS</p>", unsafe_allow_html=True)
    
    # Real DB Fetch
    history = fetch_conversations()
    for item in history:
        st.markdown(f'<div class="history-pill">📄 {item["title"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN CHAT TERMINAL
# ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# 1. Empty State (Logo + Uploader)
if not st.session_state.chat_history:
    st.markdown("""
        <div style="text-align: center; margin-top: 15vh; margin-bottom: 40px;">
            <h1 style="font-size: 42px; font-weight: 600; color: white;">How can I help you today?</h1>
            <p style="color: #71717A; font-size: 18px;">Upload a contract or ask a legal question to begin.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Elegant Integrated Uploader
    up_col, _ = st.columns([1, 0.01]) # Just for centering
    with up_col:
        uploaded_file = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
        if uploaded_file:
            st.session_state.active_file = uploaded_file.name
            with st.status("Analyzing document structure..."):
                time.sleep(1.2)
                st.session_state.chat_history.append({"role": "user", "content": f"Analyze {uploaded_file.name}", "file": uploaded_file.name})
                st.session_state.chat_history.append({
                    "role": "ai", 
                    "content": f"I've completed the neural audit of **{uploaded_file.name}**. I found **2 high-risk factors** in the Indemnification clause (Section 8.2). Would you like a breakdown?",
                    "type": "report"
                })
                commit_to_sql(st.session_state.session_id, "ai", "Analysis complete...")
            st.rerun()

# 2. Chat Feed
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        # Show file chip if it was a file upload message
        file_html = f'<div class="file-chip">📎 {msg["file"]}</div>' if "file" in msg else ""
        st.markdown(f'<div class="user-bubble">{file_html}{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-bubble">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:JetBrains Mono; font-size:10px; color:#555; margin-bottom:12px;">LEXAI CORE v.1.0</p>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 3. Persistent Input Bar
if prompt := st.chat_input("Ask about specific clauses or request a rewrite..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    commit_to_sql(st.session_state.session_id, "user", prompt)
    
    with st.spinner("Processing..."):
        time.sleep(1)
        response = "I've reviewed Clause 4. Under most jurisdictions, this 'Best Efforts' standard is interpreted as a high bar. I recommend changing it to 'Reasonable Commercial Efforts' to reduce your liability."
        st.session_state.chat_history.append({"role": "ai", "content": response})
        commit_to_sql(st.session_state.session_id, "ai", response)
    st.rerun()