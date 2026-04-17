import streamlit as st
import time
import uuid
import pandas as pd
# import databricks.sql as dbsql # Production DB connection

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI Terminal",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── THE PRODUCTION DESIGN SYSTEM (DEEP OBSIDIAN) ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=JetBrains+Mono&display=swap');

:root {
    --bg-main: #0A0A0B;
    --sidebar-bg: #050506;
    --accent: #D4AF6A;
    --border: rgba(255, 255, 255, 0.07);
    --text-muted: #71717A;
}

.stApp {
    background-color: var(--bg-main) !important;
    color: #E4E4E7;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Sidebar - The Persistent Control Center */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border);
}

/* Permanent Upload Area in Sidebar */
.sidebar-upload-container {
    background: rgba(255,255,255,0.02);
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 20px;
    text-align: center;
}

/* Chat Layout (GPT Style) */
.chat-wrapper {
    max-width: 850px;
    margin: 0 auto;
    padding-top: 2rem;
}

.message-row {
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
    animation: slideUp 0.4s ease-out;
}

.user-bubble {
    background: #1C1C1E;
    padding: 12px 20px;
    border-radius: 18px 18px 2px 18px;
    max-width: 85%;
    margin-left: auto;
    margin-bottom: 2rem;
    border: 1px solid var(--border);
    font-size: 15px;
}

/* Status Badges */
.engine-tag {
    font-family: 'JetBrains Mono';
    font-size: 10px;
    color: var(--accent);
    letter-spacing: 1px;
    margin-bottom: 10px;
}

@keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

/* Hide Streamlit elements */
header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE INTERFACE (SQL INTEGRATION) ────────────────────────────────────
def fetch_user_history():
    """SQL: SELECT session_id, title FROM chat_sessions ORDER BY created_at DESC"""
    # This is where you would call your Databricks/SQL Warehouse
    return [{"id": "1", "title": "Employment Contract Audit"}, {"id": "2", "title": "Lease Agreement Review"}]

def save_to_sql(session_id, role, content, file_name=None):
    """SQL: INSERT INTO messages (session_id, role, content, file_ref) VALUES (...)"""
    # Logic to commit chat to database
    pass

# ─── SIDEBAR: PERMANENT UPLOAD & HISTORY ─────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-weight:700; color:white;'>LexAI</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # PERMANENT UPLOAD OPTION
    st.markdown("<p style='font-size:11px; font-weight:600; color:#555;'>PERMANENT UPLOAD STREAM</p>", unsafe_allow_html=True)
    with st.container():
        uploaded_file = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"Active: {uploaded_file.name}")
            # CALL: Process file with ML model and save reference to SQL
    
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    
    # DB FETCHED HISTORY
    st.markdown("<p style='font-size:11px; font-weight:600; color:#555;'>HISTORY ARCHIVE</p>", unsafe_allow_html=True)
    history = fetch_user_history()
    for item in history:
        st.markdown(f"""
            <div style="padding: 10px; border-radius: 8px; font-size: 13px; color: #888; cursor: pointer; border: 1px solid transparent;" 
                 onmouseover="this.style.background='#111'; this.style.borderColor='rgba(255,255,255,0.1)';" 
                 onmouseout="this.style.background='transparent'; this.style.borderColor='transparent';">
                📄 {item['title']}
            </div>
        """, unsafe_allow_html=True)

# ─── MAIN CHAT AREA ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# Welcome State
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; margin-top: 15vh; opacity: 0.5;">
            <h1 style="font-size: 50px;">⚖️</h1>
            <p style="font-size: 18px;">Upload a contract in the sidebar or ask a question to begin.</p>
        </div>
    """, unsafe_allow_html=True)

# Chat Feed
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="message-row">', unsafe_allow_html=True)
        st.markdown('<div class="engine-tag">LEX-ENGINE ALPHA v1.0</div>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── PERSISTENT INPUT ────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask LexAI to rewrite a clause or audit a risk..."):
    # 1. Save User Query to Session + SQL
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_sql(st.session_state.session_id, "user", prompt)
    
    # 2. Run ML Inference (Dummy timer for smooth feel)
    with st.spinner("Processing legal vectors..."):
        time.sleep(1)
        response = "I've reviewed the requested section. Given the current jurisdiction, this language is **standard but restrictive**. Recommend pushing for a 'Mutual' termination clause to balance the leverage."
        
        # 3. Save AI Response to Session + SQL
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_to_sql(st.session_state.session_id, "assistant", response)
    
    st.rerun()