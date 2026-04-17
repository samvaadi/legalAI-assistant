"""
LexAI — Legal Contract Analyzer
Streamlit App (Databricks-ready)
"""

import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Optional

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI — Legal Contract Analyzer",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── STYLES ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0c;
    color: #f0eff4;
}
.stApp { background-color: #0a0a0c; }

/* Hide Streamlit chrome */
#MainMenu, footer, .stDeployButton { visibility: hidden; }
header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111115 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] .stMarkdown h1 {
    font-family: 'Playfair Display', serif;
    color: #f0eff4;
}

/* Cards */
.lex-card {
    background: #111115;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.lex-card-accent {
    background: #111115;
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #c8a96e;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

/* Risk colors */
.risk-critical { color: #ff2d55 !important; }
.risk-high     { color: #ff6b35 !important; }
.risk-medium   { color: #ffd60a !important; }
.risk-low      { color: #34c759 !important; }
.risk-safe     { color: #30d158 !important; }

.badge-critical { background: rgba(255,45,85,0.15);  color: #ff2d55; border: 1px solid rgba(255,45,85,0.3);  padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; font-family: 'DM Mono'; }
.badge-high     { background: rgba(255,107,53,0.15); color: #ff6b35; border: 1px solid rgba(255,107,53,0.3); padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; font-family: 'DM Mono'; }
.badge-medium   { background: rgba(255,214,10,0.15); color: #ffd60a; border: 1px solid rgba(255,214,10,0.3); padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; font-family: 'DM Mono'; }
.badge-low      { background: rgba(52,199,89,0.15);  color: #34c759; border: 1px solid rgba(52,199,89,0.3);  padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; font-family: 'DM Mono'; }

/* Buttons */
.stButton > button {
    background: #c8a96e !important;
    color: #0a0a0c !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans' !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Text input */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #18181e !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #f0eff4 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans' !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #111115;
    border: 2px dashed rgba(255,255,255,0.12);
    border-radius: 10px;
}

/* Progress bars */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #c8a96e, #e8c98e) !important;
}

/* Metric */
[data-testid="stMetric"] {
    background: #111115;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #8b8a99 !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #f0eff4 !important; }

/* Expander */
[data-testid="stExpander"] {
    background: #111115;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}

/* Chat */
.chat-user {
    background: rgba(200,169,110,0.12);
    border: 1px solid rgba(200,169,110,0.25);
    border-radius: 10px 10px 2px 10px;
    padding: 10px 14px;
    margin: 6px 0 6px 20%;
    font-size: 13px;
    line-height: 1.55;
}
.chat-ai {
    background: #18181e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px 10px 10px 2px;
    padding: 10px 14px;
    margin: 6px 20% 6px 0;
    font-size: 13px;
    line-height: 1.55;
}
.chat-ai-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #c8a96e;
    font-family: 'DM Mono';
    margin-bottom: 4px;
}

/* Section header */
.section-label {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #4a4958;
    font-family: 'DM Mono';
    margin-bottom: 8px;
    text-transform: uppercase;
}

/* Score circle */
.score-circle {
    width: 90px; height: 90px;
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    margin: 0 auto 12px;
    font-family: 'Playfair Display';
}

/* Divider */
.lex-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 14px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 20px !important;
    color: #8b8a99 !important;
    font-family: 'DM Sans' !important;
    font-size: 13px !important;
    padding: 5px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(200,169,110,0.12) !important;
    border-color: rgba(200,169,110,0.3) !important;
    color: #c8a96e !important;
}
</style>
""", unsafe_allow_html=True)

# ─── MOCK DATA ─────────────────────────────────────────────────────────────────
SAMPLE_CLAUSES = [
    {
        "id": "c1", "title": "Limitation of Liability",
        "risk_level": "high", "risk_score": 78,
        "text": "In no event shall either party be liable for any indirect, incidental, special, exemplary, or consequential damages, however caused.",
        "explanation": "This clause broadly excludes consequential damages, severely limiting your recovery if the counterparty breaches.",
        "suggestions": [
            "Add a carve-out for gross negligence and willful misconduct",
            "Cap limitation at a reasonable multiple of fees paid",
            "Explicitly exclude IP indemnification from liability cap",
        ],
    },
    {
        "id": "c2", "title": "Indemnification",
        "risk_level": "critical", "risk_score": 91,
        "text": "You shall indemnify, defend, and hold harmless the Company from any claims arising from your use of the service.",
        "explanation": "One-sided indemnification placing nearly all risk on you. No mutual indemnity, no cap.",
        "suggestions": [
            "Require mutual indemnification obligations",
            "Add carve-out for Company's own negligence",
            "Cap indemnification at the contract value",
        ],
    },
    {
        "id": "c3", "title": "IP Assignment",
        "risk_level": "critical", "risk_score": 88,
        "text": "All work product and deliverables created in connection with Services shall be the exclusive property of the Company.",
        "explanation": "Broad IP assignment may capture pre-existing IP and background technology with no carve-outs.",
        "suggestions": [
            "Add schedule of pre-existing IP that is excluded",
            "Limit assignment to work created specifically under this contract",
            "Negotiate license-back for general methodologies",
        ],
    },
    {
        "id": "c4", "title": "Termination for Convenience",
        "risk_level": "medium", "risk_score": 52,
        "text": "Either party may terminate with 30 days written notice. Company's sole obligation is payment for services rendered.",
        "explanation": "Short notice period for a complex engagement. No kill fee or transition assistance.",
        "suggestions": [
            "Negotiate 60-90 day notice period",
            "Add kill fee of 20-25% of remaining contract value",
            "Include transition assistance clause",
        ],
    },
    {
        "id": "c5", "title": "Non-Compete",
        "risk_level": "high", "risk_score": 82,
        "text": "For 24 months post-termination, you agree not to engage in any competing business within the United States.",
        "explanation": "Broad geographic scope and long duration. May be unenforceable but still poses legal risk.",
        "suggestions": [
            "Limit to specific markets where Company operates",
            "Reduce duration to 12 months",
            "Add specific definition of 'competing business'",
        ],
    },
    {
        "id": "c6", "title": "Confidentiality",
        "risk_level": "low", "risk_score": 22,
        "text": "Each party agrees to maintain confidentiality of the other's Confidential Information for 3 years post-termination.",
        "explanation": "Standard mutual NDA with reasonable duration. Adequately protects both parties.",
        "suggestions": ["Extend protection for trade secrets to be indefinite"],
    },
    {
        "id": "c7", "title": "Payment Terms",
        "risk_level": "medium", "risk_score": 48,
        "text": "Invoices are due within 60 days of receipt. Company may withhold payment for disputed deliverables without interest.",
        "explanation": "60-day net terms longer than industry standard. No interest on late payments.",
        "suggestions": [
            "Negotiate Net-30 payment terms",
            "Add 1.5% monthly interest on overdue amounts",
        ],
    },
    {
        "id": "c8", "title": "Governing Law",
        "risk_level": "low", "risk_score": 28,
        "text": "This Agreement is governed by the laws of Delaware, with exclusive jurisdiction in New Castle County courts.",
        "explanation": "Delaware jurisdiction is standard and reasonably neutral for commercial contracts.",
        "suggestions": ["Consider adding arbitration clause for faster resolution"],
    },
]

RISK_COLORS = {
    "critical": "#ff2d55",
    "high": "#ff6b35",
    "medium": "#ffd60a",
    "low": "#34c759",
    "safe": "#30d158",
}

CHAT_RESPONSES = {
    "risk": "The overall risk score is **71/100 (High)**. The two most critical issues are:\n\n1. **Indemnification** (91/100) — one-sided, no cap\n2. **IP Assignment** (88/100) — captures pre-existing IP\n\nThese should be your priority in negotiations.",
    "negotiate": "**Negotiation Strategy:**\n\n1. Push for mutual indemnification\n2. Explicitly carve out pre-existing IP\n3. Request liability cap = fees paid in prior 12 months\n4. Demand Net-30 payment terms\n5. Narrow non-compete geography",
    "default": "Based on my analysis, this contract contains several provisions that disproportionately favor the counterparty. I recommend focusing on the indemnification and IP assignment clauses first, as they carry the highest risk exposure. Would you like me to draft alternative language for any specific clause?",
}

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "contract_uploaded" not in st.session_state:
    st.session_state.contract_uploaded = False
if "contract_name" not in st.session_state:
    st.session_state.contract_name = ""
if "active_clause" not in st.session_state:
    st.session_state.active_clause = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def risk_color(level: str) -> str:
    return RISK_COLORS.get(level, "#8b8a99")

def render_risk_bar(score: int, level: str, width: str = "100%"):
    color = risk_color(level)
    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.06);border-radius:3px;height:5px;width:{width};overflow:hidden;margin:4px 0 0">
          <div style="width:{score}%;height:100%;background:{color};border-radius:3px;transition:width 0.6s"></div>
        </div>
    """, unsafe_allow_html=True)

def get_chat_response(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["risk", "score", "dangerous", "worst"]):
        return CHAT_RESPONSES["risk"]
    if any(w in msg for w in ["negotiate", "strategy", "push back", "counter"]):
        return CHAT_RESPONSES["negotiate"]
    return CHAT_RESPONSES["default"]

def compute_breakdown():
    bd = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for c in SAMPLE_CLAUSES:
        lvl = c["risk_level"]
        if lvl in bd:
            bd[lvl] += 1
    return bd

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.07)">
          <div style="width:32px;height:32px;background:rgba(200,169,110,0.15);border:1px solid rgba(200,169,110,0.3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px">⚖</div>
          <div>
            <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700">Lex</span><span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#c8a96e">AI</span>
          </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋  Analyze New Contract", use_container_width=True):
        st.session_state.show_upload = True
        st.rerun()

    st.markdown('<div class="section-label" style="margin-top:16px">RECENT CONTRACTS</div>', unsafe_allow_html=True)

    if st.session_state.contract_uploaded:
        st.markdown(f"""
            <div style="background:rgba(200,169,110,0.1);border:1px solid rgba(200,169,110,0.2);border-radius:8px;padding:10px 12px;cursor:pointer">
              <div style="display:flex;align-items:center;gap:8px">
                <span>📄</span>
                <div style="flex:1;min-width:0">
                  <p style="font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0">{st.session_state.contract_name or "Service Agreement"}</p>
                  <p style="font-size:10px;color:#8b8a99;margin:0;font-family:'DM Mono'">Today · 8 clauses</p>
                </div>
                <span style="font-size:11px;font-weight:700;color:#ff6b35;background:rgba(255,107,53,0.12);padding:2px 7px;border-radius:20px;font-family:'DM Mono'">71</span>
              </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:12px;color:#4a4958">No contracts yet</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="font-size:10px;color:#4a4958">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
            <div style="width:6px;height:6px;background:#34c759;border-radius:50%"></div>
            <span>AI Legal Analysis</span>
          </div>
          <p style="margin:0">Not a substitute for legal counsel</p>
        </div>
    """, unsafe_allow_html=True)

# ─── UPLOAD MODAL (simulated with expander) ────────────────────────────────────
if st.session_state.show_upload and not st.session_state.contract_uploaded:
    st.markdown("## Upload Contract")
    uploaded = st.file_uploader(
        "Drag & drop a contract PDF or DOCX",
        type=["pdf", "docx", "doc"],
        label_visibility="visible",
    )
    if uploaded:
        with st.spinner("Analyzing contract — extracting clauses & scoring risk…"):
            progress = st.progress(0, text="Parsing document…")
            for i in range(100):
                time.sleep(0.02)
                if i == 30:
                    progress.progress(i, text="Identifying clauses…")
                elif i == 60:
                    progress.progress(i, text="Running risk models…")
                elif i == 85:
                    progress.progress(i, text="Generating recommendations…")
                else:
                    progress.progress(i)
            progress.progress(100, text="Analysis complete ✓")
            time.sleep(0.3)

        st.session_state.contract_uploaded = True
        st.session_state.contract_name = uploaded.name
        st.session_state.show_upload = False
        st.success("Contract analyzed successfully!")
        time.sleep(0.5)
        st.rerun()

    col_cancel, _ = st.columns([1, 3])
    with col_cancel:
        if st.button("Cancel"):
            st.session_state.show_upload = False
            st.rerun()

# ─── MAIN CONTENT ──────────────────────────────────────────────────────────────
elif not st.session_state.contract_uploaded:
    # Empty State
    st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;text-align:center;padding:60px 20px">
          <div style="font-size:64px;filter:drop-shadow(0 0 30px rgba(200,169,110,0.3));margin-bottom:16px">⚖</div>
          <h1 style="font-family:'Playfair Display',serif;font-size:32px;font-weight:900;margin-bottom:12px">Analyze Your Contract</h1>
          <p style="font-size:15px;color:#8b8a99;max-width:440px;line-height:1.6;margin-bottom:28px">
            Upload a PDF or DOCX to get instant AI-powered risk scoring, clause extraction, and negotiation recommendations.
          </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Upload Contract →", use_container_width=True):
            st.session_state.show_upload = True
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    for col, icon, title, desc in [
        (f1, "🔍", "Risk Scoring", "Every clause scored 0–100"),
        (f2, "📋", "Clause Extraction", "Auto-identify key provisions"),
        (f3, "💡", "Rewrites", "AI-suggested improvements"),
        (f4, "🔄", "Version Diff", "Track changes across drafts"),
    ]:
        with col:
            st.markdown(f"""
                <div class="lex-card" style="text-align:center">
                  <div style="font-size:24px;margin-bottom:8px">{icon}</div>
                  <strong style="font-size:12px">{title}</strong>
                  <p style="font-size:11px;color:#8b8a99;margin-top:4px">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

else:
    # ─── CONTRACT ANALYZED ────────────────────────────────────────────────────
    fname = st.session_state.contract_name or "Service Agreement.pdf"
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
          <span style="font-size:18px">📄</span>
          <span style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700">{fname}</span>
        </div>
        <p style="color:#8b8a99;font-size:12px;margin-bottom:20px">Analyzed {datetime.now().strftime('%-d %b %Y, %H:%M')} · 8 clauses · 2 parties</p>
    """, unsafe_allow_html=True)

    tab_clauses, tab_chat, tab_versions, tab_compare = st.tabs([
        "📋  Clauses", "💬  AI Chat", "🕐  Versions", "🔄  Compare",
    ])

    # ─── TAB: CLAUSES ─────────────────────────────────────────────────────────
    with tab_clauses:
        col_risk, col_clauses = st.columns([1.1, 2])

        with col_risk:
            # Overall Risk
            breakdown = compute_breakdown()
            st.markdown("""<div class="lex-card">""", unsafe_allow_html=True)
            st.markdown('<div class="section-label">OVERALL RISK</div>', unsafe_allow_html=True)

            # Gauge via SVG
            score = 71
            circ = 2 * 3.14159 * 54
            offset = circ - (score / 100) * circ
            st.markdown(f"""
                <div style="text-align:center;margin-bottom:14px">
                  <svg viewBox="0 0 128 128" style="width:130px">
                    <circle cx="64" cy="64" r="54" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
                    <circle cx="64" cy="64" r="54" fill="none" stroke="#ff6b35" stroke-width="10"
                      stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}"
                      stroke-linecap="round" transform="rotate(-90 64 64)"/>
                  </svg>
                  <div style="margin-top:-80px;margin-bottom:58px">
                    <span style="font-family:'Playfair Display',serif;font-size:36px;font-weight:900;color:#ff6b35">{score}</span><br>
                    <span style="font-size:9px;font-weight:700;letter-spacing:0.08em;color:#ff6b35;font-family:'DM Mono'">HIGH RISK</span>
                  </div>
                </div>
            """, unsafe_allow_html=True)

            for lvl, count in breakdown.items():
                total = sum(breakdown.values())
                pct = int((count / total) * 100) if total else 0
                color = risk_color(lvl)
                st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                      <span style="font-size:9px;font-weight:700;width:52px;font-family:'DM Mono';letter-spacing:0.06em;color:{color}">{lvl.upper()}</span>
                      <div style="flex:1;height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;background:{color};border-radius:3px"></div>
                      </div>
                      <span style="font-size:11px;font-family:'DM Mono';color:#8b8a99;width:14px;text-align:right">{count}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # AI Summary
            st.markdown("""
                <div class="lex-card">
                  <div class="section-label">AI ANALYSIS</div>
                  <p style="font-size:12px;color:#8b8a99;line-height:1.6">
                    This agreement contains several high-risk provisions that disproportionately favor the Company.
                    Key concerns: one-sided indemnification, broad IP assignment, and an overly wide non-compete.
                    Immediate legal review is recommended before signing.
                  </p>
                </div>
            """, unsafe_allow_html=True)

            # Meta
            st.markdown("""
                <div class="lex-card">
                  <div class="section-label">CONTRACT DETAILS</div>
            """, unsafe_allow_html=True)
            for key, val in [("Party 1", "Acme Corp"), ("Party 2", "Consultant"), ("Effective", "Jan 1, 2025"), ("Clauses", "8")]:
                st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06)">
                      <span style="font-size:11px;color:#8b8a99">{key}</span>
                      <span style="font-size:11px;font-family:'DM Mono'">{val}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_clauses:
            # Filter
            filter_options = ["All", "Critical", "High", "Medium", "Low"]
            selected_filter = st.selectbox("Filter by risk level", filter_options, label_visibility="collapsed")
            search = st.text_input("Search clauses…", placeholder="Search clauses…", label_visibility="collapsed")

            sorted_clauses = sorted(SAMPLE_CLAUSES, key=lambda x: -x["risk_score"])
            for clause in sorted_clauses:
                lvl = clause["risk_level"]
                if selected_filter != "All" and lvl != selected_filter.lower():
                    continue
                if search and search.lower() not in clause["title"].lower() and search.lower() not in clause["text"].lower():
                    continue

                color = risk_color(lvl)
                with st.expander(f"{clause['title']}  ·  Score: {clause['risk_score']}", expanded=False):
                    st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                          <span class="badge-{lvl}">{lvl.upper()}</span>
                          <span style="font-size:22px;font-family:'Playfair Display';font-weight:900;color:{color}">{clause['risk_score']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    render_risk_bar(clause["risk_score"], lvl)

                    st.markdown('<div class="section-label" style="margin-top:14px">CONTRACT LANGUAGE</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style="border-left:2px solid rgba(255,255,255,0.1);padding-left:12px;font-size:12px;color:#8b8a99;font-style:italic;line-height:1.6">
                          "{clause['text']}"
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown('<div class="section-label" style="margin-top:12px">AI ANALYSIS</div>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size:12px;line-height:1.6">{clause["explanation"]}</p>', unsafe_allow_html=True)

                    st.markdown('<div class="section-label" style="margin-top:12px">RECOMMENDED CHANGES</div>', unsafe_allow_html=True)
                    for sug in clause["suggestions"]:
                        st.markdown(f"""
                            <div style="display:flex;gap:8px;font-size:12px;color:#8b8a99;margin-bottom:5px">
                              <span style="color:#c8a96e;flex-shrink:0">→</span>
                              <span>{sug}</span>
                            </div>
                        """, unsafe_allow_html=True)

    # ─── TAB: AI CHAT ─────────────────────────────────────────────────────────
    with tab_chat:
        st.markdown('<div class="section-label">AI LEGAL ASSISTANT</div>', unsafe_allow_html=True)

        # Starter prompts
        if not st.session_state.chat_history:
            st.markdown('<p style="color:#8b8a99;font-size:13px;margin-bottom:14px">Ask anything about this contract:</p>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            for col, prompt in zip(
                [c1, c2, c3, c4],
                ["What are the biggest risks?", "Give me a negotiation strategy", "Explain the indemnification", "What should I push back on?"],
            ):
                with col:
                    if st.button(prompt, use_container_width=True, key=f"starter_{prompt[:10]}"):
                        st.session_state.chat_history.append({"role": "user", "content": prompt})
                        st.session_state.chat_history.append({"role": "assistant", "content": get_chat_response(prompt)})
                        st.rerun()

        # Chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai"><div class="chat-ai-label">AI ANALYSIS</div>{msg["content"]}</div>', unsafe_allow_html=True)

        # Input
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input("", placeholder="Ask about any clause, risk, or negotiation strategy…", label_visibility="collapsed", key="chat_input")
        with col_send:
            if st.button("Send →", use_container_width=True):
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    with st.spinner("Thinking…"):
                        time.sleep(0.8)
                    st.session_state.chat_history.append({"role": "assistant", "content": get_chat_response(user_input)})
                    st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear conversation", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

    # ─── TAB: VERSIONS ────────────────────────────────────────────────────────
    with tab_versions:
        st.markdown('<div class="section-label">VERSION HISTORY</div>', unsafe_allow_html=True)
        for i, (version_label, risk_score, uploaded_time) in enumerate([
            ("Version 1 — Original", 71, datetime.now().strftime("%-d %b %Y, %H:%M")),
        ]):
            color = risk_color("high")
            st.markdown(f"""
                <div style="display:flex;gap:16px;padding-bottom:20px;position:relative">
                  <div style="display:flex;flex-direction:column;align-items:center">
                    <div style="width:15px;height:15px;border-radius:50%;border:2px solid #c8a96e;background:rgba(200,169,110,0.15)"></div>
                    {'<div style="width:1px;flex:1;background:rgba(255,255,255,0.07);margin-top:4px"></div>' if i == 0 else ''}
                  </div>
                  <div class="lex-card" style="flex:1">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <div>
                        <p style="font-size:13px;font-weight:600;margin-bottom:3px">{version_label}</p>
                        <p style="font-size:11px;color:#8b8a99;font-family:'DM Mono'">{uploaded_time}</p>
                        <p style="font-size:11px;color:#8b8a99;margin-top:4px">{st.session_state.contract_name}</p>
                      </div>
                      <div style="text-align:center">
                        <span style="font-family:'Playfair Display';font-size:28px;font-weight:900;color:{color}">{risk_score}</span>
                        <p style="font-size:9px;color:{color};font-family:'DM Mono';font-weight:700">HIGH RISK</p>
                      </div>
                    </div>
                  </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        st.info("Upload additional contract versions to track risk evolution over drafts.")

    # ─── TAB: COMPARE ─────────────────────────────────────────────────────────
    with tab_compare:
        st.markdown('<div class="section-label">VERSION COMPARISON</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="lex-card" style="text-align:center;padding:40px">
              <div style="font-size:40px;margin-bottom:12px">🔄</div>
              <h3 style="font-family:'Playfair Display';font-size:18px;margin-bottom:8px">Compare Contract Versions</h3>
              <p style="color:#8b8a99;font-size:13px;max-width:360px;margin:0 auto">
                Upload a second version of this contract to compare changes, track risk evolution, and see exactly what changed between drafts.
              </p>
            </div>
        """, unsafe_allow_html=True)

        # Demo comparison (show even with 1 version as preview)
        st.markdown('<div class="section-label" style="margin-top:20px">SAMPLE DIFF PREVIEW</div>', unsafe_allow_html=True)
        demo_changes = [
            {"type": "modified", "title": "Limitation of Liability", "delta": +32, "color": "#ff6b35",
             "old": "Liability is limited to direct damages only.",
             "new": "In no event shall either party be liable for any indirect, incidental, or consequential damages."},
            {"type": "added", "title": "Non-Compete", "delta": +82, "color": "#ff2d55",
             "new": "For 24 months post-termination, you agree not to engage in any competing business within the United States."},
            {"type": "removed", "title": "Arbitration Clause", "delta": -15, "color": "#34c759",
             "old": "All disputes shall be resolved through binding arbitration under AAA rules."},
        ]
        type_icons = {"modified": "~", "added": "+", "removed": "−"}
        type_colors_map = {"modified": "#ffd60a", "added": "#34c759", "removed": "#ff2d55"}

        for ch in demo_changes:
            t = ch["type"]
            tc = type_colors_map[t]
            delta_color = "#ff2d55" if ch["delta"] > 0 else "#34c759"
            delta_str = f"▲ {ch['delta']}" if ch["delta"] > 0 else f"▼ {abs(ch['delta'])}"
            st.markdown(f"""
                <div style="background:#111115;border:1px solid rgba(255,255,255,0.07);border-left:3px solid {tc};border-radius:10px;padding:14px;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px">
                    <span style="background:{tc}22;color:{tc};padding:2px 9px;border-radius:20px;font-size:10px;font-weight:700;font-family:'DM Mono'">{type_icons[t]} {t.upper()}</span>
                    <span style="font-size:13px;font-weight:600;flex:1">{ch['title']}</span>
                    <span style="font-size:12px;font-weight:700;color:{delta_color};font-family:'DM Mono'">{delta_str} risk</span>
                  </div>
                  {'<div style="background:rgba(255,45,85,0.06);border:1px solid rgba(255,45,85,0.15);border-left:2px solid #ff2d55;border-radius:6px;padding:9px;font-size:12px;color:#8b8a99;margin-bottom:6px"><span style="font-size:9px;font-weight:700;letter-spacing:0.08em;color:#4a4958;font-family:DM Mono;display:block;margin-bottom:4px">BEFORE</span>' + ch.get("old", "") + "</div>" if ch.get("old") else ""}
                  {'<div style="background:rgba(52,199,89,0.06);border:1px solid rgba(52,199,89,0.15);border-left:2px solid #34c759;border-radius:6px;padding:9px;font-size:12px;color:#8b8a99"><span style="font-size:9px;font-weight:700;letter-spacing:0.08em;color:#4a4958;font-family:DM Mono;display:block;margin-bottom:4px">AFTER</span>' + ch.get("new", "") + "</div>" if ch.get("new") else ""}
                </div>
            """, unsafe_allow_html=True)