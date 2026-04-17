import streamlit as st
import base64
import time
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI | Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CLAUDE-INSPIRED "SOBER" DESIGN SYSTEM ────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

    /* Color Palette & Base */
    :root {
        --bg-color: #F9F8F6;
        --sidebar-color: #F0EEE9;
        --text-main: #2D2D2D;
        --text-muted: #656565;
        --border-color: #E2E0D7;
        --accent-color: #D97757; /* Subtle burnt orange for actions */
        --card-bg: #FFFFFF;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Decor */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; }

    /* Sidebar - History */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-color) !important;
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-item {
        padding: 10px 12px;
        border-radius: 6px;
        margin-bottom: 4px;
        font-size: 13px;
        color: var(--text-main);
        cursor: pointer;
        transition: background 0.2s;
    }
    .sidebar-item:hover { background: rgba(0,0,0,0.05); }

    /* Main Chat Layout */
    .chat-container {
        max-width: 850px;
        margin: 0 auto;
        padding: 40px 20px;
        display: flex;
        flex-direction: column;
        gap: 24px;
    }

    /* Message Styling */
    .user-bubble {
        align-self: flex-end;
        background: #ECE9E1;
        padding: 14px 20px;
        border-radius: 20px 20px 4px 20px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.5;
    }

    .ai-bubble {
        align-self: flex-start;
        background: transparent;
        padding: 0;
        max-width: 100%;
        font-size: 15px;
        line-height: 1.6;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 30px;
        margin-bottom: 10px;
    }

    /* Analysis Cards inside Chat */
    .analysis-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .risk-indicator {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Input System */
    .stChatInputContainer {
        padding: 20px !important;
        background: var(--bg-color) !important;
    }
    
    .input-wrapper {
        position: fixed;
        bottom: 0;
        width: calc(100% - 300px); /* Sidebar width offset */
        background: var(--bg-color);
        padding: 20px 0;
        border-top: 1px solid var(--border-color);
    }

    /* Buttons & File Upload */
    .stButton>button {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-main) !important;
        border-radius: 8px !important;
    }
    
    /* Elegant Title */
    .lex-title {
        font-family: 'Source Serif 4', serif;
        font-weight: 600;
        font-size: 24px;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding: 20px;'><h1 class='lex-title'>LexAI</h1></div>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_file_name = None
        st.rerun()
        
    st.markdown("<br><div style='padding: 0 20px; font-size: 11px; font-weight: 600; color: #999; text-transform: uppercase;'>Recent History</div>", unsafe_allow_html=True)
    history = ["Employment_Agreement.pdf", "Rental_Lease_Draft.docx", "Privacy_Policy_v2.pdf"]
    for item in history:
        st.markdown(f"<div class='sidebar-item'>📄 {item}</div>", unsafe_allow_html=True)

# ─── MAIN CHAT INTERFACE ─────────────────────────────────────────────────────
# We wrap everything in a centered div for that Claude feel
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Welcome State
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; margin-top: 10vh;">
            <h2 style="font-family: 'Source Serif 4', serif; font-size: 32px;">How can I help with your contract?</h2>
            <p style="color: var(--text-muted); font-size: 16px;">Upload a document or ask a legal question to begin analysis.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Elegant File Uploader as a "first message"
    uploaded_file = st.file_uploader("Upload contract", type=['pdf', 'docx'], label_visibility="collapsed")
    if uploaded_file:
        st.session_state.uploaded_file_name = uploaded_file.name
        with st.spinner("Analyzing document structure..."):
            time.sleep(1.5)
            st.session_state.messages.append({"role": "user", "content": f"Uploaded: {uploaded_file.name}"})
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Analysis complete. I've identified **12 clauses** with **3 high-risk areas** regarding Indemnification and Liability.",
                "type": "analysis"
            })
            st.rerun()

# Message Display Loop
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        # AI Response
        st.markdown('<div class="ai-bubble">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight: 600; margin-bottom: 8px;">LexAI</div>', unsafe_allow_html=True)
        st.write(msg["content"])
        
        # If the message has an "analysis" type, show the Claude-style cards
        if msg.get("type") == "analysis":
            st.markdown(f"""
                <div class="analysis-card">
                    <span class="risk-indicator" style="background: #FEE2E2; color: #991B1B;">High Risk</span>
                    <div style="font-weight: 600; font-size: 16px;">Limitation of Liability</div>
                    <div style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">
                        The current draft caps all damages at $500, which is significantly below the contract value. 
                        Recommend increasing this to 100% of fees paid.
                    </div>
                </div>
                <div class="analysis-card">
                    <span class="risk-indicator" style="background: #FEF3C7; color: #92400E;">Medium Risk</span>
                    <div style="font-weight: 600; font-size: 16px;">Termination for Convenience</div>
                    <div style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">
                        30-day notice period is standard, but no "kill-fee" is specified for work-in-progress.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End chat-container

# ─── INPUT SYSTEM ─────────────────────────────────────────────────────────────
# We use the built-in chat_input but it is styled via CSS to stick to the bottom
if prompt := st.chat_input("Ask a follow-up or request a rewrite..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mock AI logic
    if "rewrite" in prompt.lower():
        response = "Here is a suggested rewrite for the **Indemnification** clause that adds mutual protection:\n\n`Each party shall indemnify and hold harmless the other party from and against any third-party claims arising from gross negligence...`"
    else:
        response = "I've reviewed the section you mentioned. While it seems standard, the jurisdiction in New York might affect how the 'Force Majeure' clause is interpreted."
        
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ─── FLOATING UPLOAD (When already in chat) ──────────────────────────────────
if st.session_state.uploaded_file_name:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"""
            <div style='background: white; border: 1px solid var(--border-color); padding: 12px; border-radius: 8px;'>
                <div style='font-size: 10px; color: var(--text-muted);'>ACTIVE FILE</div>
                <div style='font-size: 13px; font-weight: 500;'>{st.session_state.uploaded_file_name}</div>
            </div>
        """, unsafe_allow_html=True)