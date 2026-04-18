import streamlit as st
import uuid
import pandas as pd
from databricks import sql
import requests
import os

st.set_page_config(
    page_title="ClauseBreaker",
    page_icon="⚖️",
    layout="wide"
)

TABLE_NAME = "default.chat_logs"

# Auto-injected by Databricks Apps
DB_HOST = os.environ.get("DATABRICKS_HOST", "").replace("https://", "")
# Try all possible token sources
DB_TOKEN = (
    os.environ.get("DATABRICKS_TOKEN") or
    os.environ.get("DB_TOKEN") or
    os.environ.get("GRPC_GATEWAY_TOKEN") or
    ""
)
DB_PATH = os.environ.get("DB_PATH", "")

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
[data-testid="stSidebar"] { background-color: #050505 !important; }
.chat-container { max-width: 800px; margin: auto; padding-bottom: 100px; }
.ai-block { padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
.user-block { display: flex; justify-content: flex-end; margin: 20px 0; }
.user-bubble { background: #27272A; padding: 10px 16px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# LOAD MODEL - lazy, cached, only when needed
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_translation_model():
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from IndicTransToolkit import IndicProcessor
    model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
    model.eval()
    ip = IndicProcessor(inference=True)
    return tokenizer, model, ip


# ─────────────────────────────────────────────────────────────
# DB CONNECTION
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
                SELECT role, content FROM {TABLE_NAME}
                WHERE session_id = ? ORDER BY ts ASC
            """, (sid,))
            rows = cursor.fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────
# TRANSLATION
# ─────────────────────────────────────────────────────────────
def translate_to_hindi(text):
    import torch
    tokenizer, model, ip = load_translation_model()
    src_lang, tgt_lang = "eng_Latn", "hin_Deva"
    batch = ip.preprocess_batch([text], src_lang=src_lang, tgt_lang=tgt_lang)
    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt")
    with torch.no_grad():
        generated_tokens = model.generate(**inputs, num_beams=5, max_length=256)
    translations = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return ip.postprocess_batch(translations, lang=tgt_lang)[0]


# ─────────────────────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────────────────────
def call_llm(prompt):
    try:
        url = f"https://{DB_HOST}/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"
        headers = {
            "Authorization": f"Bearer {DB_TOKEN}",
            "Content-Type": "application/json"
        }
        full_prompt = f"""
You are a legal AI assistant for Indian law (BNS).

User Query:
{prompt}

Give:
- Explanation
- Risks
- Fix suggestions
"""
        response = requests.post(url, headers=headers, json={
            "messages": [{"role": "user", "content": full_prompt}]
        })
        response.raise_for_status()
        english = response.json()["choices"][0]["message"]["content"]

        with st.spinner("Translating to Hindi..."):
            hindi = translate_to_hindi(english)

        return f"""### 🇬🇧 English:
{english}

---

### 🇮🇳 Hindi:
{hindi}"""

    except Exception as e:
        return f"LLM Error: {e}"


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

    # DEBUG - remove after testing
    st.caption(f"Host: {'✅' if DB_HOST else '❌ NOT SET'}")
    st.caption(f"Token: {'✅' if DB_TOKEN else '❌ NOT SET'}")
    st.caption(f"Path: {'✅' if DB_PATH else '❌ NOT SET'}")

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
# CHAT INPUT - always visible at bottom
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your contract..."):
    if not st.session_state.messages:
        st.session_state.chat_title = prompt[:40]

    st.session_state.messages.append({"role": "user", "content": prompt})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "user", prompt)

    with st.spinner("Analyzing contract..."):
        response = call_llm(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_to_db(st.session_state.sid, st.session_state.chat_title, "assistant", response)
    st.rerun()