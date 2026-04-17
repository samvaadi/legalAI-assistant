import streamlit as st
import uuid
import time
import pandas as pd
from databricks import sql

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClauseBreaker",
    page_icon="⚖️",
    layout="wide"
)

TABLE_NAME = "default.chat_logs"  # ✅ use default schema

# ─────────────────────────────────────────────────────────────
# UI STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background-color: #0E0E10;
    color: #E4E4E7;
    font-family: sans-serif;
}
header, footer { visibility: hidden; }

[data-testid="stSidebar"] {
    background-color: #050505 !important;
}

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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DB CONNECTION
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
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {TABLE_NAME}
                    (session_id, title, role, content, ts)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (sid, title, role, content))
    except Exception as e:
        st.error(f"DB Insert Error: {e}")


def load_history_list():
    try:
        with get_db_conn() as conn:
            return pd.read_sql(f"""
                SELECT session_id, MAX(title) as title
                FROM {TABLE_NAME}
                GROUP BY session_id
                ORDER BY MAX(ts) DESC
            """, conn)
    except Exception:
        return pd.DataFrame()


def fetch_session_messages(sid):
    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT role, content
                FROM {TABLE_NAME}
                WHERE session_id = ?
                ORDER BY ts ASC
            """, (sid,))
            rows = cursor.fetchall()

        return [{"role": r[0], "content": r[1]} for r in rows]
    except Exception:
        return []

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
    st.markdown("### 🧠 Chat History")

    history_df = load_history_list()

    if history_df.empty:
        st.caption("No past sessions")
    else:
        for _, row in history_df.iterrows():
            if st.button(f"📄 {row['title']}", key=row["session_id"]):
                st.session_state.sid = row["session_id"]
                st.session_state.messages = fetch_session_messages(row["session_id"])
                st.session_state.chat_title = row["title"]
                st.rerun()

# ─────────────────────────────────────────────────────────────
# CHAT UI
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
# INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your contract..."):

    if not st.session_state.messages:
        st.session_state.chat_title = prompt[:40]

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "user", prompt)

    # Fake AI response (replace later with real model)
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