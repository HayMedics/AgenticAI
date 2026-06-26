import os
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic search model is optional — if it can't load, we fall back to keyword search.
try:
    from sentence_transformers import SentenceTransformer
    HAS_SEMANTIC = True
except Exception:
    HAS_SEMANTIC = False

# ----------------------------------------------------------------------
# Load secrets from the .env file (this is where your API_TOKEN lives)
# ----------------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------------
# SETTINGS YOU MIGHT CHANGE
# ----------------------------------------------------------------------
MODEL = "openrouter/free"                 # auto-picks a working FREE chat model
EMBED_MODEL = "all-MiniLM-L6-v2"          # free, lightweight semantic model (downloads once)

HEADER_LOGO_CANDIDATES = ["Resources/HMA.jpg", "Resources/HMA__Tagline.jpg", "HMA.jpg"]
ICON_CANDIDATES = ["Resources/HMA_ICON.jpg", "HMA_ICON.jpg", "Resources/HMA.jpg"]
CONTEXT_CANDIDATES = ["Resources/summary.txt", "Resources/resume.pdf"]


# ----------------------------------------------------------------------
# Small helpers
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
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{b64}"


LOGO_PATH = first_existing(HEADER_LOGO_CANDIDATES)
ICON_PATH = first_existing(ICON_CANDIDATES)


# ----------------------------------------------------------------------
# 1. Page configuration  (MUST be the first Streamlit command)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Dr. Awal O. Abdulrahman — AI Assistant",
    page_icon=ICON_PATH if ICON_PATH else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------
# 2. Brand styling (custom CSS) — HayMedics colours
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

    [data-testid="stToolbar"] { display:none; }
    [data-testid="stDecoration"] { display:none; }
    [data-testid="stStatusWidget"] { display:none; }
    .stDeployButton { display:none; }
    #MainMenu { visibility:hidden; }
    footer { visibility:hidden; }
    header { background:transparent; }

    h1, h2, h3 { font-family:'Poppins', sans-serif; color:var(--navy); }

    .header-card {
        background:var(--card); border:1px solid var(--border); border-top:4px solid var(--orange);
        border-radius:16px; padding:15px 24px;
        display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:14px; box-shadow:0 6px 24px rgba(16,35,90,0.06); margin-bottom:13px;
    }
    .brand-logo { height:72px; width:auto; display:block; }
    .brand-fallback { font-family:'Poppins'; font-weight:700; font-size:26px; color:var(--navy); }
    .brand-fallback .hm { color:var(--blue); }
    .header-pill {
        font-family:'Poppins'; font-weight:600; font-size:11px; letter-spacing:1.4px;
        text-transform:uppercase; color:var(--navy);
        background:var(--blue-soft); border:1px solid #D4E0F5;
        padding:9px 16px; border-radius:999px; white-space:nowrap;
    }

    .eyebrow {
        font-family:'Poppins', sans-serif; font-weight:600; font-size:11px; letter-spacing:2px;
        text-transform:uppercase; color:var(--orange-deep); margin:0 0 6px 0;
    }
    .page-title {
        font-family:'Poppins', sans-serif !important;
        font-size:24px !important; font-weight:800 !important; line-height:1.2 !important;
        color:var(--navy) !important; margin:0 0 7px 0 !important;
    }
    .page-sub { color:var(--muted); font-size:13px; line-height:1.5; margin:0; }

    [data-testid="stChatMessage"] {
        background:var(--card); border:1px solid var(--border); border-radius:14px;
        padding:6px 14px; box-shadow:0 2px 10px rgba(16,35,90,0.04); margin-bottom:10px;
    }

    .stButton > button {
        background:var(--card); color:var(--navy); border:1px solid var(--border);
        border-radius:12px; padding:14px 16px;
        font-family:'Inter'; font-weight:500; font-size:14px; text-align:left; line-height:1.35;
        box-shadow:0 2px 10px rgba(16,35,90,0.04); transition:all .15s ease; height:100%;
    }
    .stButton > button:hover {
        border-color:var(--orange); box-shadow:0 6px 18px rgba(245,166,35,0.18); transform:translateY(-1px);
    }

    [data-testid="stSidebar"] { background:var(--card); border-right:1px solid var(--border); }
    [data-testid="stSidebar"] .sb-logo { text-align:center; padding:8px 0 2px 0; }
    [data-testid="stSidebar"] .sb-logo img { max-width:185px; height:auto; }
    [data-testid="stSidebar"] .sb-caption {
        text-align:center; color:var(--muted); font-size:12px; font-weight:500;
        letter-spacing:.3px; margin:8px 0 4px 0;
    }
    [data-testid="stSidebar"] .stButton > button {
        background:var(--navy); color:#FFFFFF; border:none; border-radius:10px;
        font-family:'Poppins'; font-weight:600; font-size:14px; text-align:center;
        padding:10px 14px; box-shadow:none;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background:var(--orange-deep); transform:none; box-shadow:none;
    }

    [data-testid="stChatInput"] textarea { font-family:'Inter'; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# 3. Connect to the AI service (OpenRouter)
# ----------------------------------------------------------------------
@st.cache_resource
def get_openai_client():
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("API_TOKEN"))


client = get_openai_client()


