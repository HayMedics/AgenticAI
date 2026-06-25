import os
import base64
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ----------------------------------------------------------------------
# Load secrets from the .env file (this is where your API_TOKEN lives)
# ----------------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------------
# SETTINGS YOU MIGHT CHANGE
# ----------------------------------------------------------------------
# The AI model. "openrouter/free" automatically picks a working FREE model,
# which helps you avoid both "model not found" (404) and "too busy" (429)
# errors. If you'd rather pin a specific model, replace the line below with
# any ":free" model ID from https://openrouter.ai/models (set Price = Free),
# for example: "meta-llama/llama-3.2-3b-instruct:free"
MODEL = "openrouter/free"

# The app looks for your brand files in these places (first match wins).
# Drop your logo into a folder called "Resources" next to this file.
HEADER_LOGO_CANDIDATES = [
    "Resources/HMA.jpg",
    "Resources/HMA__Tagline.jpg",
    "HMA.jpg",
]
ICON_CANDIDATES = [
    "Resources/HMA_ICON.jpg",
    "HMA_ICON.jpg",
    "Resources/HMA.jpg",
]
CONTEXT_CANDIDATES = ["Resources/summary.txt", "Resources/resume.pdf"]


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def first_existing(paths):
    """Return the first file path that actually exists, otherwise None."""
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def img_to_data_uri(path):
    """Turn an image file into text we can embed directly inside HTML."""
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "png" if ext == "png" else "jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{b64}"


LOGO_PATH = first_existing(HEADER_LOGO_CANDIDATES)
ICON_PATH = first_existing(ICON_CANDIDATES)


# ----------------------------------------------------------------------
# 1. Page configuration  (this MUST be the first Streamlit command)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Dr. Awal O. Abdulrahman — AI Assistant",
    page_icon=ICON_PATH if ICON_PATH else "🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------
