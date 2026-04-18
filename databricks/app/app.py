import streamlit as st
import os
import requests
import uuid
import pandas as pd
from databricks import sql

st.set_page_config(page_title="ClauseBreaker", page_icon="⚖️", layout="wide")

TABLE_NAME = "default.chat_logs"

# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
def get_oauth_token():
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
    try:
        response = requests.post(
            f"{host}/oidc/v1/token",
            data={
                "grant_type": "client_credentials",
                "scope": "all-apis",
                "client_id": os.environ.get("DATABRICKS_CLIENT_ID", ""),
                "client_secret": os.environ.get("DATABRICKS_CLIENT_SECRET", "")
            },
            timeout=10
        )
        return response.json().get("access_token", "")
    except Exception as e:
        return ""

DB_HOST = os.environ.get("DATABRICKS_HOST", "").replace("https://", "").rstrip("/")
DB_PATH = os.environ.get("DB_PATH", "")
DB_TOKEN = get_oauth_token()

# ─────────────────────────────────────────────────────────────
# DB
# ─────────────────────────────────────────────────────────────
def get_db_conn():
    return sql.connect(
        server_hostname=DB_HOST,
        http_path=DB_PATH,
        access_token=DB_TOKEN
    )

def save_to_db(sid, title, role, content):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {TABLE_NAME}
                    (session_id, title, role, content, ts)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (sid, title, role, content))
    except:
        pass

def load_history_list():
    try:
        with get_db_conn() as conn:
            return pd.read_sql(f"""
                SELECT session_id, MAX(title) as title
                FROM {TABLE_NAME}
                GROUP BY session_id
                ORDER BY MAX(ts) DESC
            """, conn)
    except:
        return pd.DataFrame()

def fetch_session_messages(sid):
    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT role, content FROM {TABLE_NAME}
                WHERE session_id = ? ORDER BY ts ASC
            """, (sid,))
            rows = cursor.fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]
    except:
        return []

# ─────────────────────────────────────────────────────────────
# BNS SEARCH
# ─────────────────────────────────────────────────────────────
def search_bns(query):
    try:
        with sql.connect(
            server_hostname=DB_HOST,
            http_path=DB_PATH,
            access_token=DB_TOKEN
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT section, section_name, description
                    FROM default.bns_sections
                    WHERE LOWER(description) LIKE '%{query.lower()}%'
                    LIMIT 3
                """)
                return cursor.fetchall()
    except:
        return []

# ─────────────────────────────────────────────────────────────
# LLM — uses Databricks Foundation Model API (pay-per-token)
# Works on Free Edition, no endpoint deployment needed
# ─────────────────────────────────────────────────────────────
def call_llm(prompt):
    try:
        token = get_oauth_token()
        if not token:
            return "❌ Could not get auth token. Check DATABRICKS_CLIENT_ID and SECRET in app settings."

        # Foundation Model API endpoint — no deployment needed
        url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        full_prompt = f"""You are a legal AI assistant specializing in Indian law (BNS - Bharatiya Nyaya Sanhita).

User Query:
{prompt}

Respond in the following format EXACTLY:

### 🇬🇧 English:
**Explanation:**
[Clear explanation of the legal clause or query]

**Risks:**
[Key legal risks involved]

**Fix Suggestions:**
[How to fix or safeguard against the issue]

---

### 🇮🇳 Hindi (हिंदी):
**स्पष्टीकरण:**
[Same explanation in Hindi]

**जोखिम:**
[Same risks in Hindi]

**सुझाव:**
[Same fix suggestions in Hindi]
"""

        response = requests.post(
            url,
            headers=headers,
            json={
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 1024
            },
            timeout=60
        )

        if response.status_code == 404:
            return "❌ LLM endpoint not found. Please enable Foundation Model APIs in your Databricks workspace under **AI Gateway**."
        if response.status_code == 401:
            return "❌ Auth error. Your token may have expired or lacks permissions."
        if response.status_code == 403:
            return "❌ Access denied. Make sure Foundation Model APIs are enabled for your workspace."

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "❌ Request timed out after 60s. Try again."
    except Exception as e:
        return f"❌ Error: {e}"

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())
if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ ClauseBreaker")
    st.caption(f"Host: {'✅' if DB_HOST else '❌'}")
    st.caption(f"Token: {'✅' if DB_TOKEN else '❌'}")
    st.caption(f"Path: {'✅' if DB_PATH else '❌'}")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
        st.session_state.history_loaded = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Chat History")

    if not st.session_state.history_loaded:
        if st.button("📂 Load History", use_container_width=True):
            st.session_state.history_loaded = True
            st.rerun()
    else:
        try:
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
        except:
            st.caption("No past sessions")

# ─────────────────────────────────────────────────────────────
# CHAT UI
# ─────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your contract..."):
    if not st.session_state.messages:
        st.session_state.chat_title = prompt[:40]

    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚖️ Analyzing contract..."):
            response = call_llm(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "assistant", response)
    st.rerun()