import streamlit as st
import os
import requests
import uuid
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="ClauseBreaker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

/* Root theme */
:root {
    --ink: #1a1a2e;
    --gold: #c9a84c;
    --gold-light: #f0d080;
    --gold-pale: #fdf6e3;
    --surface: #ffffff;
    --surface-2: #f8f5ef;
    --muted: #6b6560;
    --border: #e8e0d0;
    --danger: #c0392b;
    --success: #1a6b3c;
    --radius: 12px;
}

/* Global font */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--surface-2) !important;
    color: var(--ink) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid rgba(201,168,76,0.2) !important;
}
[data-testid="stSidebar"] * {
    color: #e8e0d0 !important;
}

/* Sidebar title */
.sidebar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--gold) !important;
    letter-spacing: 0.01em;
    margin-bottom: 0.2rem;
}
.sidebar-tagline {
    font-size: 0.75rem;
    color: rgba(232,224,208,0.5) !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Sidebar status dots */
.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    margin: 4px 0;
    color: rgba(232,224,208,0.7) !important;
}
.dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-ok { background: #4caf7d; }
.dot-err { background: #e05c5c; }

/* New chat button */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(201,168,76,0.12) !important;
    border: 1px solid rgba(201,168,76,0.35) !important;
    color: var(--gold) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    margin-top: 1rem !important;
    letter-spacing: 0.03em;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201,168,76,0.22) !important;
    border-color: var(--gold) !important;
}

/* Divider in sidebar */
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(201,168,76,0.15);
    margin: 1.2rem 0;
}

/* Main area - hide default header padding */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 6rem !important;
    max-width: 820px !important;
}

/* Page header */
.page-header {
    text-align: center;
    margin-bottom: 2.5rem;
}
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--ink);
    letter-spacing: -0.01em;
}
.page-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    margin-top: 0.25rem;
    letter-spacing: 0.02em;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}

/* Message content styling */
[data-testid="stChatMessageContent"] {
    font-size: 0.93rem !important;
    line-height: 1.7 !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    box-shadow: 0 2px 12px rgba(26,26,46,0.06) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12), 0 2px 12px rgba(26,26,46,0.06) !important;
}

/* Expander (retrieved sections) */
.streamlit-expanderHeader {
    font-size: 0.82rem !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.streamlit-expanderContent {
    background: var(--gold-pale) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    font-size: 0.8rem !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--muted) !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: var(--gold) !important;
}

/* Welcome card */
.welcome-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    text-align: center;
    margin: 2rem 0;
}
.welcome-card h3 {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: var(--ink);
    margin-bottom: 0.75rem;
}
.welcome-card p {
    font-size: 0.88rem;
    color: var(--muted);
    line-height: 1.7;
    margin: 0;
}
.suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 1.25rem;
}
.chip {
    background: var(--gold-pale);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 0.8rem;
    color: var(--ink);
    cursor: pointer;
}

/* Info badge */
.badge {
    display: inline-block;
    background: var(--gold-pale);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 100px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #8a6c1e;
    font-weight: 500;
    letter-spacing: 0.04em;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


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
                "client_secret": client_secret,
            },
        )
        return response.json().get("access_token", "")
    except:
        return ""


DB_HOST = os.environ.get("DATABRICKS_HOST", "").replace("https://", "").rstrip("/")
DB_TOKEN = get_oauth_token()
VOLUME_PATH = "/Volumes/workspace/default/bns_dataset/bns_sections.csv"