# 2. Brand styling (custom CSS) — this is what makes it look professional.
#    Colours are taken straight from your HayMedics brand.
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
        --navy:#16235A;
        --navy-deep:#0E1A45;
        --blue:#2D5BB8;
        --blue-soft:#EAF0FB;
        --orange:#F5A623;
        --orange-deep:#E8901A;
        --bg:#F4F6FB;
        --card:#FFFFFF;
        --text:#1B2440;
        --muted:#64708A;
        --border:#E3E8F2;
    }

    /* Base look */
    html, body, [class*="css"] { font-family:'Inter', sans-serif; color:var(--text); }
    .stApp { background:var(--bg); }
    .block-container { max-width:880px; padding-top:0.5rem; padding-bottom:8rem; }

    /* Hide Streamlit's default chrome (Deploy button, menu, footer, status) */
    [data-testid="stToolbar"] { display:none; }
    [data-testid="stDecoration"] { display:none; }
    [data-testid="stStatusWidget"] { display:none; }
    .stDeployButton { display:none; }
    #MainMenu { visibility:hidden; }
    footer { visibility:hidden; }
    header { background:transparent; }

    h1, h2, h3 { font-family:'Poppins', sans-serif; color:var(--navy); }

    /* ---- Header card holding the logo ---- */
    .header-card {
        background:var(--card);
        border:1px solid var(--border);
        border-top:4px solid var(--orange);
        border-radius:16px;
        padding:15px 24px;
        display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:14px;
        box-shadow:0 6px 24px rgba(16,35,90,0.06);
        margin-bottom:13px;
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

    /* ---- Title block (self-contained so Streamlit can't resize it) ---- */
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

    /* ---- Chat bubbles ---- */
    [data-testid="stChatMessage"] {
        background:var(--card);
        border:1px solid var(--border);
        border-radius:14px;
        padding:6px 14px;
        box-shadow:0 2px 10px rgba(16,35,90,0.04);
        margin-bottom:10px;
    }

    /* ---- Buttons in the MAIN area = suggested-question chips ---- */
    .stButton > button {
        background:var(--card);
        color:var(--navy);
        border:1px solid var(--border);
        border-radius:12px;
        padding:14px 16px;
        font-family:'Inter'; font-weight:500; font-size:14px;
        text-align:left; line-height:1.35;
        box-shadow:0 2px 10px rgba(16,35,90,0.04);
        transition:all .15s ease;
        height:100%;
    }
    .stButton > button:hover {
        border-color:var(--orange);
        box-shadow:0 6px 18px rgba(245,166,35,0.18);
        transform:translateY(-1px);
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] { background:var(--card); border-right:1px solid var(--border); }
    [data-testid="stSidebar"] .sb-logo { text-align:center; padding:8px 0 2px 0; }
    [data-testid="stSidebar"] .sb-logo img { max-width:185px; height:auto; }
    [data-testid="stSidebar"] .sb-caption {
        text-align:center; color:var(--muted); font-size:12px; font-weight:500;
        letter-spacing:.3px; margin:8px 0 4px 0;
    }
    /* Sidebar buttons override the chip style = solid navy action button */
    [data-testid="stSidebar"] .stButton > button {
        background:var(--navy); color:#FFFFFF; border:none; border-radius:10px;
        font-family:'Poppins'; font-weight:600; font-size:14px; text-align:center;
        padding:10px 14px; box-shadow:none;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background:var(--orange-deep); transform:none; box-shadow:none;
    }

    /* Chat input box */
    [data-testid="stChatInput"] textarea { font-family:'Inter'; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# 3. Connect to the AI service (OpenRouter)  —  your working settings
# ----------------------------------------------------------------------
@st.cache_resource
def get_openai_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("API_TOKEN"),
    )


client = get_openai_client()


# ----------------------------------------------------------------------
# 4. Load Dr. Awal's profile (resume / summary) to ground the answers
# ----------------------------------------------------------------------
@st.cache_data
def load_context_data():
    path = first_existing(CONTEXT_CANDIDATES)
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return "Resume context unavailable."


resume_context = load_context_data()


# ----------------------------------------------------------------------
# 5. The persona instructions sent to the AI
# ----------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are an advanced AI assistant representing Dr. Awal Olalekan Abdulrahman.
Your purpose is to answer questions about his career, background, skills, and professional experience accurately based ONLY on the provided context.

Context:
{resume_context}

Guidelines:
- Speak professionally, elegantly, and confidently.
- If asked questions outside his professional profile, gently steer the conversation back to his medical, data science, or educational expertise.
- Do not make up facts or certifications not explicitly listed in the context.
"""


# ----------------------------------------------------------------------
# 6. Sidebar (brand + quick reference)
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
# 7. Main header (logo card + title)
# ----------------------------------------------------------------------
if LOGO_PATH:
    logo_html = f'<img src="{img_to_data_uri(LOGO_PATH)}" class="brand-logo"/>'
else:
    logo_html = '<div class="brand-fallback"><span class="hm">Hay</span>Medics Academy</div>'

st.markdown(
    f"""
    <div class="header-card">
        <div>{logo_html}</div>
        <div class="header-pill">AI Assistant</div>
    </div>
    <div class="eyebrow">Conversational AI</div>
    <div class="page-title">Chat with Dr. Awal&#39;s AI Assistant</div>
    <p class="page-sub">Answers are drawn from Dr. Awal&#39;s verified professional profile.</p>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# 8. The conversation
# ----------------------------------------------------------------------
# Make sure we have somewhere to store the chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# The text box (Streamlit always pins this to the bottom of the page)
typed = st.chat_input("Ask about clinical work, data projects, research…")

# The prompt can come from the text box OR from a suggested-question chip
prompt = typed

# Show the conversation so far
for message in st.session_state.messages:
    avatar = "🩺" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Show suggested questions only at the very start (empty, nothing typed yet)
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
        "What is HayMedics Academy?",
    ]
    col_left, col_right = st.columns(2)
    grid = [col_left, col_right, col_left, col_right]
    for i, question in enumerate(starters):
        if grid[i].button(question, key=f"starter_{i}", use_container_width=True):
            prompt = question

# If we have a new prompt, answer it
if prompt:
    # Show the user's message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build the full message list for the AI (system prompt + history)
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # Stream the assistant's reply so it "types" out
    with st.chat_message("assistant", avatar="🩺"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            # An error message that tells you what to do, not just "sorry"
            response_placeholder.error(
                "Couldn't reach the AI just now. If this keeps happening, the free "
                "model may be busy (429) or renamed (404) — change the MODEL line near "
                f"the top of app.py.\n\nDetails: `{e}`"
            )
            full_response = "I'm sorry, I'm having trouble processing that request right now."

    # Save the assistant's reply to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
