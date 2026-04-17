import streamlit as st
import time
import uuid
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI | Legal Intel",
    page_icon="⚖️",
    layout="wide",
)

# ─── THE "CLAUDE SOBER" DESIGN SYSTEM ────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

    :root {
        --bg-color: #F9F8F6;
        --sidebar-color: #F3F2EE;
        --text-main: #1A1A1A;
        --text-muted: #656565;
        --border-color: #E5E3DA;
        --accent: #D97757;
    }

    .stApp { background-color: var(--bg-color); color: var(--text-main); font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Sidebar - Navigation & History */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-color) !important;
        border-right: 1px solid var(--border-color);
        padding: 20px 10px;
    }

    /* Conversation History Items */
    .history-item {
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 5px;
        font-size: 13.5px;
        color: var(--text-main);
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .history-item:hover {
        background: #EAE8E0;
        border-color: var(--border-color);
    }
    .history-item.active {
        background: #EAE8E0;
        font-weight: 500;
        border-color: var(--border-color);
    }

    /* Main Chat Area */
    .main-chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding-bottom: 150px;
    }

    /* Chat Bubbles */
    .ai-message {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 40px;
        padding-bottom: 20px;
        border-bottom: 1px solid var(--border-color);
    }
    .user-message {
        background: #F0EDE4;
        padding: 12px 20px;
        border-radius: 15px;
        display: inline-block;
        margin-bottom: 30px;
        align-self: flex-end;
        max-width: 85%;
        font-size: 15px;
    }

    /* File Chip */
    .file-chip {
        display: inline-flex;
        align-items: center;
        background: white;
        border: 1px solid var(--border-color);
        padding: 8px 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        font-size: 13px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px !important;
        background: white !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-main) !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE LAYER (MOCK) ───────────────────────────────────────────────────
# In a real app, replace these with: 
# conn = sqlite3.connect('lex.db') or your SQL Alchemy logic
def fetch_conversations():
    """Fetch all chat sessions from DB"""
    if "db_mock" not in st.session_state:
        st.session_state.db_mock = [
            {"id": "1", "title": "Service Agreement Analysis", "timestamp": "2026-04-15"},
            {"id": "2", "title": "NDA Review", "timestamp": "2026-04-16"}
        ]
    return st.session_state.db_mock

def save_new_conversation(title):
    """Save a new chat session to DB"""
    new_id = str(uuid.uuid4())
    new_entry = {
        "id": new_id,
        "title": title[:30] + "...",
        "timestamp": datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.db_mock.insert(0, new_entry)
    return new_id

# ─── SESSION STATE MANAGEMENT ───────────────────────────────────────────────
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# ─── SIDEBAR: DB FETCH & NEW CHAT ────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-family:Source Serif 4; margin-bottom:20px;'>LexAI</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_chat_id = None
        st.session_state.chat_history = []
        st.session_state.uploaded_filename = None
        st.rerun()

    st.markdown("<br><div style='font-size: 11px; font-weight: 600; color: #888; letter-spacing: 0.5px; margin-bottom: 10px;'>CONVERSATIONS</div>", unsafe_allow_html=True)
    
    # Fetch from DB
    conversations = fetch_conversations()
    for conv in conversations:
        is_active = "active" if st.session_state.current_chat_id == conv['id'] else ""
        st.markdown(f"""
            <div class="history-item {is_active}">
                <span>📄 {conv['title']}</span>
            </div>
        """, unsafe_allow_html=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)

# 1. Start State: Logo and File Upload
if not st.session_state.chat_history:
    st.markdown("""
        <div style="text-align: center; margin-top: 15vh; margin-bottom: 40px;">
            <h1 style="font-family: Source Serif 4; font-size: 36px; margin-bottom: 10px;">How can I assist you?</h1>
            <p style="color: #666; font-size: 17px;">Upload a legal document to begin a risk audit.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # The centered upload box
    up_file = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
    if up_file:
        st.session_state.uploaded_filename = up_file.name
        # Simulate Analysis
        with st.spinner("Analyzing document..."):
            time.sleep(1.5)
            # DATABASE ACTION: Create new record on first interaction
            chat_id = save_new_conversation(f"Analysis: {up_file.name}")
            st.session_state.current_chat_id = chat_id
            
            st.session_state.chat_history.append({"role": "user", "content": f"Analyze {up_file.name}"})
            st.session_state.chat_history.append({"role": "ai", "content": "I've processed the document. I found **4 critical issues** in the Indemnity section. Would you like me to summarize the risks or draft a counter-clause?"})
            st.rerun()

# 2. Chat History Display
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div style="text-align: right;"><div class="user-message">{chat["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="ai-message">
                <div style="font-weight: 600; font-size: 13px; color: #888; margin-bottom: 10px; letter-spacing: 0.5px;">LEXAI ASSISTANT</div>
                {chat["content"]}
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End Container

# 3. Persistent Input Bar
if prompt := st.chat_input("Ask about specific clauses or request a rewrite..."):
    # If it's a fresh chat without a file, create DB entry on first text
    if st.session_state.current_chat_id is None:
        chat_id = save_new_conversation(prompt)
        st.session_state.current_chat_id = chat_id
        
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Simulated response
    with st.spinner("Thinking..."):
        time.sleep(1)
        response = f"I've analyzed your request regarding '{prompt}'. In legal contexts, this often triggers a 'Best Efforts' requirement. I recommend specifying a 'Reasonable Efforts' standard instead to lower your liability."
        st.session_state.chat_history.append({"role": "ai", "content": response})
    
    st.rerun()

# ─── FOOTER STATUS ────────────────────────────────────────────────────────────
if st.session_state.uploaded_filename:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div class="file-chip">
            <span style="margin-right:8px;">📎</span>
            <span>{st.session_state.uploaded_filename}</span>
        </div>
    """, unsafe_allow_html=True)