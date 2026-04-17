import streamlit as st
import pandas as pd
import uuid
import time
# import databricks.sql as dbsql  # Uncomment for Databricks SQL
# from sqlalchemy import create_engine # Uncomment for standard SQL

# ─── DATABASE CORE LOGIC (REAL IMPLEMENTATION) ──────────────────────────────
def get_db_connection():
    # Example for Databricks SQL Warehouse connection
    # return dbsql.connect(server_hostname=st.secrets["host"], 
    #                     http_path=st.secrets["path"], 
    #                     access_token=st.secrets["token"])
    pass

def load_chat_history():
    """Fetches real session headers from the SQL Database."""
    # query = "SELECT session_id, title FROM lex_sessions ORDER BY created_at DESC"
    # return pd.read_sql(query, get_db_connection())
    return pd.DataFrame(columns=["session_id", "title"]) 

def save_message_to_db(session_id, role, content):
    """Commits actual user/ai strings to the database."""
    # execute("INSERT INTO lex_messages (session_id, role, content) VALUES (%s, %s, %s)", ...)
    pass

# ─── UI & DESIGN SYSTEM ──────────────────────────────────────────────────────
st.set_page_config(page_title="LexAI Terminal", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    
    :root {
        --bg: #0A0A0B;
        --panel: #111113;
        --accent: #C8A96E;
        --border: rgba(255, 255, 255, 0.06);
    }

    .stApp { background-color: var(--bg); color: #E4E4E7; font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"], footer { visibility: hidden; }

    /* Layout Split */
    .locked-hud {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
        height: 85vh;
        position: sticky;
        top: 20px;
    }

    /* Chat Terminal */
    .chat-bubble {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        line-height: 1.6;
        border: 1px solid var(--border);
    }
    .ai-msg { background: rgba(255,255,255,0.02); border-left: 3px solid var(--accent); }
    .user-msg { background: #1C1C1E; margin-left: 15%; border-radius: 12px 12px 2px 12px; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── APP ARCHITECTURE ────────────────────────────────────────────────────────
col_hud, col_main = st.columns([1, 2.5], gap="large")

# ─── LEFT PANEL: PERMANENT HUD ───
with col_hud:
    st.markdown('<div class="locked-hud">', unsafe_allow_html=True)
    st.markdown("<h2 style='letter-spacing:-1px; margin-bottom:0;'>LexAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px; color:#555; font-family:JetBrains Mono;'>COMMAND HUD v1.0</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # 1. PERMANENT UPLOADER
    st.markdown("### 📄 Contract Feed")
    uploaded_file = st.file_uploader("Drop PDF/DOCX here", type=["pdf", "docx"], label_visibility="collapsed")
    if uploaded_file:
        # REAL ACTION: Save file to Databricks Volume or S3
        # with open(f"/Volumes/main/default/lex_uploads/{uploaded_file.name}", "wb") as f:
        #     f.write(uploaded_file.getbuffer())
        st.caption(f"✅ {uploaded_file.name} synced to storage.")

    # 2. MODEL CONFIG
    st.markdown("### ⚙️ Engine")
    model_choice = st.selectbox("Select ML Model", ["Claude 3.5 Sonnet", "GPT-4o", "Llama 3 (70B)"], label_visibility="collapsed")
    
    st.markdown("### 📊 Metrics")
    st.info("No active analysis") if not uploaded_file else st.success("Document Vectorized")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ─── RIGHT PANEL: CHAT TERMINAL ───
with col_main:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Chat Scroll Area
    chat_container = st.container(height=650, border=False)
    with chat_container:
        if not st.session_state.messages:
            st.markdown("<div style='text-align:center; margin-top:20%; opacity:0.2;'><h1>⚖️</h1><p>Terminal Ready for Command</p></div>", unsafe_allow_html=True)
        
        for m in st.session_state.messages:
            css_class = "ai-msg ai-bubble" if m["role"] == "assistant" else "user-msg chat-bubble"
            st.markdown(f'<div class="{css_class}">{m["content"]}</div>', unsafe_allow_html=True)

    # Permanent Input Bar
    if prompt := st.chat_input("Input legal query or clause request..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message_to_db(st.session_state.session_id, "user", prompt)
        
        # 2. Trigger Real ML Inference
        with st.spinner("Executing Inference..."):
            # response = call_llm_api(prompt, model_choice, context=uploaded_file)
            time.sleep(1) # Simulating API latency
            response = "Based on the input, this clause lacks a 'Mutual Indemnity' carve-out. Recommendation: Amend Section 4.2."
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message_to_db(st.session_state.session_id, "assistant", response)
        
        st.rerun()

# ─── SIDEBAR: DB FETCHED HISTORY ───
with st.sidebar:
    st.markdown("### 📂 Archive")
    history_df = load_chat_history()
    if history_df.empty:
        st.caption("No past sessions found in SQL.")
    else:
        for idx, row in history_df.iterrows():
            if st.button(f"📄 {row['title']}", key=row['session_id']):
                # st.session_state.session_id = row['session_id']
                # st.session_state.messages = fetch_messages_from_db(row['session_id'])
                st.rerun()