# ─────────────────────────────────────────────────────────────
# LOAD DATASET
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_bns_data():
    try:
        url = f"https://{DB_HOST}/api/2.0/fs/files{VOLUME_PATH}"
        headers = {"Authorization": f"Bearer {DB_TOKEN}"}
        response = requests.get(url, headers=headers)
        df = pd.read_csv(StringIO(response.text))
        return df
    except Exception as e:
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────────────
def search_sections(query: str, df: pd.DataFrame, top_k: int = 5) -> str:
    if df.empty:
        return "No dataset available."

    query_words = set(query.lower().split())
    text_cols = df.select_dtypes(include="object").columns.tolist()

    def score_row(row):
        combined = " ".join(str(row[c]) for c in text_cols).lower()
        return sum(1 for w in query_words if w in combined)

    df = df.copy()
    df["_score"] = df.apply(score_row, axis=1)
    top = df[df["_score"] > 0].sort_values("_score", ascending=False).head(top_k)

    if top.empty:
        return "No relevant sections found."

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
# LOAD DATA
# ─────────────────────────────────────────────────────────────
df = load_bns_data()


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚖ ClauseBreaker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">BNS Legal Intelligence</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    def status_row(label, ok):
        dot_class = "dot-ok" if ok else "dot-err"
        st.markdown(
            f'<div class="status-row"><div class="dot {dot_class}"></div>{label}</div>',
            unsafe_allow_html=True,
        )

    status_row("Databricks host", bool(DB_HOST))
    status_row("Auth token", bool(DB_TOKEN))
    status_row(f"Dataset loaded ({len(df):,} rows)" if not df.empty else "Dataset unavailable", not df.empty)

    if not df.empty:
        st.markdown(
            f'<div style="font-size:0.75rem;color:rgba(232,224,208,0.4);margin-top:6px;">'
            f'Columns: {", ".join(df.columns.tolist())}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    if st.button("＋  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sid = str(uuid.uuid4())
        st.rerun()

    st.markdown(
        '<div style="position:absolute;bottom:1.5rem;left:1.5rem;font-size:0.7rem;'
        'color:rgba(232,224,208,0.25);letter-spacing:0.06em;">POWERED BY LLAMA 3.3 · 70B</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="page-header">'
    '<div class="page-title">Bharatiya Nyaya Sanhita</div>'
    '<div class="page-subtitle">Ask anything about BNS sections — powered by your dataset</div>'
    "</div>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# WELCOME STATE
# ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
            <h3>How can I help you today?</h3>
            <p>I can answer questions about BNS sections, explain legal clauses,<br>
            compare provisions, and help you understand your rights.</p>
            <div class="suggestion-chips">
                <span class="chip">What is Section 302?</span>
                <span class="chip">Punishment for theft</span>
                <span class="chip">Clauses on assault</span>
                <span class="chip">Rights of the accused</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m["role"] == "assistant" and m.get("context"):
            with st.expander("📄 Retrieved BNS sections"):
                st.text(m["context"])


# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about a BNS section, clause or legal concept…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching BNS sections…"):

            context = search_sections(prompt, df)

            rag_prompt = f"""You are a knowledgeable and precise legal assistant specialising in the Bharatiya Nyaya Sanhita (BNS), the Indian criminal code that replaced the IPC in 2023.

Use ONLY the following BNS sections to answer the user's question. If the information is not present in the provided sections, say so clearly and honestly — do not guess.

RELEVANT BNS SECTIONS:
{context}

USER QUESTION:
{prompt}

Instructions:
- Answer clearly, concisely and professionally.
- Cite section numbers (e.g. Section 103, Section 45) wherever applicable.
- Use plain language that a non-lawyer can understand.
- If punishments are mentioned, quote them precisely.
- End with a brief disclaimer that this is informational and not legal advice."""

            try:
                url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"
                headers = {
                    "Authorization": f"Bearer {DB_TOKEN}",
                    "Content-Type": "application/json",
                }

                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                    if m["role"] in ("user", "assistant")
                ]
                history.append({"role": "user", "content": rag_prompt})

                response = requests.post(url, headers=headers, json={"messages": history})
                answer = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                answer = f"Something went wrong: {e}"

        st.write(answer)

        with st.expander("📄 Retrieved BNS sections"):
            st.text(context)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "context": context}
    )