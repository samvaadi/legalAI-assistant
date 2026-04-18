import streamlit as st
import os
import requests
import uuid
import pandas as pd
from io import StringIO
from databricks import sql

st.set_page_config(page_title="ClauseBreaker", page_icon="⚖️", layout="wide")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
def get_oauth_token():
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
    client_id = os.environ.get("DATABRICKS_CLIENT_ID", "")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET", "")
    try:
        response = requests.post(
            f"{host}/oidc/v1/token",
            data={
                "grant_type": "client_credentials",
                "scope": "all-apis",
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
        return response.json().get("access_token", "")
    except:
        return ""

DB_HOST = os.environ.get("DATABRICKS_HOST", "").replace("https://", "").rstrip("/")
DB_TOKEN = get_oauth_token()
DB_PATH = os.environ.get("DB_PATH")

VOLUME_PATH = "/Volumes/workspace/default/bns_dataset/bns_sections.csv"

# ─────────────────────────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────────────────────────
def get_db_conn():
    return sql.connect(
        server_hostname=DB_HOST,
        http_path=DB_PATH,
        access_token=DB_TOKEN
    )

# ─────────────────────────────────────────────────────────────
# SAVE CHAT
# ─────────────────────────────────────────────────────────────
def save_chat(role, content):
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO default.chat_logs (session_id, role, content)
                    VALUES (?, ?, ?)
                """, (st.session_state.sid, role, content))
    except Exception as e:
        print("DB error:", e)

# ─────────────────────────────────────────────────────────────
# LOAD CHAT
# ─────────────────────────────────────────────────────────────
def load_chat():
    try:
        with get_db_conn() as conn:
            return pd.read_sql(f"""
                SELECT role, content
                FROM default.chat_logs
                WHERE session_id = '{st.session_state.sid}'
                ORDER BY ts
            """, conn)
    except:
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────────
# LOAD DATASET
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading BNS dataset...")
def load_bns_data():
    try:
        url = f"https://{DB_HOST}/api/2.0/fs/files{VOLUME_PATH}"
        headers = {"Authorization": f"Bearer {DB_TOKEN}"}
        response = requests.get(url, headers=headers)
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.error(f"Dataset error: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────────
# SEARCH (RAG)
# ─────────────────────────────────────────────────────────────
def search_sections(query, df, top_k=5):
    if df.empty:
        return "No dataset available."

    query_words = set(query.lower().split())
    text_cols = df.select_dtypes(include="object").columns.tolist()

    def score(row):
        text = " ".join(str(row[c]) for c in text_cols).lower()
        return sum(1 for w in query_words if w in text)

    df = df.copy()
    df["_score"] = df.apply(score, axis=1)
    top = df[df["_score"] > 0].sort_values("_score", ascending=False).head(top_k)

    if top.empty:
        return "No relevant sections found."

    return "\n\n---\n\n".join(
        "\n".join(f"{col}: {row[col]}" for col in text_cols)
        for _, row in top.iterrows()
    )

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

if "messages" not in st.session_state:
    df_chat = load_chat()
    st.session_state.messages = df_chat.to_dict("records") if not df_chat.empty else []

df = load_bns_data()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ ClauseBreaker")

    st.caption(f"DB: {'✅' if DB_TOKEN else '❌'}")
    st.caption(f"Dataset rows: {len(df) if not df.empty else '❌'}")

    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.rerun()

# ─────────────────────────────────────────────────────────────
# CHAT UI
# ─────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# ─────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything (legal or normal)..."):

    # SAVE USER
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat("user", prompt)

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            # 🔍 Retrieve dataset context
            context = search_sections(prompt, df)

            # 🧠 Decide mode (RAG vs Normal)
            use_rag = context != "No relevant sections found."

            if use_rag:
                final_prompt = f"""
You are a legal AI specializing in BNS law.

Use the following context:

{context}

User Question:
{prompt}

Answer with reasoning + section references.
"""
            else:
                final_prompt = f"""
You are a helpful AI assistant.

User:
{prompt}
"""

            try:
                url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"

                headers = {
                    "Authorization": f"Bearer {DB_TOKEN}",
                    "Content-Type": "application/json"
                }

                history = st.session_state.messages[:-1] + [
                    {"role": "user", "content": final_prompt}
                ]

                response = requests.post(
                    url,
                    headers=headers,
                    json={"messages": history},
                    timeout=20
                )

                answer = response.json()["choices"][0]["message"]["content"]

            except Exception as e:
                answer = f"Error: {e}"

        st.write(answer)

        if use_rag:
            with st.expander("📄 Retrieved Legal Context"):
                st.text(context)

    # SAVE ASSISTANT
    st.session_state.messages.append({"role": "assistant", "content": answer})
    save_chat("assistant", answer)