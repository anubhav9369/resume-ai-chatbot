# app.py — ResumeAI Production v2
import os
import json
import fitz  # pymupdf
import streamlit as st
from dotenv import load_dotenv
from src.chatbot import ResumeChatbot
from src.analytics import get_resume_analysis, get_interview_questions, make_groq_client
from src.prompts import STRATEGY_INFO

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ResumeAI — Intelligent Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# CSS — Dark Professional Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #080c14 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0;
}

/* ── Top navbar ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 32px;
    background: rgba(15, 20, 35, 0.95);
    border-bottom: 1px solid #1e2d4a;
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
    margin: -1rem -1rem 0 -1rem;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
}
.nav-badge {
    background: linear-gradient(135deg, #1e3a5f, #1e2d4a);
    border: 1px solid #2563eb44;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    color: #60a5fa;
    font-weight: 500;
}

/* ── Cards ── */
.card {
    background: #0f1520;
    border: 1px solid #1e2d4a;
    border-radius: 16px;
    padding: 24px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #2563eb44; }

.card-accent {
    background: linear-gradient(135deg, #0f1a2e 0%, #0f1520 100%);
    border: 1px solid #2563eb33;
    border-radius: 16px;
    padding: 24px;
}

/* ── Upload zone ── */
.upload-zone {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1428 100%);
    border: 2px dashed #2563eb55;
    border-radius: 20px;
    padding: 40px 32px;
    text-align: center;
    transition: all 0.3s;
}
.upload-zone:hover {
    border-color: #3b82f6;
    background: linear-gradient(135deg, #0d1428 0%, #0f1a2e 100%);
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0f1520 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: #0f1520 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 14px !important;
    padding: 6px 4px !important;
    margin-bottom: 10px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #0d1a30 !important;
    border-color: #1e3a5f !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #0f1520 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #2563eb !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #4f46e5 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px #2563eb44 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Secondary button ── */
.stButton > button[kind="secondary"] {
    background: #0f1520 !important;
    border: 1px solid #1e2d4a !important;
    color: #94a3b8 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #0a0f1e !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid #1e2d4a !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #1e2d4a !important;
    color: #e2e8f0 !important;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    border-radius: 4px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0a0f1e !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 10px !important;
}
details summary {
    color: #64748b !important;
    font-size: 12px !important;
}

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: #0f1520 !important;
    border-color: #1e2d4a !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    background: #0a0f1e !important;
    border: 2px dashed #1e3a5f !important;
    border-radius: 14px !important;
}

/* ── Divider ── */
hr { border-color: #1e2d4a !important; margin: 20px 0 !important; }

/* ── Skill tag ── */
.skill-tag {
    display: inline-block;
    background: #0d1a30;
    color: #60a5fa;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 4px 10px;
    margin: 3px;
    font-size: 12px;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Role tag ── */
.role-tag {
    display: inline-block;
    background: #1a0d30;
    color: #a78bfa;
    border: 1px solid #4c1d95;
    border-radius: 6px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 12px;
    font-weight: 500;
}

/* ── Strength / weakness items ── */
.strength-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 12px;
    background: #0a1f0a;
    border: 1px solid #166534;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 13px;
    color: #86efac;
}
.weakness-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 12px;
    background: #1a0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    margin: 4px 0;
    font-size: 13px;
    color: #fca5a5;
}

/* ── ATS Score ring ── */
.ats-ring {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    font-weight: 700;
    margin: 0 auto 8px auto;
}

/* ── Section label ── */
.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
    display: block;
}

/* ── Strategy pill ── */
.strategy-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0f1520;
    border: 1px solid #1e2d4a;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: #94a3b8;
}

/* ── Question suggestion ── */
.q-suggestion {
    background: #0a0f1e;
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 0;
    font-size: 13px;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
}
.q-suggestion:hover {
    border-color: #2563eb55;
    color: #94a3b8;
    background: #0d1428;
}

/* ── Interview question card ── */
.iq-card {
    background: #0a0f1e;
    border: 1px solid #1e2d4a;
    border-left: 3px solid #4f46e5;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
}

