"""
app.py — Multimodal Math Mentor (Slothpilot-style Chatbot UI)

Run:  streamlit run app.py
"""

import os
import json
import time
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Math Mentor · AI Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Slothpilot-style CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --brand:         #6C63FF;
    --brand-light:   #8B85FF;
    --brand-lighter: #E8E6FF;
    --brand-bg:      #F0EEFF;
    --bg-white:      #FFFFFF;
    --bg-page:       #F7F7FB;
    --bg-user-msg:   linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%);
    --bg-bot-msg:    #F2F2F7;
    --text-dark:     #1A1A2E;
    --text-medium:   #4A4A68;
    --text-light:    #8E8EA0;
    --text-on-brand: #FFFFFF;
    --border-light:  #E8E8F0;
    --border-medium: #D5D5E0;
    --shadow-sm:     0 1px 3px rgba(0,0,0,0.06);
    --shadow-md:     0 4px 12px rgba(0,0,0,0.08);
    --radius-sm:     8px;
    --radius-md:     12px;
    --radius-lg:     16px;
    --radius-xl:     20px;
    --radius-pill:   100px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Main background ── */
[data-testid="stAppViewContainer"] { background: var(--bg-page) !important; }
[data-testid="stHeader"] { background: var(--bg-white) !important; border-bottom: 1px solid var(--border-light); box-shadow: var(--shadow-sm); }
[data-testid="stMainBlockContainer"] { max-width: 860px; margin: 0 auto; padding-top: 0.5rem; }
[data-testid="stBottomBlockContainer"] { background: var(--bg-page) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: var(--bg-white) !important; border-right: 1px solid var(--border-light) !important; }
section[data-testid="stSidebar"] * { color: var(--text-medium) !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5 { color: var(--text-dark) !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border-light) !important; }

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    border-radius: var(--radius-lg) !important;
    margin-bottom: 0.8rem;
    padding: 1rem 1.3rem !important;
    animation: slideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    border: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--bg-user-msg) !important;
    margin-left: 4rem;
    box-shadow: 0 4px 16px rgba(108,99,255,0.25);
    border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) *,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div {
    color: var(--text-on-brand) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: var(--bg-bot-msg) !important;
    margin-right: 4rem;
    box-shadow: var(--shadow-sm);
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) span,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li {
    color: var(--text-dark) !important;
}
@keyframes slideIn {
    0%   { opacity:0; transform: translateY(12px); }
    100% { opacity:1; transform: translateY(0); }
}

/* ── Chat Input ── */
[data-testid="stChatInput"] { border-top: 1px solid var(--border-light) !important; }
[data-testid="stChatInput"] textarea {
    background: var(--bg-white) !important;
    border: 2px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-dark) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.12) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-light) !important; }
[data-testid="stChatInput"] button {
    background: var(--brand) !important; border: none !important;
    border-radius: var(--radius-sm) !important; color: white !important;
}

/* ── Expanders ── */
details {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    margin: 0.35rem 0 !important;
    box-shadow: var(--shadow-sm);
}
details:hover { border-color: var(--brand-lighter) !important; }
details summary span { font-weight: 500 !important; font-size: 0.84rem !important; color: var(--text-medium) !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important; font-size: 0.86rem !important;
    border: 1px solid var(--border-light) !important;
    background: var(--bg-white) !important;
    color: var(--text-dark) !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    border-color: var(--brand) !important; color: var(--brand) !important;
    transform: translateY(-1px) !important; box-shadow: var(--shadow-md) !important;
}
.stButton > button[kind="primary"] {
    background: var(--brand) !important; border: none !important;
    color: white !important; box-shadow: 0 4px 12px rgba(108,99,255,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--brand-light) !important; box-shadow: 0 6px 20px rgba(108,99,255,0.35) !important;
}

/* ── Progress bar ── */
div[data-testid="stProgress"] > div { background: var(--border-light) !important; border-radius: 20px !important; }
div[data-testid="stProgress"] > div > div { background: var(--brand) !important; }

/* ── Status ── */
[data-testid="stStatusWidget"] {
    background: var(--bg-white) !important; border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
}

/* ═══════════ CUSTOM COMPONENTS ═══════════ */

