import streamlit as st
import uuid
import time
import pandas as pd
from datetime import datetime
from databricks import sql

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClauseBreaker",
    page_icon="⚖️",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# UI STYLING (CLEAN CLAUDE STYLE)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {
    background-color: #0E0E10;
    color: #E4E4E7;
    font-family: 'Inter', sans-serif;
}
header, footer { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #050505 !important;
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Chat */
.chat-container {
    max-width: 800px;
    margin: auto;
    padding-bottom: 100px;
}

.ai-block {
    padding: 20px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.user-block {
    display: flex;
    justify-content: flex-end;
    margin: 20px 0;
}

.user-bubble {
    background: #27272A;
    padding: 10px 16px;
    border-radius: 12px;
}

/* Sidebar buttons */
.stButton > button {
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    color: #888 !important;
}
.stButton > button:hover {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────────────────────
def get_db_conn():
    return sql.connect(
        server_hostname=st.secrets["DB_HOST"],
        http_path=st.secrets["DB_PATH"],
        access_token=st.secrets["DB_TOKEN"]
    )

# ─────────────────────────────────────────────────────────────
# DB FUNCTIONS
# ─────────────────────────────────────────────────────────────
def save_to_db(sid, title, role, content):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO main.lex.chat_logs
                (session_id, title, role, content, ts)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (sid, title, role, content))


def load_history_list():
    with get_db_conn() as conn:
        df = pd.read_sql("""
            SELECT session_id, MAX(title) as title
            FROM main.lex.chat_logs
            GROUP BY session_id
            ORDER BY MAX(ts) DESC
        """, conn)
    return df


def fetch_session_messages(sid):
    with get_db_conn() as conn:
        df = pd.read_sql(f"""
            SELECT role, content
            FROM main.lex.chat_logs
            WHERE session_id = '{sid}'
            ORDER BY ts ASC
        """, conn)
    return df.to_dict("records")

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ ClauseBreaker")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
        st.rerun()

    st.markdown("---")
    st.caption("History")

    history_df = load_history_list()

    if history_df.empty:
        st.caption("No past sessions")
    else:
        for _, row in history_df.iterrows():
            if st.button(f"📄 {row['title']}", key=row['session_id']):
                st.session_state.sid = row['session_id']
                st.session_state.messages = fetch_session_messages(row['session_id'])
                st.session_state.chat_title = row['title']
                st.rerun()

# ─────────────────────────────────────────────────────────────
# MAIN CHAT UI
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"""
        <div class="user-block">
            <div class="user-bubble">{m["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ai-block">
            <b>⚖️ ClauseBreaker</b><br><br>
            {m["content"]}
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUT LOGIC
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your contract..."):

    if not st.session_state.messages:
        st.session_state.chat_title = prompt[:40]

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "user", prompt)

    with st.spinner("Analyzing contract..."):
        time.sleep(1)

        response = """
### ⚠️ Risk Found: Indemnity Clause

The indemnity clause is **non-mutual**, exposing one party disproportionately.

**Fix Suggestions:**
- Make indemnity mutual  
- Add liability cap  
- Define trigger conditions  
"""

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_to_db(st.session_state.sid, st.session_state.chat_title, "assistant", response)

    st.rerun()