/* ── Hide streamlit chrome ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080c14; }
::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2563eb; }

/* ── Notification banners ── */
[data-testid="stSuccess"] {
    background: #052e16 !important;
    border: 1px solid #166534 !important;
    border-radius: 10px !important;
    color: #86efac !important;
}
[data-testid="stError"] {
    background: #2d0a0a !important;
    border: 1px solid #7f1d1d !important;
    border-radius: 10px !important;
}
[data-testid="stInfo"] {
    background: #0c1a2e !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
}
[data-testid="stWarning"] {
    background: #1c1000 !important;
    border: 1px solid #78350f !important;
    border-radius: 10px !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def extract_pdf(uploaded_file) -> str:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def ats_color(score: int) -> str:
    if score >= 75: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"


def ats_label(score: int) -> str:
    if score >= 75: return "Strong"
    if score >= 50: return "Average"
    return "Needs Work"


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
DEFAULTS = {
    "bot": None,
    "messages": [],
    "analysis": None,
    "interview_qs": [],
    "initialized": False,
    "resume_text": "",
    "active_tab": "chat",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="navbar">
    <div class="nav-logo">
        <span style="font-size:22px;">🧠</span>
        <span>Resume<span style="color:#3b82f6;">AI</span></span>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="nav-badge">LLaMA 3.1 · Groq</span>git add .
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LAYOUT: NOT INITIALIZED → Upload-first centered layout
# ═══════════════════════════════════════════════════════════════
if not st.session_state.initialized:

    # Hero
    st.markdown("""
    <div style="text-align:center; padding: 24px 0 32px 0;">
        <div style="font-size:13px; color:#3b82f6; font-weight:600; letter-spacing:2px;
                    text-transform:uppercase; margin-bottom:12px;">
            AI-Powered Resume Intelligence
        </div>
        <h1 style="font-size:42px; font-weight:700; color:#f1f5f9; margin:0 0 12px 0;
                   line-height:1.2; letter-spacing:-0.5px;">
            Understand Any Resume<br/>
            <span style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);
                         -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Instantly
            </span>
        </h1>
        <p style="color:#64748b; font-size:16px; max-width:480px; margin:0 auto;">
            Upload a PDF resume, choose your AI strategy, and get deep insights
            about any candidate in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main upload card — centered
    left_pad, main_col, right_pad = st.columns([1, 2, 1])
    with main_col:

        st.markdown("<span class='section-label'>📄 Resume Input</span>", unsafe_allow_html=True)
        input_method = st.radio("Input Method", ["📎 Upload PDF", "✏️ Paste Text"], horizontal=True,
                        label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        resume_text = ""
        if "PDF" in input_method:
            uploaded = st.file_uploader("Upload Resume PDF", type=["pdf"], label_visibility="collapsed")
            if uploaded:
                with st.spinner("Extracting text from PDF..."):
                    resume_text = extract_pdf(uploaded)
                word_count = len(resume_text.split())
                st.success(f"✅ PDF loaded — {word_count:,} words extracted")
                with st.expander("Preview extracted text"):
                    st.markdown(f"""
                    <div style="background:#080c14; border:1px solid #1e2d4a; border-radius:10px;
                                padding:16px; font-family:'JetBrains Mono',monospace; font-size:12px;
                                color:#64748b; max-height:200px; overflow-y:auto; white-space:pre-wrap;">
                    {resume_text[:800]}{"..." if len(resume_text) > 800 else ""}
                    </div>""", unsafe_allow_html=True)
        else:
            resume_text = st.text_area("", height=180,
                                       placeholder="Paste resume plain text here...",
                                       label_visibility="collapsed")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<span class='section-label'>🎯 AI Strategy</span>", unsafe_allow_html=True)

        strategy_key = st.selectbox(
            "AI Strategy",
            options=list(STRATEGY_INFO.keys()),
            format_func=lambda x: f"{STRATEGY_INFO[x]['label']} — {STRATEGY_INFO[x]['short']}",
            index=1,
            label_visibility="collapsed"
        )

        info = STRATEGY_INFO[strategy_key]
        st.markdown(f"""
        <div style="background:#0a0f1e; border:1px solid #1e2d4a;
                    border-left:3px solid {info['color']}; border-radius:8px;
                    padding:12px 16px; margin:8px 0 20px 0;">
            <div style="font-size:11px; font-weight:700; color:{info['color']};
                        letter-spacing:0.8px; margin-bottom:4px;">
                {info['badge']}
            </div>
            <div style="font-size:13px; color:#94a3b8; line-height:1.5;">
                {info['desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Analyze Resume", use_container_width=True,
                     disabled=not bool(resume_text.strip())):
            with st.spinner("Running AI analysis..."):
                tmp_path = "/tmp/uploaded_resume.txt"
                with open(tmp_path, "w") as f:
                    f.write(resume_text)

                st.session_state.bot = ResumeChatbot(
                    resume_path=tmp_path, strategy=strategy_key)
                client = make_groq_client()
                st.session_state.analysis = get_resume_analysis(resume_text, client)
                st.session_state.resume_text = resume_text
                st.session_state.initialized = True
                st.session_state.messages = []
            st.rerun()

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # Feature strip
    cols = st.columns(4)
    features = [
        ("📄", "PDF Upload", "Drop any resume PDF"),
        ("⚡", "3 AI Strategies", "Zero-shot to Chain-of-Thought"),
        ("📊", "ATS Scoring", "Resume quality analysis"),
        ("💬", "Deep Q&A", "Ask anything about the candidate"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:20px;">
                <div style="font-size:26px; margin-bottom:8px;">{icon}</div>
                <div style="font-weight:600; color:#e2e8f0; font-size:14px; margin-bottom:4px;">{title}</div>
                <div style="color:#475569; font-size:12px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LAYOUT: INITIALIZED → Full Dashboard
# ═══════════════════════════════════════════════════════════════
else:
    analysis = st.session_state.analysis or {}
    bot = st.session_state.bot

    # ── Top action bar ──
    top_left, top_right = st.columns([3, 1])
    with top_left:
        headline = analysis.get("headline", "Candidate Resume")
        st.markdown(f"""
        <div style="padding:4px 0 16px 0;">
            <div style="font-size:20px; font-weight:700; color:#f1f5f9;">{headline}</div>
        </div>
        """, unsafe_allow_html=True)
    with top_right:
        if st.button("↩ New Resume", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()

    # ── Profile + ATS row ──
    left_col, right_col = st.columns([3, 1])

    with left_col:
        # Skills
        skills = analysis.get("top_strengths", [])
        roles = analysis.get("best_fit_roles", [])
        summary = analysis.get("summary", "")

        if summary:
            st.markdown(f"""
            <div class="card-accent" style="margin-bottom:16px;">
                <span class="section-label">Professional Summary</span>
                <p style="color:#cbd5e1; font-size:14px; line-height:1.7; margin:0;">{summary}</p>
            </div>
            """, unsafe_allow_html=True)

        # Strengths / Gaps side by side
        s_col, w_col = st.columns(2)
        strengths = analysis.get("top_strengths", [])
        weaknesses = analysis.get("areas_for_improvement", [])

        with s_col:
            st.markdown("<span class='section-label'>✅ Top Strengths</span>", unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f"<div class='strength-item'>✓ {s}</div>", unsafe_allow_html=True)

        with w_col:
            st.markdown("<span class='section-label'>⚠ Areas to Improve</span>", unsafe_allow_html=True)
            for w in weaknesses:
                st.markdown(f"<div class='weakness-item'>→ {w}</div>", unsafe_allow_html=True)

        # Best-fit roles
        if roles:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown("<span class='section-label'>🎯 Best-Fit Roles</span>", unsafe_allow_html=True)
            roles_html = "".join([f"<span class='role-tag'>{r}</span>" for r in roles])
            st.markdown(roles_html, unsafe_allow_html=True)

    with right_col:
        # ATS Score
        ats = analysis.get("ats_score", 0)
        ats_c = ats_color(ats)
        ats_l = ats_label(ats)
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:28px 16px;">
            <span class="section-label">ATS Score</span>
            <div class="ats-ring" style="background: conic-gradient({ats_c} {ats*3.6}deg, #1e2d4a 0deg);">
                <div style="width:76px; height:76px; background:#0f1520; border-radius:50%;
                            display:flex; align-items:center; justify-content:center; flex-direction:column;">
                    <span style="font-size:22px; font-weight:800; color:{ats_c};">{ats}</span>
                    <span style="font-size:9px; color:#475569;">/100</span>
                </div>
            </div>
            <div style="color:{ats_c}; font-weight:700; font-size:14px; margin-bottom:8px;">{ats_l}</div>
            <div style="font-size:12px; color:#475569; line-height:1.5;">
                {analysis.get('ats_feedback', '')[:120]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Session stats
        if bot and bot.logs:
            stats = bot.get_stats()
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown("<span class='section-label'>Session Stats</span>", unsafe_allow_html=True)
            st.metric("Queries", stats["total_calls"])
            st.metric("Avg Speed", f"{stats['avg_latency_ms']:.0f}ms")
            st.metric("Total Cost", f"${stats['total_cost_usd']:.5f}")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Tabs: Chat | Interview Prep ──
    tab_chat, tab_interview = st.tabs(["💬  Chat with Resume", "🎤  Interview Prep"])

    # ────────────────────────────────
    # TAB 1: CHAT
    # ────────────────────────────────
    with tab_chat:
        current_strategy = bot.strategy if bot else "few_shot"
        info = STRATEGY_INFO[current_strategy]

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:8px 0 16px 0;">
            <span style="color:#475569; font-size:13px;">
                {len(st.session_state.messages) // 2} questions asked
            </span>
            <span class="strategy-pill">
                Strategy: <strong style="color:{info['color']};">{info['label']}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Suggested questions (shown when no messages yet)
        if not st.session_state.messages:
            st.markdown("<span class='section-label'>💡 Suggested Questions</span>",
                        unsafe_allow_html=True)
            suggestions = [
                "Summarize this candidate's profile in 3 bullet points.",
                "What are the candidate's strongest technical skills?",
                "Would this candidate suit a senior AI/ML engineer role?",
                "What's missing from this resume for a data science role?",
                "Has the candidate worked on any NLP or GenAI projects?",
                "What is their highest level of education?",
            ]
            cols = st.columns(2)
            for i, q in enumerate(suggestions):
                with cols[i % 2]:
                    st.markdown(f"<div class='q-suggestion'>💬 {q}</div>",
                                unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.messages:
            avatar = "🧑‍💻" if msg["role"] == "user" else "🧠"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "meta" in msg:
                    meta = msg["meta"]
                    with st.expander("📊 Query metadata"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Tokens In", meta["tokens_in"])
                        c2.metric("Tokens Out", meta["tokens_out"])
                        c3.metric("Latency", f"{meta['latency_ms']:.0f}ms")
                        c4.metric("Cost", f"${meta['cost_usd']:.6f}")

        # Input
        if prompt := st.chat_input("Ask anything about the candidate..."):
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant", avatar="🧠"):
                with st.spinner("Analyzing..."):
                    answer, log = bot.chat(prompt)
                st.markdown(answer)
                with st.expander("📊 Query metadata"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Tokens In", log.tokens_in)
                    c2.metric("Tokens Out", log.tokens_out)
                    c3.metric("Latency", f"{log.latency_ms:.0f}ms")
                    c4.metric("Cost", f"${log.cost_usd:.6f}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "meta": {
                    "tokens_in": log.tokens_in,
                    "tokens_out": log.tokens_out,
                    "latency_ms": log.latency_ms,
                    "cost_usd": log.cost_usd
                }
            })

        # Clear chat
        if st.session_state.messages:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("🗑 Clear Chat", use_container_width=False):
                st.session_state.messages = []
                bot.reset_history()
                st.rerun()

    # ────────────────────────────────
    # TAB 2: INTERVIEW PREP
    # ────────────────────────────────
    with tab_interview:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        role_col, btn_col = st.columns([3, 1])
        with role_col:
            target_role = st.text_input(
                "Target Role",
                value="AI Engineer",
                placeholder="e.g. Senior Data Scientist, ML Engineer, GenAI Engineer",
                label_visibility="visible"
            )
        with btn_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            gen_btn = st.button("Generate Questions", use_container_width=True)

        if gen_btn:
            with st.spinner(f"Generating interview questions for {target_role}..."):
                client = make_groq_client()
                st.session_state.interview_qs = get_interview_questions(
                    st.session_state.resume_text, target_role, client
                )

        if st.session_state.interview_qs:
            st.markdown(f"""
            <div style="margin:16px 0 8px 0;">
                <span class="section-label">
                    {len(st.session_state.interview_qs)} Interview Questions for {target_role}
                </span>
            </div>
            """, unsafe_allow_html=True)

            for i, q in enumerate(st.session_state.interview_qs, 1):
                with st.expander(f"Q{i}: {q.get('question', '')[:80]}..."):
                    st.markdown(f"""
                    <div class="iq-card">
                        <div style="font-size:15px; font-weight:600; color:#e2e8f0; margin-bottom:12px;">
                            {q.get('question', '')}
                        </div>
                        <div style="margin-bottom:10px;">
                            <span style="font-size:11px; font-weight:700; color:#64748b;
                                         text-transform:uppercase; letter-spacing:0.8px;">
                                WHY WE ASK
                            </span>
                            <p style="color:#94a3b8; font-size:13px; margin:4px 0 0 0;">
                                {q.get('reason', '')}
                            </p>
                        </div>
                        <div>
                            <span style="font-size:11px; font-weight:700; color:#64748b;
                                         text-transform:uppercase; letter-spacing:0.8px;">
                                STRONG ANSWER INCLUDES
                            </span>
                            <p style="color:#86efac; font-size:13px; margin:4px 0 0 0;">
                                {q.get('strong_answer_hints', '')}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:48px; color:#334155;">
                <div style="font-size:32px; margin-bottom:8px;">🎤</div>
                <div style="font-size:14px;">
                    Enter a target role and click Generate Questions
                </div>
            </div>
            """, unsafe_allow_html=True)