/* Top nav */
.mm-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.7rem 1.2rem; background: var(--bg-white);
    border: 1px solid var(--border-light); border-radius: var(--radius-lg);
    margin-bottom: 0.8rem; box-shadow: var(--shadow-sm);
}
.mm-topbar-brand { display: flex; align-items: center; gap: 0.6rem; }
.mm-topbar-logo {
    width: 36px; height: 36px; border-radius: 10px; background: var(--brand);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; color: white; box-shadow: 0 2px 8px rgba(108,99,255,0.3);
}
.mm-topbar-title { font-size: 1.1rem; font-weight: 700; color: var(--text-dark); }
.mm-topbar-badges { display: flex; gap: 0.5rem; align-items: center; }
.mm-topbar-badge {
    padding: 0.3rem 0.8rem; border-radius: var(--radius-pill);
    font-size: 0.72rem; font-weight: 600;
    background: var(--brand-bg); color: var(--brand); border: 1px solid var(--brand-lighter);
}

/* Input mode bar */
.mm-input-bar {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0; margin-bottom: 0.4rem;
}
.mm-mode-btn {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.45rem 1rem; border-radius: var(--radius-pill);
    font-size: 0.82rem; font-weight: 600;
    cursor: pointer; transition: all 0.2s ease;
    border: 2px solid var(--border-light);
    background: var(--bg-white); color: var(--text-medium);
}
.mm-mode-btn:hover {
    border-color: var(--brand); color: var(--brand); transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}
.mm-mode-btn.active {
    background: var(--brand); color: white; border-color: var(--brand);
    box-shadow: 0 4px 12px rgba(108,99,255,0.25);
}

/* Audio recorder container */
.mm-recorder {
    background: var(--bg-white); border: 2px solid var(--brand-lighter);
    border-radius: var(--radius-lg); padding: 1.2rem 1.5rem;
    margin: 0.5rem 0; box-shadow: var(--shadow-md);
    text-align: center;
}
.mm-recorder-title { font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; }
.mm-recorder-hint { font-size: 0.78rem; color: var(--text-light); margin-top: 0.4rem; }

/* Photo upload container */
.mm-upload-zone {
    background: var(--bg-white); border: 2px dashed var(--brand-lighter);
    border-radius: var(--radius-lg); padding: 1.2rem 1.5rem;
    margin: 0.5rem 0; text-align: center;
}
.mm-upload-title { font-weight: 600; color: var(--text-dark); margin-bottom: 0.3rem; }
.mm-upload-hint { font-size: 0.78rem; color: var(--text-light); }

