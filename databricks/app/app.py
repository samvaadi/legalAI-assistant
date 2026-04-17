import streamlit as st
import time
import uuid
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI | Legal Command",
    page_icon="⚖️",
    layout="wide",
)

# ─── THE ELITE "SOBER" DESIGN SYSTEM ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

    /* Color Palette - Stone & Paper */
    :root {
        --bg-color: #F7F7F2;
        --sidebar-color: #EFEDE7;
        --text-main: #1D1D1B;
        --text-muted: #6B6B63;
        --border: #E1E1D9;
        --accent: #D97757;
        --ai-bubble-bg: transparent;
        --user-bubble-bg: #E7E4DB;
    }

    .stApp { background-color: var(--bg-color); color: var(--text-main); font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    /* Centered Chat Layout */
    .chat-wrapper {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 60px;
        padding-bottom: 150px;
    }

    /* Sidebar - High End Navigation */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-color) !important;
        border-right: 1px solid var(--border);
        padding: 20px 10px;
    }

    .history-card {
        padding: 12px 14px;
        border-radius: 10px;
        margin-bottom: 6px;
        font-size: 13.5px;
        color: var(--text-main);
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        background: transparent;
    }
    .history-card:hover {
        background: #E4E1D8;
        border-color: var(--border);
        transform: translateX(4px);
    }
    .history-active {
        background: #E4E1D8;
        font-weight: 500;
        border-color: var(--border);
    }

    /* Chat Bubbles - Claude Style */
    .ai-row {
        margin-bottom: 48px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 32px;
        animation: fadeIn 0.5s ease;
    }
    .user-row {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 32px;
        animation: slideIn 0.3s ease;
    }
    .user-bubble {
        background: var(--user-bubble-bg);
        padding: 14px 22px;
        border-radius: 20px 20px 4px 20px;
        font-size: 15.5px;
        line-height: 1.5;
        max-width: 85%;
        color: var(--text-main);
    }

    /* Analysis Report Card */
    .report-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .risk-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        display: inline-block;
    }

    /* Input HUD */
    .stChatInputContainer {
        border-top: 1px solid var(--border) !important;
        background: var(--bg-color) !important;
        padding: 20px 0 !important;
    }

    /* Animations */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE LAYER ──────────────────────────────────────────────────────────
# Connects to session_state to persist chats during session
def get_db_chats():
    if "db_chats" not in st.session_state:
        st.session_state.db_chats = [
            {"id": str(uuid.uuid4()), "title": "MSA Risk Audit", "time": "2h ago"},
            {"id": str(uuid.uuid4()), "title": "Consulting Rewrite", "time": "5h ago"},
        ]
    return st.session_state.db_chats

def commit_to_db(title):
    new_chat = {"id": str(uuid.uuid4()), "title": title[:28] + "...", "time": "Just now"}
    st.session_state.db_chats.insert(0, new_chat)
    return new_chat["id"]

# ─── STATE MANAGEMENT ────────────────────────────────────────────────────────
if "active_id" not in st.session_state:
    st.session_state.active_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-family:Source Serif 4; font-size: 26px; padding: 10px 0;'>LexAI</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.active_id = None
        st.session_state.messages = []
        st.session_state.file_name = None
        st.rerun()

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 11px; font-weight: 600; color: #999; letter-spacing: 0.8px; margin-bottom: 12px;'>HISTORY</div>", unsafe_allow_html=True)
    
    chats = get_db_chats()
    for c in chats:
        active_class = "history-active" if st.session_state.active_id == c['id'] else ""
        st.markdown(f"""
            <div class="history-card {active_class}">
                <div style="font-weight: 500;">📄 {c['title']}</div>
                <div style="font-size: 10px; color: #999; margin-top: 2px;">{c['time']}</div>
            </div>
        """, unsafe_allow_html=True)

# ─── MAIN INTERFACE ──────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# 1. Empty State
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; margin-top: 12vh;">
            <h1 style="font-family: Source Serif 4; font-size: 42px; font-weight: 600; color: #1a1a1a;">Analyze your contract.</h1>
            <p style="color: #6B6B63; font-size: 18px; margin-top: 10px;">Upload a legal document to map risks and generate counter-clauses.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Styled Uploader
    up = st.file_uploader("Upload", type=['pdf', 'docx'], label_visibility="collapsed")
    if up:
        st.session_state.file_name = up.name
        with st.spinner("Processing neural audit..."):
            time.sleep(1.8)
            # Commit to DB on first action
            st.session_state.active_id = commit_to_db(f"Audit: {up.name}")
            st.session_state.messages.append({"role": "user", "content": f"Analyze {up.name}"})
            st.session_state.messages.append({
                "role": "ai", 
                "content": f"I've completed the audit for **{up.name}**. I found significant liability exposure in the Intellectual Property section. Would you like a breakdown of the risks?",
                "type": "report"
            })
            st.rerun()

# 2. Conversation Stream
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="user-row"><div class="user-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-row">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: 600; font-size: 12px; color: #999; margin-bottom: 12px; letter-spacing: 1px;">LEXAI</div>', unsafe_allow_html=True)
        st.write(m["content"])
        
        # Premium Report Card
        if m.get("type") == "report":
            st.markdown("""
                <div class="report-card">
                    <span class="risk-badge" style="background: #FEE2E2; color: #991B1B;">Critical</span>
                    <div style="font-weight: 600; font-size: 17px; margin-bottom: 4px;">Indemnification Gap</div>
                    <div style="font-size: 14px; color: var(--text-muted); line-height: 1.5;">
                        Clause 8.2 creates an uncapped indemnity for third-party IP claims. Industry standard is to cap this at 2x the annual contract value.
                    </div>
                    <hr style="margin: 20px 0; opacity: 0.1;">
                    <span class="risk-badge" style="background: #FEF3C7; color: #92400E;">Moderate</span>
                    <div style="font-weight: 600; font-size: 17px; margin-bottom: 4px;">Governing Law</div>
                    <div style="font-size: 14px; color: var(--text-muted); line-height: 1.5;">
                        The contract defaults to California law but lacks an arbitration sub-clause, which may lead to costly litigation.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End chat-wrapper

# ─── INPUT SYSTEM ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask for a rewrite or specific legal analysis..."):
    # If no active chat, start one in DB
    if not st.session_state.active_id:
        st.session_state.active_id = commit_to_db(prompt)
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Processing..."):
        time.sleep(1.2)
        # Professional legal reasoning response
        ans = "I've reviewed the language. While the clause is enforceable in most jurisdictions, adding a 'gross negligence' carve-out would significantly lower your exposure. Should I draft that version?"
        st.session_state.messages.append({"role": "ai", "content": ans})
    st.rerun()

# ─── SIDEBAR FOOTER ───────────────────────────────────────────────────────────
if st.session_state.file_name:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"""
            <div style="background: white; border: 1px solid var(--border); padding: 14px; border-radius: 12px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 18px;">📄</span>
                <div style="overflow: hidden;">
                    <div style="font-size: 11px; font-weight: 600; color: #1a1a1a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.file_name}</div>
                    <div style="font-size: 10px; color: #999;">Audit in progress</div>
                </div>
            </div>
        """, unsafe_allow_html=True)