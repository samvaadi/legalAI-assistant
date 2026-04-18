import streamlit as st
import os
import requests
import uuid
import pandas as pd

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
DB_PATH = os.environ.get("DB_PATH", "")

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
    st.caption(f"Host: {'✅' if DB_HOST else '❌'}")
    st.caption(f"Token: {'✅' if DB_TOKEN else '❌'}")
    st.caption(f"Path: {'✅' if DB_PATH else '❌'}")
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.chat_title = "New Chat"
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
if prompt := st.chat_input("Ask about your contract..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"
                headers = {
                    "Authorization": f"Bearer {DB_TOKEN}",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, json={
                    "messages": [{"role": "user", "content": prompt}]
                })
                answer = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                answer = f"Error: {e}"

        st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})