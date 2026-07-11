import os
import uuid
import base64
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic model is optional — if it can't load, we fall back to keyword search.
try:
    from sentence_transformers import SentenceTransformer
    HAS_SEMANTIC = True
except Exception:
    HAS_SEMANTIC = False

load_dotenv()

# ----------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------
MODEL = "openrouter/free"
EMBED_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "analytics.db"

HEADER_LOGO_CANDIDATES = ["Resources/HMA.jpg", "Resources/HMA__Tagline.jpg", "HMA.jpg"]
ICON_CANDIDATES = ["Resources/HMA_ICON.jpg", "HMA_ICON.jpg", "Resources/HMA.jpg"]
CONTEXT_CANDIDATES = ["Resources/summary.txt", "Resources/Summary.txt", "summary.txt", "Summary.txt"]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def img_to_data_uri(path):
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "png" if ext == "png" else "jpeg"
    with open(path, "rb") as f:
        return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"


LOGO_PATH = first_existing(HEADER_LOGO_CANDIDATES)
ICON_PATH = first_existing(ICON_CANDIDATES)

st.set_page_config(
    page_title="Dr. Awal O. Abdulrahman — AI Assistant",
    page_icon=ICON_PATH if ICON_PATH else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Brand styling
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
    :root {
        --navy:#16235A; --navy-deep:#0E1A45; --blue:#2D5BB8; --blue-soft:#EAF0FB;
        --orange:#F5A623; --orange-deep:#E8901A; --bg:#F4F6FB; --card:#FFFFFF;
        --text:#1B2440; --muted:#64708A; --border:#E3E8F2;
    }
    html, body, [class*="css"] { font-family:'Inter', sans-serif; color:var(--text); }
    .stApp { background:var(--bg); }
    .block-container { max-width:880px; padding-top:0.5rem; padding-bottom:8rem; }
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton { display:none; }
    [data-testid="stToolbar"] { background:transparent; }
    [data-testid="stToolbar"] button[kind="header"], [data-testid="stToolbar"] button[title="Deploy"] { display:none; }
    [data-testid="collapsedControl"] { display:flex !important; visibility:visible !important; opacity:1 !important; }
    #MainMenu, footer { visibility:hidden; }
    header { background:transparent; }
    h1, h2, h3 { font-family:'Poppins', sans-serif; color:var(--navy); }
    .header-card {
        background:var(--card); border:1px solid var(--border); border-top:4px solid var(--orange);
        border-radius:16px; padding:15px 24px; display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:14px; box-shadow:0 6px 24px rgba(16,35,90,0.06); margin-bottom:13px;
    }
    .brand-logo { height:72px; width:auto; display:block; }
    .brand-fallback { font-family:'Poppins'; font-weight:700; font-size:26px; color:var(--navy); }
    .brand-fallback .hm { color:var(--blue); }
    .header-pill {
        font-family:'Poppins'; font-weight:600; font-size:11px; letter-spacing:1.4px; text-transform:uppercase;
        color:var(--navy); background:var(--blue-soft); border:1px solid #D4E0F5;
        padding:9px 16px; border-radius:999px; white-space:nowrap;
    }
    .eyebrow {
        font-family:'Poppins', sans-serif; font-weight:600; font-size:11px; letter-spacing:2px;
        text-transform:uppercase; color:var(--orange-deep); margin:0 0 6px 0;
    }
    .page-title {
        font-family:'Poppins', sans-serif !important; font-size:24px !important; font-weight:800 !important;
        line-height:1.2 !important; color:var(--navy) !important; margin:0 0 7px 0 !important;
    }
    .page-sub { color:var(--muted); font-size:13px; line-height:1.5; margin:0 0 10px 0; }
    [data-testid="stChatMessage"] {
        background:var(--card); border:1px solid var(--border); border-radius:14px;
        padding:6px 14px; box-shadow:0 2px 10px rgba(16,35,90,0.04); margin-bottom:10px;
    }
    .stButton > button {
        background:var(--card); color:var(--navy); border:1px solid var(--border); border-radius:12px;
        padding:14px 16px; font-family:'Inter'; font-weight:500; font-size:14px; text-align:left;
        line-height:1.35; box-shadow:0 2px 10px rgba(16,35,90,0.04); transition:all .15s ease; height:100%;
    }
    .stButton > button:hover { border-color:var(--orange); box-shadow:0 6px 18px rgba(245,166,35,0.18); transform:translateY(-1px); }
    [data-testid="stSidebar"] { background:var(--card); border-right:1px solid var(--border); }
    [data-testid="stSidebar"] .sb-logo { text-align:center; padding:8px 0 2px 0; }
    [data-testid="stSidebar"] .sb-logo img { max-width:185px; height:auto; }
    [data-testid="stSidebar"] .sb-caption {
        text-align:center; color:var(--muted); font-size:12px; font-weight:500; letter-spacing:.3px; margin:8px 0 4px 0;
    }
    [data-testid="stSidebar"] .stButton > button {
        background:var(--navy); color:#FFFFFF; border:none; border-radius:10px; font-family:'Poppins';
        font-weight:600; font-size:14px; text-align:center; padding:10px 14px; box-shadow:none;
    }
    [data-testid="stSidebar"] .stButton > button:hover { background:var(--orange-deep); transform:none; box-shadow:none; }
    [data-testid="stChatInput"] textarea { font-family:'Inter'; }
    [data-testid="stMetric"] {
        background:var(--card); border:1px solid var(--border); border-radius:14px;
        padding:14px 16px; box-shadow:0 2px 10px rgba(16,35,90,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# OpenRouter client
# ----------------------------------------------------------------------
@st.cache_resource
def get_openai_client():
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("API_TOKEN"))


client = get_openai_client()


# ----------------------------------------------------------------------
# Analytics database (SQLite)
# ----------------------------------------------------------------------
@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, session_id TEXT, question TEXT,
            confidence REAL, search_mode TEXT
        )"""
    )
    conn.commit()
    return conn


def log_event(conn, session_id, question, confidence, mode):
    try:
        conn.execute(
            "INSERT INTO events (timestamp, session_id, question, confidence, search_mode) VALUES (?,?,?,?,?)",
            (datetime.utcnow().isoformat(), session_id, question, confidence, mode),
        )
        conn.commit()
    except Exception:
        pass  # never let logging break the chat


DB = get_db()


# ----------------------------------------------------------------------
# RAG (semantic with keyword fallback)
# ----------------------------------------------------------------------
def load_context_text():
    path = first_existing(CONTEXT_CANDIDATES)
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), path
        except Exception:
            pass
    return "", None


def build_chunks(text, target_words=150):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        combined = (current + "\n" + para).strip()
        if not current or len(combined.split()) <= target_words:
            current = combined
        else:
            chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


@st.cache_resource(show_spinner="Loading semantic search model…")
def get_embedder():
    if not HAS_SEMANTIC:
        return None
    try:
        return SentenceTransformer(EMBED_MODEL)
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def get_knowledge_base():
    text, source_file = load_context_text()
    chunks = build_chunks(text)
    if not chunks:
        return {"mode": "empty", "text": text, "chunks": [], "source_file": source_file}
    embedder = get_embedder()
    if embedder is not None:
        vectors = embedder.encode(chunks, normalize_embeddings=True)
        return {"mode": "semantic", "text": text, "chunks": chunks, "embedder": embedder, "vectors": vectors, "source_file": source_file}
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)
    return {"mode": "keyword", "text": text, "chunks": chunks, "vectorizer": vectorizer, "matrix": matrix, "source_file": source_file}


def retrieve_context(query, kb, k=3):
    chunks = kb["chunks"]
    if not chunks:
        return kb["text"], []
    if kb["mode"] == "semantic":
        q_vec = kb["embedder"].encode([query], normalize_embeddings=True)
        scores = cosine_similarity(q_vec, kb["vectors"])[0]
    else:
        q_vec = kb["vectorizer"].transform([query])
        scores = cosine_similarity(q_vec, kb["matrix"])[0]
    ranked = scores.argsort()[::-1]
    picked = [(chunks[i], float(scores[i])) for i in ranked[:k] if scores[i] > 0]
    if not picked:
        return kb["text"], []
    return "\n\n".join(c for c, _ in picked), picked


def build_system_prompt(context_text):
    context_text = context_text.strip() or "No profile information is currently available."
    return f"""You are an advanced AI assistant representing Dr. Awal Olalekan Abdulrahman.
Answer questions about his career, background, skills, and experience using ONLY the context below.

Context:
{context_text}

Guidelines:
- Speak professionally, elegantly, and confidently.
- If the answer is not in the context, say you don't have that detail rather than guessing.
- If asked something outside his professional profile, gently steer back to his medical, data science, or educational expertise.
- Never invent facts, dates, or certifications that are not present in the context.
"""


def render_sources(sources):
    if not sources:
        return
    with st.expander("📚  Sources used to answer this"):
        for i, (chunk, score) in enumerate(sources, 1):
            st.markdown(f"**Match {i}** · relevance {score:.0%}")
            st.caption(chunk[:400] + ("…" if len(chunk) > 400 else ""))


def render_confidence(score):
    """Small coloured badge showing how relevant the retrieved profile section is.
    Semantic similarity scores are naturally low, so thresholds are tuned for them."""
    if score is None:
        return
    if score >= 0.30:
        bg, fg, label = "#E6F4EC", "#1F7A47", "Strong match"
    elif score >= 0.18:
        bg, fg, label = "#FDF1DF", "#9A5B00", "Partial match"
    else:
        bg, fg, label = "#EAF0FB", "#2D5BB8", "General answer"
    st.markdown(
        f'<span style="display:inline-block;font-family:Poppins;font-weight:600;font-size:11px;'
        f'padding:4px 11px;border-radius:999px;background:{bg};color:{fg};margin-top:4px;">'
        f'● {label} · {score:.0%} relevance</span>',
        unsafe_allow_html=True,
    )


KB = get_knowledge_base()
MODE_LABELS = {
    "semantic": "🧠 Semantic (meaning-based)",
    "keyword": "🔤 Keyword (fallback)",
    "empty": "⚠️ No profile indexed",
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]


# ----------------------------------------------------------------------
# Sidebar (brand + navigation + controls)
# ----------------------------------------------------------------------
with st.sidebar:
    sidebar_logo = LOGO_PATH or ICON_PATH
    if sidebar_logo:
        st.markdown(f'<div class="sb-logo"><img src="{img_to_data_uri(sidebar_logo)}"/></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sb-logo"><span class="brand-fallback"><span class="hm">Hay</span>Medics Academy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-caption">Medical Doctor · Data Scientist · Medical Educator</div>', unsafe_allow_html=True)
    st.markdown("---")

    view = st.radio("View", ["💬  Chat", "📊  Analytics"], label_visibility="collapsed")

    st.markdown("---")
    with st.expander("💼  Core expertise", expanded=True):
        st.markdown(
            "- **Clinical care** — emergency medicine, inpatient management\n"
            "- **Data science** — predictive modelling, Python, SQL, Power BI\n"
            "- **Education** — Founder, HayMedics Academy"
        )
    with st.expander("📞  Contact & links"):
        st.markdown("**Email**  \ndrherwal@gmail.com")
        st.markdown("[LinkedIn](https://www.linkedin.com/in/awal-abdulrahman-a53483219)")
        st.markdown("[HayMedics on YouTube](https://www.youtube.com/@HayMedicsAcademy)")
        st.markdown("[GitHub](https://github.com/HayMedics)")
    with st.expander("⚙️  Assistant settings"):
        k = st.slider("Context depth", 1, 10, 7, help="How many of the most relevant profile sections the AI reads per question.")
        st.caption(f"Search mode: {MODE_LABELS.get(KB['mode'], KB['mode'])}")
        st.caption(f"🔎 Knowledge base: {len(KB['chunks'])} sections indexed")
        st.caption(f"📄 Reading: {KB.get('source_file') or '⚠️ NO FILE FOUND'}")

    st.markdown("---")
    if st.button("🧹  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        '<div style="text-align:center;color:var(--muted);font-size:11px;margin-top:16px;">'
        '© 2026 HayMedics Academy<br>Data | Research | Innovation</div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Shared brand header (logo card)
# ----------------------------------------------------------------------
if LOGO_PATH:
    logo_html = f'<img src="{img_to_data_uri(LOGO_PATH)}" class="brand-logo"/>'
else:
    logo_html = '<div class="brand-fallback"><span class="hm">Hay</span>Medics Academy</div>'

is_chat = view.strip().startswith("💬")
pill = "AI Assistant · Semantic RAG" if is_chat else "Usage Analytics"
st.markdown(
    f'<div class="header-card"><div>{logo_html}</div><div class="header-pill">{pill}</div></div>',
    unsafe_allow_html=True,
)


# ======================================================================
# ANALYTICS VIEW
# ======================================================================
def analytics_unlocked():
    """Optional password gate. If no ADMIN_PASSWORD secret is set, stays open."""
    try:
        pw = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        pw = None
    if not pw:
        return True
    if st.session_state.get("analytics_ok"):
        return True
    entered = st.text_input("Enter admin password to view analytics", type="password")
    if entered and entered == pw:
        st.session_state.analytics_ok = True
        return True
    if entered:
        st.error("Incorrect password.")
    return False


def render_analytics():
    st.markdown('<div class="eyebrow">Usage Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Who is using the assistant?</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Live usage data, captured automatically as people chat.</p>', unsafe_allow_html=True)

    if not analytics_unlocked():
        return

    df = pd.read_sql_query("SELECT * FROM events", DB)
    if df.empty:
        st.info("No usage data yet. Ask a few questions in the **Chat** view, then return here.")
        return

    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    c1, c2, c3 = st.columns(3)
    c1.metric("Questions asked", len(df))
    c2.metric("Unique visitors", df["session_id"].nunique())
    avg = df["confidence"].mean()
    c3.metric("Avg. relevance", f"{avg:.0%}" if pd.notna(avg) else "—")

    st.markdown("##### Questions per day")
    daily = df.dropna(subset=["timestamp"]).groupby(df["timestamp"].dt.date).size().rename("questions")
    if not daily.empty:
        st.bar_chart(daily, color="#2D5BB8")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### Most asked questions")
        top = df["question"].value_counts().head(8).rename_axis("question").reset_index(name="count")
        st.dataframe(top, use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("##### Recent activity")
        recent = (
            df.sort_values("timestamp", ascending=False)
            .head(10)[["timestamp", "question", "confidence"]]
            .copy()
        )
        recent["confidence"] = recent["confidence"].map(lambda v: f"{v:.0%}" if pd.notna(v) else "—")
        st.dataframe(recent, use_container_width=True, hide_index=True)


# ======================================================================
# CHAT VIEW
# ======================================================================
def render_chat():
    st.markdown('<div class="eyebrow">Semantic Retrieval-Augmented AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Chat with Dr. Awal&#39;s AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Answers are retrieved by meaning from Dr. Awal&#39;s verified profile — with sources and a relevance score.</p>', unsafe_allow_html=True)

    typed = st.chat_input("Ask about clinical work, data projects, research…")
    prompt = typed

    for message in st.session_state.messages:
        avatar = "🩺" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_confidence(message.get("confidence"))
                render_sources(message.get("sources"))

    if not st.session_state.messages and not typed:
        st.markdown(
            '<p style="margin:12px 0 8px 0;font-family:Poppins;font-weight:600;'
            'color:var(--navy);font-size:14px;">Try one of these to get started</p>',
            unsafe_allow_html=True,
        )
        starters = [
            "Who is Dr. Awal and what is his background?",
            "What data science projects has he built?",
            "Tell me about his clinical experience.",
            "How can I get in touch with him?",
        ]
        col_left, col_right = st.columns(2)
        grid = [col_left, col_right, col_left, col_right]
        for i, question in enumerate(starters):
            if grid[i].button(question, key=f"starter_{i}", use_container_width=True):
                prompt = question

    if prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        context, sources = retrieve_context(prompt, KB, k=k)
        confidence = sources[0][1] if sources else None
        log_event(DB, st.session_state.session_id, prompt, confidence, KB["mode"])

        system_prompt = build_system_prompt(context)
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant", avatar="🩺"):
            placeholder = st.empty()
            full_response = ""
            try:
                response = client.chat.completions.create(model=MODEL, messages=api_messages, stream=True)
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                placeholder.error(
                    "Couldn't reach the AI just now. If this keeps happening, the free model "
                    f"may be busy (429) or renamed (404) — change the MODEL line in app.py.\n\nDetails: `{e}`"
                )
                full_response = "I'm sorry, I'm having trouble processing that request right now."

            render_confidence(confidence)
            render_sources(sources)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response, "sources": sources, "confidence": confidence}
        )


# ----------------------------------------------------------------------
# Route to the selected view
# ----------------------------------------------------------------------
if is_chat:
    render_chat()
else:
    render_analytics()
