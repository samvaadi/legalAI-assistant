import streamlit as st
import os
import requests
import uuid
import pandas as pd
from io import StringIO

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
VOLUME_PATH = "/Volumes/workspace/default/bns_dataset/bns_sections.csv"

# ─────────────────────────────────────────────────────────────
# LOAD DATASET FROM DATABRICKS VOLUME via DBFS API
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading BNS dataset...")
def load_bns_data():
    try:
        url = f"https://{DB_HOST}/api/2.0/fs/files{VOLUME_PATH}"
        headers = {"Authorization": f"Bearer {DB_TOKEN}"}
        response = requests.get(url, headers=headers)
        df = pd.read_csv(StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────────
# SEARCH RELEVANT SECTIONS
# ─────────────────────────────────────────────────────────────
def search_sections(query: str, df: pd.DataFrame, top_k: int = 5) -> str:
    if df.empty:
        return "No dataset available."

    query_words = set(query.lower().split())

    # Score each row by keyword overlap across all text columns
    text_cols = df.select_dtypes(include="object").columns.tolist()

    def score_row(row):
        combined = " ".join(str(row[c]) for c in text_cols).lower()
        return sum(1 for w in query_words if w in combined)

    df = df.copy()
    df["_score"] = df.apply(score_row, axis=1)
    top = df[df["_score"] > 0].sort_values("_score", ascending=False).head(top_k)

    if top.empty:
        return "No relevant sections found."

    # Format results
    results = []
    for _, row in top.iterrows():
        results.append("\n".join(f"{col}: {row[col]}" for col in text_cols))
    return "\n\n---\n\n".join(results)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
df = load_bns_data()

with st.sidebar:
    st.markdown("## ⚖️ ClauseBreaker")
    st.caption(f"Host: {'✅' if DB_HOST else '❌'}")
    st.caption(f"Token: {'✅' if DB_TOKEN else '❌'}")
    st.caption(f"Dataset rows: {len(df) if not df.empty else '❌'}")

    if not df.empty:
        st.caption(f"Columns: {', '.join(df.columns.tolist())}")

    if st.button("＋ New Chat", use_container_width=True):
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
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about BNS sections..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching BNS sections..."):

            # 1. Retrieve relevant sections from CSV
            context = search_sections(prompt, df)

            # 2. Build RAG prompt
            rag_prompt = f"""You are a legal assistant specializing in the Bharatiya Nyaya Sanhita (BNS).
Use ONLY the following BNS sections to answer the user's question.
If the answer is not in the provided sections, say so clearly.

RELEVANT BNS SECTIONS:
{context}

USER QUESTION:
{prompt}

Answer clearly and cite the section numbers where applicable."""

            # 3. Send to Llama
            try:
                url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"
                headers = {
                    "Authorization": f"Bearer {DB_TOKEN}",
                    "Content-Type": "application/json"
                }
                
                # Build conversation history
                history = [{"role": m["role"], "content": m["content"]} 
                          for m in st.session_state.messages[:-1]]
                history.append({"role": "user", "content": rag_prompt})

                response = requests.post(url, headers=headers, json={"messages": history})
                answer = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                answer = f"Error: {e}"

        st.write(answer)

        # Show retrieved context in expander
        with st.expander("📄 Retrieved BNS Sections"):
            st.text(context)

    st.session_state.messages.append({"role": "assistant", "content": answer})