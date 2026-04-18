import streamlit as st
import os
import requests
import uuid
import pandas as pd
from io import StringIO

st.set_page_config(page_title="ClauseBreaker", page_icon="⚖️", layout="wide")

# ─────────────────────────────────────────────────────────────
# 🎨 UI DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0a0a;
    color: #e5e5e5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #1f1f1f;
}

/* Chat bubbles */
.chat-user {
    background: linear-gradient(135deg, #6c5ce7, #a29bfe);
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    color: white;
    margin-left: auto;
    max-width: 75%;
    font-size: 14px;
}

.chat-ai {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    padding: 14px 18px;
    border-radius: 6px 18px 18px 18px;
    max-width: 75%;
    font-size: 14px;
}

/* Input */
.stChatInputContainer {
    background: #0a0a0a !important;
    border-top: 1px solid #222;
    padding: 10px;
}

/* Buttons */
.stButton button {
    background: #1f1f1f;
    color: white;
    border-radius: 10px;
    border: 1px solid #333;
}

.stButton button:hover {
    background: #2a2a2a;
}

/* Expander */
details {
    background: #111;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #222;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 🧠 CONFIG
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
VOLUME_PATH = "/Volumes/workspace/default/bns_dataset/bns_sections.csv"

# ─────────────────────────────────────────────────────────────
# 📂 LOAD DATASET
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
# 🔍 SEARCH (RAG)
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
# 🧠 SESSION
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

df = load_bns_data()

# ─────────────────────────────────────────────────────────────
# 🧾 HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-size:28px;'>⚖️ ClauseBreaker</h1>
<p style='color:#888;'>AI Legal Assistant + General Chat</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 📌 SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <h2>⚖️ ClauseBreaker</h2>
    <p style='font-size:12px;color:#777;'>Legal AI System</p>
    """, unsafe_allow_html=True)

    st.caption(f"Dataset rows: {len(df) if not df.empty else '❌'}")

    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.rerun()

# ─────────────────────────────────────────────────────────────
# 💬 CHAT DISPLAY
# ─────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="chat-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai">{m["content"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 💬 INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything (legal or normal)..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Thinking..."):

        context = search_sections(prompt, df)
        use_rag = context != "No relevant sections found."

        if use_rag:
            final_prompt = f"""
You are a legal AI specializing in BNS law.

Context:
{context}

User Question:
{prompt}

Answer with reasoning + section references.
"""
        else:
            final_prompt = f"""
You are a helpful assistant.

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

    st.markdown(f'<div class="chat-ai">{answer}</div>', unsafe_allow_html=True)

    if use_rag:
        with st.expander("📄 Retrieved Legal Context"):
            st.text(context)

    st.session_state.messages.append({"role": "assistant", "content": answer})