import streamlit as st
import time

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClauseBreaker",
    page_icon="⚖️",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# PREMIUM UI (CLAUDE / GEMINI STYLE)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --bg: #0b0b0c;
    --panel: rgba(255,255,255,0.04);
    --accent: #d4af6a;
    --border: rgba(255,255,255,0.08);
}

/* Base */
.stApp {
    background: radial-gradient(circle at top, #111 0%, #050505 100%);
    color: #e4e4e7;
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #050505;
    border-right: 1px solid var(--border);
}

/* Glass cards */
.glass {
    background: var(--panel);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Chat */
.chat-ai {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    line-height: 1.6;
}

.chat-user {
    background: linear-gradient(135deg, #d4af6a, #b8964f);
    color: black;
    border-radius: 16px;
    padding: 12px 18px;
    margin-left: auto;
    margin-bottom: 18px;
    max-width: 75%;
    font-weight: 500;
}

/* Upload */
.upload-box {
    border: 1px dashed var(--border);
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    transition: 0.2s;
}
.upload-box:hover {
    border-color: var(--accent);
}

/* Titles */
.title {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 11px;
    color: #666;
    margin-bottom: 8px;
}

/* Metrics */
.metric {
    font-family: 'JetBrains Mono';
    font-size: 28px;
    color: var(--accent);
    font-weight: 700;
}

/* Input */
.stChatInputContainer {
    border-top: 1px solid var(--border);
    padding-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ ClauseBreaker")

    if st.button("＋ New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("History (mock)")
    st.write("📄 NDA Contract")
    st.write("📄 Vendor Agreement")

# ─────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([0.7, 1.3])

# ─────────────────────────────────────────────────────────────
# LEFT PANEL (HUD)
# ─────────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="title">System HUD</div>', unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">INPUT STREAM</div>', unsafe_allow_html=True)

    st.markdown('<div class="upload-box">Drop contract or upload</div>', unsafe_allow_html=True)
    file = st.file_uploader("", type=["pdf","docx"], label_visibility="collapsed")

    if file:
        st.success(f"Loaded: {file.name}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Metrics
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    c1.markdown('<div class="subtitle">RISK</div><div class="metric">84%</div>', unsafe_allow_html=True)
    c2.markdown('<div class="subtitle">CLAUSES</div><div class="metric">12</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# RIGHT PANEL (CHAT)
# ─────────────────────────────────────────────────────────────
with col_right:
    st.markdown('<div class="title">AI Contract Terminal</div>', unsafe_allow_html=True)

    chat_container = st.container(height=600)

    with chat_container:
        for m in st.session_state.messages:
            if m["role"] == "user":
                st.markdown(f'<div class="chat-user">{m["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">{m["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask about your contract..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing contract..."):
            time.sleep(1)

            response = """
### ⚠️ Risk Detected: Indemnity Clause

The indemnity clause is **non-mutual**, exposing one party disproportionately.

**Fix Suggestions:**
- Make indemnity mutual  
- Add liability cap  
- Clearly define trigger conditions  
"""
            st.session_state.messages.append({"role": "ai", "content": response})

        st.rerun()