/* Answer card */
.mm-answer {
    background: var(--bg-white); border: 2px solid var(--brand-lighter);
    border-radius: var(--radius-lg); padding: 1.2rem 1.4rem;
    margin: 0.6rem 0; box-shadow: var(--shadow-md);
    position: relative; overflow: hidden;
}
.mm-answer::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--brand), var(--brand-light), #22d3ee);
}
.mm-answer-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: var(--brand); margin-bottom: 0.35rem; }
.mm-answer-value { font-size: 1.3rem; font-weight: 700; color: var(--text-dark); line-height: 1.4; }
.mm-conf {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.28rem 0.85rem; border-radius: var(--radius-pill);
    font-size: 0.76rem; font-weight: 600; margin-top: 0.6rem;
}
.mm-conf-high { background: #E6F9F0; color: #059669; border: 1px solid #A7F3D0; }
.mm-conf-mid  { background: #FEF9E7; color: #D97706; border: 1px solid #FDE68A; }
.mm-conf-low  { background: #FEE2E2; color: #DC2626; border: 1px solid #FECACA; }

/* Meta pills */
.mm-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.6rem 0; }
.mm-pill {
    display: inline-flex; align-items: center; gap: 0.25rem;
    padding: 0.2rem 0.65rem; border-radius: var(--radius-pill);
    font-size: 0.72rem; font-weight: 500;
    background: var(--bg-page); border: 1px solid var(--border-light); color: var(--text-medium);
}
.mm-pill b { color: var(--text-dark); font-weight: 600; }

/* Trace */
.mm-trace {
    display: flex; align-items: center; gap: 0.65rem;
    padding: 0.5rem 0.85rem; border-radius: var(--radius-sm);
    margin: 0.2rem 0; font-size: 0.82rem;
    background: var(--bg-page); border-left: 3px solid; transition: all 0.2s ease;
}
.mm-trace:hover { background: var(--brand-bg); }
.mm-trace-name { font-weight: 600; min-width: 120px; }
.mm-trace-status { color: var(--text-light); font-size: 0.78rem; }

/* RAG */
.mm-rag {
    background: var(--bg-page); border: 1px solid var(--border-light);
    border-radius: var(--radius-sm); padding: 0.55rem 0.8rem;
    margin: 0.2rem 0; font-size: 0.8rem; color: var(--text-medium); transition: all 0.2s ease;
}
.mm-rag:hover { border-color: var(--brand-lighter); background: var(--brand-bg); }
.mm-rag-source { font-weight: 600; color: var(--brand); }
.mm-rag-score { float: right; font-size: 0.72rem; color: var(--text-light); font-family: 'JetBrains Mono', monospace; }

/* HITL */
.mm-hitl { background: #FFFBEB; border: 2px solid #F59E0B; border-radius: var(--radius-md); padding: 1.1rem 1.3rem; margin: 0.8rem 0; }

/* Welcome */
.mm-welcome-text { text-align: center; padding: 2rem 0 0.8rem; color: var(--text-light); font-size: 0.95rem; }
.mm-examples { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.7rem; margin: 0 auto; max-width: 600px; }
@media (max-width: 600px) { .mm-examples { grid-template-columns: 1fr; } }
.mm-ex-card { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1rem 1.1rem; transition: all 0.25s ease; box-shadow: var(--shadow-sm); }
.mm-ex-card:hover { border-color: var(--brand); box-shadow: 0 6px 20px rgba(108,99,255,0.12); transform: translateY(-3px); }
.mm-ex-emoji { font-size: 1.5rem; }
.mm-ex-title { font-weight: 600; color: var(--text-dark); font-size: 0.88rem; margin-top: 0.4rem; }
.mm-ex-desc { color: var(--text-light); font-size: 0.76rem; margin-top: 0.1rem; font-family: 'JetBrains Mono', monospace; }

/* Explanation header */
.mm-exp-header { display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem; font-weight: 700; color: var(--text-dark); margin: 0.7rem 0 0.4rem; padding-bottom: 0.35rem; border-bottom: 2px solid var(--brand-lighter); }
.mm-hr { border: none; border-top: 1px solid var(--border-light); margin: 0.7rem 0; }

/* Sidebar */
.mm-label { font-size: 0.66rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: var(--text-light) !important; margin: 0.7rem 0 0.3rem; }
.mm-sb-brand { display: flex; align-items: center; gap: 0.6rem; padding-bottom: 0.6rem; }
.mm-sb-logo { width: 38px; height: 38px; border-radius: 10px; background: var(--brand); display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: white; box-shadow: 0 2px 8px rgba(108,99,255,0.3); }
.mm-sb-name { font-size: 1.05rem !important; font-weight: 700 !important; color: var(--text-dark) !important; }
.mm-sb-sub { font-size: 0.7rem !important; color: var(--text-light) !important; margin-top: -2px; }
.mm-stats { display: flex; gap: 0.4rem; margin: 0.3rem 0 0.5rem; }
.mm-stat { flex: 1; background: var(--bg-page); border: 1px solid var(--border-light); border-radius: var(--radius-sm); padding: 0.5rem 0.4rem; text-align: center; }
.mm-stat-val { font-size: 1.15rem; font-weight: 700; color: var(--text-dark) !important; }
.mm-stat-lbl { font-size: 0.62rem; color: var(--text-light) !important; text-transform: uppercase; letter-spacing: 0.5px; }
.mm-hist { padding: 0.35rem 0.5rem; border-radius: var(--radius-sm); font-size: 0.78rem; color: var(--text-medium) !important; margin: 0.1rem 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mm-hist:hover { background: var(--brand-bg); }
.mm-sympy { display: inline-flex; align-items: center; gap: 0.3rem; background: #E6F9F0; border: 1px solid #A7F3D0; border-radius: var(--radius-pill); padding: 0.22rem 0.75rem; font-size: 0.76rem; font-weight: 500; color: #059669; margin: 0.3rem 0; }
.mm-time { font-size: 0.68rem; color: var(--text-light); text-align: right; margin-top: 0.3rem; opacity: 0.7; }
.mm-time-user { color: rgba(255,255,255,0.65); }
.mm-footer { text-align: center; padding: 1.2rem 0 0.5rem; font-size: 0.72rem; color: var(--text-light); }

/* Transcript box */
.mm-transcript {
    background: var(--brand-bg); border: 1px solid var(--brand-lighter);
    border-radius: var(--radius-md); padding: 0.8rem 1rem;
    margin: 0.5rem 0; font-size: 0.88rem; color: var(--text-dark);
}
.mm-transcript-label { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--brand); margin-bottom: 0.25rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "text"
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = None


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="mm-sb-brand">
        <div class="mm-sb-logo">🧮</div>
        <div>
            <div class="mm-sb-name">Math Mentor</div>
            <div class="mm-sb-sub">Gemini 2.5 Flash · 5 Agents</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API Key
    st.markdown('<div class="mm-label">🔑 API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""),
        type="password", label_visibility="collapsed", placeholder="Enter your Gemini API key"
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        st.markdown('<span style="color:#059669;font-size:0.75rem;">✓ Key set</span>', unsafe_allow_html=True)

    st.divider()

    # Knowledge Base
    st.markdown('<div class="mm-label">📚 Knowledge Base</div>', unsafe_allow_html=True)
    if st.button("Build / Rebuild RAG Index", use_container_width=True):
        if not api_key:
            st.error("Set API key first!")
        else:
            with st.spinner("Embedding documents…"):
                from rag import build_vectorstore
                ok = build_vectorstore(api_key)
                st.success("✓ Index built!" if ok else "Using keyword search")

    from rag import FAISS_INDEX_PATH
    if (FAISS_INDEX_PATH / "index.faiss").exists():
        st.markdown('<span style="color:#059669;font-size:0.75rem;">✓ Vector index ready</span>', unsafe_allow_html=True)
    else:
        st.caption("ℹ️ Build index for better results")

    st.divider()

    # Stats
    st.markdown('<div class="mm-label">📊 Stats</div>', unsafe_allow_html=True)
    from memory import get_stats, get_all_problems
    stats = get_stats()
    st.markdown(f"""
    <div class="mm-stats">
        <div class="mm-stat"><div class="mm-stat-val">{stats['total']}</div><div class="mm-stat-lbl">Solved</div></div>
        <div class="mm-stat"><div class="mm-stat-val">{stats['correct']}</div><div class="mm-stat-lbl">Correct</div></div>
        <div class="mm-stat"><div class="mm-stat-val">{stats['incorrect']}</div><div class="mm-stat-lbl">Wrong</div></div>
    </div>
    """, unsafe_allow_html=True)
    if stats["total"] > 0:
        accuracy = int(100 * stats["correct"] / max(stats["total"] - stats["unevaluated"], 1))
        st.progress(min(accuracy, 100) / 100, text=f"Accuracy: {accuracy}%")
    if stats["topics"]:
        st.caption("Topics: " + " · ".join(f"{t} ({c})" for t, c in list(stats["topics"].items())[:5]))

    st.divider()

    # Recent Chats
    st.markdown('<div class="mm-label">📜 Recent Chats</div>', unsafe_allow_html=True)
    history = get_all_problems(limit=7)
    if history:
        for h in history:
            emoji = "✅" if h["feedback"] == "correct" else "❌" if h["feedback"] == "incorrect" else "⏳"
            st.markdown(f'<div class="mm-hist">{emoji} <b>[{h["topic"] or "?"}]</b> {h["input_text"][:35]}…</div>', unsafe_allow_html=True)
    else:
        st.caption("No problems solved yet")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_mode = "text"
        st.session_state.extracted_text = None
        st.session_state.transcript_text = None
        for key in ["hitl_approved"]:
            st.session_state.pop(key, None)
        st.rerun()


# ─────────────────────────────────────────────
# Top navbar
# ─────────────────────────────────────────────
st.markdown("""
<div class="mm-topbar">
    <div class="mm-topbar-brand">
        <div class="mm-topbar-logo">🧮</div>
        <div class="mm-topbar-title">Math Mentor</div>
    </div>
    <div class="mm-topbar-badges">
        <span class="mm-topbar-badge">5 Agents</span>
        <span class="mm-topbar-badge">RAG</span>
        <span class="mm-topbar-badge">HITL</span>
        <span class="mm-topbar-badge">Memory</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Welcome
# ─────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="mm-welcome-text">
        Hello! I'm your personal AI Math Tutor.<br>
        Choose your input mode below — type, snap a photo, or speak!
    </div>
    <div class="mm-examples">
        <div class="mm-ex-card"><div class="mm-ex-emoji">📝</div><div class="mm-ex-title">Solve an equation</div><div class="mm-ex-desc">Solve 2x² − 5x + 3 = 0</div></div>
        <div class="mm-ex-card"><div class="mm-ex-emoji">📊</div><div class="mm-ex-title">Probability</div><div class="mm-ex-desc">P(both red) from 3R + 5B balls</div></div>
        <div class="mm-ex-card"><div class="mm-ex-emoji">∫</div><div class="mm-ex-title">Calculus</div><div class="mm-ex-desc">d/dx [x³·sin(x)]</div></div>
        <div class="mm-ex-card"><div class="mm-ex-emoji">🔢</div><div class="mm-ex-title">Linear Algebra</div><div class="mm-ex-desc">Eigenvalues of [[2,1],[1,2]]</div></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def render_assistant(msg, is_latest=False):
    if msg.get("answer_html"):
        st.markdown(msg["answer_html"], unsafe_allow_html=True)
    if msg.get("meta_html"):
        st.markdown(msg["meta_html"], unsafe_allow_html=True)
    if msg.get("explanation"):
        st.markdown('<hr class="mm-hr">', unsafe_allow_html=True)
        st.markdown('<div class="mm-exp-header">📖 Step‑by‑Step Explanation</div>', unsafe_allow_html=True)
        st.markdown(msg["explanation"])
    if msg.get("sympy_verified"):
        st.markdown(f'<div class="mm-sympy">✓ SymPy verified: {msg["sympy_answer"]}</div>', unsafe_allow_html=True)
    if msg.get("practice_hint"):
        st.info(f"🎯 **Try this next:** {msg['practice_hint']}")
    if msg.get("trace"):
        with st.expander("🔍 Agent Trace", expanded=False):
            colors = {"Memory":"#F59E0B","Parser Agent":"#6C63FF","RAG Retrieval":"#06B6D4","Intent Router":"#A855F7","Solver Agent":"#10B981","Verifier Agent":"#EF4444","Explainer Agent":"#64748B"}
            for step in msg["trace"]:
                name = step.get("agent","Agent")
                clr = colors.get(name,"#64748B")
                st.markdown(f'<div class="mm-trace" style="border-left-color:{clr}"><span class="mm-trace-name" style="color:{clr}">{name}</span><span class="mm-trace-status">{step.get("status","")}</span></div>', unsafe_allow_html=True)
    if msg.get("rag_chunks"):
        with st.expander(f"📚 Knowledge Sources ({len(msg['rag_chunks'])})", expanded=False):
            for i, chunk in enumerate(msg["rag_chunks"], 1):
                score = chunk.get("similarity_score", 0)
                st.markdown(f'<div class="mm-rag"><span class="mm-rag-score">{score:.3f}</span><span class="mm-rag-source">Source {i}: {chunk["source"]}</span><br>{chunk["content"][:200]}…</div>', unsafe_allow_html=True)
    if msg.get("key_formulas"):
        with st.expander("📌 Key Formulas", expanded=False):
            for f in msg["key_formulas"]:
                st.markdown(f"- `{f}`")
    if msg.get("common_mistakes"):
        with st.expander("⚠️ Common Mistakes", expanded=False):
            for m in msg["common_mistakes"]:
                st.markdown(f"• {m}")
    if msg.get("solution_steps"):
        with st.expander("📐 Full Solution Working", expanded=False):
            for i, step in enumerate(msg["solution_steps"], 1):
                st.markdown(f"**Step {i}:** {step}")
    if msg.get("show_feedback") and is_latest:
        st.markdown('<hr class="mm-hr">', unsafe_allow_html=True)
        st.caption("Was this solution correct?")
        fc1, fc2, fc3 = st.columns([1, 1, 3])
        with fc1:
            if st.button("✅ Correct", key=f"fb_ok_{id(msg)}", use_container_width=True, type="primary"):
                _save_fb(msg, "correct"); msg["show_feedback"] = False
                st.toast("Saved as correct! 🎉", icon="✅"); st.rerun()
        with fc2:
            if st.button("❌ Wrong", key=f"fb_no_{id(msg)}", use_container_width=True):
                _save_fb(msg, "incorrect"); msg["show_feedback"] = False
                st.toast("Saved as incorrect!", icon="📝"); st.rerun()
    if msg.get("hitl_needed") and not st.session_state.get("hitl_approved"):
        st.markdown('<div class="mm-hitl">', unsafe_allow_html=True)
        st.markdown("#### 🧑‍💼 Human Review Required")
        st.write(f"**Reason:** {msg.get('hitl_reason', 'Low confidence')}")
        hc1, hc2 = st.columns(2)
        with hc1:
            if st.button("✅ Approve", key="hitl_ok", use_container_width=True, type="primary"):
                st.session_state.hitl_approved = True; st.rerun()
        with hc2:
            if st.button("✏️ Re‑solve", key="hitl_redo", use_container_width=True):
                st.session_state.messages.pop(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def _save_fb(msg, feedback):
    from memory import save_problem
    r = msg.get("_result", {})
    save_problem(input_text=r.get("raw_input",""), input_type=r.get("input_type","text"),
        parsed=r.get("parsed",{}), answer=r.get("final_answer",""),
        explanation=r.get("explanation",{}).get("explanation",""),
        confidence=r.get("confidence",0), feedback=feedback,
        rag_sources=[c.get("source","") for c in r.get("rag_chunks",[])])


def solve_problem(raw_input, input_type, api_key, display_text=None):
    """Run the pipeline and add messages to chat."""
    now = datetime.now().strftime("%H:%M")

    # User message
    user_msg = {"role": "user", "avatar": "👤", "text": display_text or raw_input, "timestamp": now}
    st.session_state.messages.append(user_msg)

    with st.chat_message("user", avatar="👤"):
        st.markdown(display_text or raw_input)
        st.markdown(f'<div class="mm-time mm-time-user">{now} ✓✓</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🧮"):
        with st.status("Solving your problem…", expanded=True) as status:
            for icon, text in [("🧠","Searching memory…"),("📝","Agent 1 · Parsing…"),("📚","Retrieving knowledge…"),("🔀","Agent 2 · Routing…"),("⚡","Agent 3 · Solving…"),("✅","Agent 4 · Verifying…"),("📖","Agent 5 · Explaining…")]:
                st.write(f"{icon}  {text}"); time.sleep(0.05)
            try:
                from orchestration.workflow import run_pipeline
                result = run_pipeline(raw_input, input_type, api_key)
                status.update(label="✅ Solution ready!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Pipeline error: {str(e)}"); st.exception(e); st.stop()

        parsed = result.get("parsed",{})
        solution = result.get("solution",{})
        verification = result.get("verification",{})
        explanation_data = result.get("explanation",{})
        confidence = result.get("confidence",0)
        verdict = verification.get("verdict","uncertain")
        conf_cls = "mm-conf-high" if confidence >= 80 else "mm-conf-mid" if confidence >= 60 else "mm-conf-low"
        conf_icon = "🟢" if confidence >= 80 else "🟡" if confidence >= 60 else "🔴"

        answer_html = f'<div class="mm-answer"><div class="mm-answer-label">Answer</div><div class="mm-answer-value">{result.get("final_answer","See explanation below")}</div><div class="mm-conf {conf_cls}">{conf_icon} Confidence: {confidence}% · {verdict}</div></div>'
        topic = parsed.get("topic","unknown").title()
        subtopic = parsed.get("subtopic","")
        route = result.get("routing",{}).get("route","")
        difficulty = result.get("routing",{}).get("difficulty","")
        meta_html = f'<div class="mm-meta"><span class="mm-pill">📊 <b>{topic}</b></span><span class="mm-pill">{subtopic}</span><span class="mm-pill">⚙️ {route}</span><span class="mm-pill">📈 {difficulty}</span></div>'
        exp_text = explanation_data.get("explanation","No explanation generated.")
        practice = explanation_data.get("similar_problem_hint","")

        st.markdown(answer_html, unsafe_allow_html=True)
        st.markdown(meta_html, unsafe_allow_html=True)
        st.markdown('<hr class="mm-hr">', unsafe_allow_html=True)
        st.markdown('<div class="mm-exp-header">📖 Step‑by‑Step Explanation</div>', unsafe_allow_html=True)
        st.markdown(exp_text)
        if solution.get("sympy_verified"):
            st.markdown(f'<div class="mm-sympy">✓ SymPy verified: {solution.get("sympy_answer")}</div>', unsafe_allow_html=True)
        if practice:
            st.info(f"🎯 **Try this next:** {practice}")
        st.markdown(f'<div class="mm-time">{now} ✓✓</div>', unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", "avatar": "🧮",
            "answer_html": answer_html, "meta_html": meta_html,
            "explanation": exp_text, "trace": result.get("trace",[]),
            "rag_chunks": result.get("rag_chunks",[]),
            "key_formulas": explanation_data.get("key_formulas",[]),
            "common_mistakes": explanation_data.get("common_mistakes",[]),
            "solution_steps": solution.get("solution_steps",[]),
            "practice_hint": practice,
            "sympy_verified": solution.get("sympy_verified",False),
            "sympy_answer": solution.get("sympy_answer",""),
            "show_feedback": True,
            "hitl_needed": result.get("hitl_needed",False),
            "hitl_reason": result.get("hitl_reason",""),
            "timestamp": now, "_result": result,
        })
    st.rerun()


# ─────────────────────────────────────────────
# Render chat history
# ─────────────────────────────────────────────
for idx, msg in enumerate(st.session_state.messages):
    is_last = (idx == len(st.session_state.messages) - 1)
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        if msg["role"] == "user":
            if msg.get("text"):
                st.markdown(msg["text"])
            if msg.get("image"):
                st.image(msg["image"], caption="📷 Attached image", use_container_width=True)
            if msg.get("timestamp"):
                st.markdown(f'<div class="mm-time mm-time-user">{msg["timestamp"]} ✓✓</div>', unsafe_allow_html=True)
        else:
            render_assistant(msg, is_latest=is_last)
            if msg.get("timestamp"):
                st.markdown(f'<div class="mm-time">{msg["timestamp"]} ✓✓</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Input Mode Selector — Three tabs: Text / Photo / Audio
# ─────────────────────────────────────────────
st.markdown("---")

mode_col1, mode_col2, mode_col3, mode_spacer = st.columns([1, 1, 1, 3])
with mode_col1:
    if st.button("✍️ Text", use_container_width=True,
                 type="primary" if st.session_state.input_mode == "text" else "secondary"):
        st.session_state.input_mode = "text"
        st.session_state.extracted_text = None
        st.session_state.transcript_text = None
        st.rerun()
with mode_col2:
    if st.button("📷 Photo", use_container_width=True,
                 type="primary" if st.session_state.input_mode == "photo" else "secondary"):
        st.session_state.input_mode = "photo"
        st.session_state.transcript_text = None
        st.rerun()
with mode_col3:
    if st.button("🎙️ Audio", use_container_width=True,
                 type="primary" if st.session_state.input_mode == "audio" else "secondary"):
        st.session_state.input_mode = "audio"
        st.session_state.extracted_text = None
        st.rerun()


# ─────────────────────────────────────────────
# TEXT MODE
# ─────────────────────────────────────────────
if st.session_state.input_mode == "text":
    user_input = st.chat_input(
        "Message to Math Mentor…" if api_key else "Set API key in the sidebar first",
        disabled=not api_key
    )
    if not api_key:
        st.info("👈 Enter your **Gemini API key** in the sidebar to start.")
    if user_input and api_key:
        solve_problem(user_input, "text", api_key)


# ─────────────────────────────────────────────
# PHOTO MODE
# ─────────────────────────────────────────────
elif st.session_state.input_mode == "photo":
    st.markdown("""
    <div class="mm-upload-zone">
        <div class="mm-upload-title">📷 Upload a math problem image</div>
        <div class="mm-upload-hint">Handwritten notes, textbook pages, or screenshots</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_img = st.file_uploader(
        "Upload image", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed", key="photo_upload"
    )

    if uploaded_img:
        img_col1, img_col2 = st.columns([1, 1])
        with img_col1:
            st.image(uploaded_img, caption="Uploaded image", use_container_width=True)
        with img_col2:
            if st.button("🔍 Extract Text", use_container_width=True, type="primary"):
                if not api_key:
                    st.error("Set API key first!")
                else:
                    with st.spinner("Extracting text with Gemini Vision…"):
                        from agents import extract_from_image
                        result = extract_from_image(uploaded_img.getvalue())
                        st.session_state.extracted_text = result["text"]
                        st.session_state.extraction_confidence = result["confidence"]
                        st.rerun()

        if st.session_state.extracted_text:
            conf = st.session_state.get("extraction_confidence", 100)
            st.markdown(f"""
            <div class="mm-transcript">
                <div class="mm-transcript-label">Extracted Text · Confidence: {conf}%</div>
                {st.session_state.extracted_text}
            </div>
            """, unsafe_allow_html=True)

            if conf < 70:
                st.warning("⚠️ Low confidence — you can edit below before solving.")

            edited_text = st.text_area(
                "Edit extracted text (if needed):",
                value=st.session_state.extracted_text,
                height=80, label_visibility="collapsed"
            )

            if st.button("🚀 Solve This Problem", use_container_width=True, type="primary"):
                if not api_key:
                    st.error("Set API key first!")
                else:
                    solve_problem(edited_text, "image", api_key,
                                  display_text=f"📷 [From image]:\n{edited_text}")


# ─────────────────────────────────────────────
# AUDIO MODE — Live microphone recording
# ─────────────────────────────────────────────
elif st.session_state.input_mode == "audio":
    st.markdown("""
    <div class="mm-recorder">
        <div class="mm-recorder-title">🎙️ Record your math problem</div>
        <div class="mm-recorder-hint">Click the mic button below, speak your problem clearly, then stop recording</div>
    </div>
    """, unsafe_allow_html=True)

    # Live microphone recording
    audio_data = st.audio_input(
        "🎙️ Click to start recording",
        key="mic_input"
    )

    if audio_data:
        st.audio(audio_data)

        if st.button("📝 Transcribe & Solve", use_container_width=True, type="primary"):
            if not api_key:
                st.error("Set API key first!")
            else:
                with st.spinner("Transcribing audio…"):
                    from agents import transcribe_audio
                    result = transcribe_audio(audio_data.getvalue(), "recording.wav")
                    transcript = result["text"]
                    confidence = result["confidence"]

                st.session_state.transcript_text = transcript
                st.session_state.transcript_confidence = confidence

                st.markdown(f"""
                <div class="mm-transcript">
                    <div class="mm-transcript-label">Transcript · Confidence: {confidence}%</div>
                    {transcript}
                </div>
                """, unsafe_allow_html=True)

                if confidence < 70:
                    st.warning("⚠️ Low transcription confidence — edit below before solving.")

                st.rerun()

    # Show transcript if we have it
    if st.session_state.transcript_text:
        conf = st.session_state.get("transcript_confidence", 100)
        st.markdown(f"""
        <div class="mm-transcript">
            <div class="mm-transcript-label">Transcript · Confidence: {conf}%</div>
            {st.session_state.transcript_text}
        </div>
        """, unsafe_allow_html=True)

        edited_transcript = st.text_area(
            "Edit transcript (if needed):",
            value=st.session_state.transcript_text,
            height=80, label_visibility="collapsed"
        )

        if st.button("🚀 Solve This Problem", use_container_width=True, type="primary", key="solve_audio"):
            if not api_key:
                st.error("Set API key first!")
            else:
                solve_problem(edited_transcript, "audio", api_key,
                              display_text=f"🎙️ [From audio]:\n{edited_transcript}")

    # Also allow file upload as fallback
    with st.expander("📁 Or upload an audio file", expanded=False):
        uploaded_audio = st.file_uploader(
            "Upload audio", type=["wav", "mp3", "m4a", "ogg", "webm"],
            label_visibility="collapsed", key="audio_file_upload"
        )
        if uploaded_audio:
            st.audio(uploaded_audio)
            if st.button("📝 Transcribe Uploaded Audio", use_container_width=True, type="primary"):
                if not api_key:
                    st.error("Set API key first!")
                else:
                    with st.spinner("Transcribing…"):
                        from agents import transcribe_audio
                        result = transcribe_audio(uploaded_audio.getvalue(), uploaded_audio.name)
                        st.session_state.transcript_text = result["text"]
                        st.session_state.transcript_confidence = result["confidence"]
                        st.rerun()


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
if st.session_state.messages:
    st.markdown(
        '<div class="mm-footer">Math Mentor · Powered by Google Gemini · FAISS RAG · 5 Agents · HITL · Memory</div>',
        unsafe_allow_html=True
    )