# ======================================================================
# 4. RAG with SEMANTIC EMBEDDINGS
# ----------------------------------------------------------------------
# Keyword search (TF-IDF) matches exact words. Semantic search matches
# MEANING: it turns each chunk into a "meaning vector" (an embedding) so
# that "how do I contact him" can match a section about "email and phone",
# even though they share no words.
#
# If the semantic model can't load (e.g. resource limits), the app
# AUTOMATICALLY falls back to keyword search, so it never breaks.
# ======================================================================
def load_context_text():
    path = first_existing(CONTEXT_CANDIDATES)
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""


def build_chunks(text, target_words=60):
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
    """Load the meaning-vector model once. Returns None if unavailable."""
    if not HAS_SEMANTIC:
        return None
    try:
        return SentenceTransformer(EMBED_MODEL)
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def get_knowledge_base():
    """Index the profile once. Uses semantic search if possible, else keyword."""
    text = load_context_text()
    chunks = build_chunks(text)
    if not chunks:
        return {"mode": "empty", "text": text, "chunks": []}

    embedder = get_embedder()
    if embedder is not None:
        vectors = embedder.encode(chunks, normalize_embeddings=True)
        return {"mode": "semantic", "text": text, "chunks": chunks,
                "embedder": embedder, "vectors": vectors}

    # Fallback: keyword search
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)
    return {"mode": "keyword", "text": text, "chunks": chunks,
            "vectorizer": vectorizer, "matrix": matrix}


def retrieve_context(query, kb, k=3):
    """Find the k most relevant chunks. Returns (context_text, [(chunk, score), ...])."""
    chunks = kb["chunks"]
    if not chunks:
        return kb["text"], []

    if kb["mode"] == "semantic":
        q_vec = kb["embedder"].encode([query], normalize_embeddings=True)
        scores = cosine_similarity(q_vec, kb["vectors"])[0]
    else:  # keyword
        q_vec = kb["vectorizer"].transform([query])
        scores = cosine_similarity(q_vec, kb["matrix"])[0]

    ranked = scores.argsort()[::-1]
    picked = [(chunks[i], float(scores[i])) for i in ranked[:k] if scores[i] > 0]
    if not picked:
        return kb["text"], []  # very general question → use the whole profile
    return "\n\n".join(chunk for chunk, _ in picked), picked


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
            preview = chunk[:400] + ("…" if len(chunk) > 400 else "")
            st.caption(preview)


KB = get_knowledge_base()
MODE_LABELS = {
    "semantic": "🧠 Semantic (meaning-based)",
    "keyword": "🔤 Keyword (fallback)",
    "empty": "⚠️ No profile indexed",
}


# ----------------------------------------------------------------------
# 5. Sidebar (brand + quick reference + RAG controls)
# ----------------------------------------------------------------------
with st.sidebar:
    sidebar_logo = LOGO_PATH or ICON_PATH
    if sidebar_logo:
        st.markdown(
            f'<div class="sb-logo"><img src="{img_to_data_uri(sidebar_logo)}"/></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sb-logo"><span class="brand-fallback">'
            '<span class="hm">Hay</span>Medics Academy</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="sb-caption">Medical Doctor · Data Scientist · Medical Educator</div>',
        unsafe_allow_html=True,
    )
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
        k = st.slider(
            "Context depth",
            min_value=1, max_value=5, value=3,
            help="How many of the most relevant profile sections the AI reads for each question.",
        )
        st.caption(f"Search mode: {MODE_LABELS.get(KB['mode'], KB['mode'])}")
        st.caption(f"🔎 Knowledge base: {len(KB['chunks'])} sections indexed")

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
# 6. Main header (logo card + title)
# ----------------------------------------------------------------------
if LOGO_PATH:
    logo_html = f'<img src="{img_to_data_uri(LOGO_PATH)}" class="brand-logo"/>'
else:
    logo_html = '<div class="brand-fallback"><span class="hm">Hay</span>Medics Academy</div>'

st.markdown(
    f"""
    <div class="header-card">
        <div>{logo_html}</div>
        <div class="header-pill">AI Assistant · Semantic RAG</div>
    </div>
    <div class="eyebrow">Semantic Retrieval-Augmented AI</div>
    <div class="page-title">Chat with Dr. Awal&#39;s AI Assistant</div>
    <p class="page-sub">Answers are retrieved by meaning from Dr. Awal&#39;s verified profile — with sources shown.</p>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# 7. The conversation
# ----------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

typed = st.chat_input("Ask about clinical work, data projects, research…")
prompt = typed

for message in st.session_state.messages:
    avatar = "🩺" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant":
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

    # --- RAG step: retrieve the most relevant profile sections by MEANING ---
    context, sources = retrieve_context(prompt, KB, k=k)
    system_prompt = build_system_prompt(context)

    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant", avatar="🩺"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model=MODEL, messages=api_messages, stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            response_placeholder.error(
                "Couldn't reach the AI just now. If this keeps happening, the free "
                "model may be busy (429) or renamed (404) — change the MODEL line near "
                f"the top of app.py.\n\nDetails: `{e}`"
            )
            full_response = "I'm sorry, I'm having trouble processing that request right now."

        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "sources": sources}
    )
