# 🩺 Dr. Awal's AI Assistant
### Semantic RAG · Usage Analytics · HayMedics Academy

> An AI-powered personal assistant that answers questions about Dr. Awal Olalekan Abdulrahman's career, clinical experience, data science projects, and HayMedics Academy.
> Built with Streamlit, powered by OpenRouter's free LLM tier, and upgraded with semantic retrieval-augmented generation (RAG), live usage analytics, and a relevance scoring system.

---

## 🌐 Live Demo

🔗 **[dr-awwal-ai-assistant.streamlit.app](https://dr-awwal-ai-assistant.streamlit.app)**

---

## 📸 What It Looks Like

| Feature | Description |
|---|---|
| **Chat view** | Branded interface · suggested question chips · streaming replies |
| **Relevance badge** | 🟢 Strong match · 🟡 Partial match · 🔵 General answer |
| **Sources panel** | Expandable "Sources used" showing which profile sections were retrieved |
| **Analytics view** | Questions asked · unique visitors · avg relevance · daily chart · top questions |

---

## ✨ Features

### AI & Retrieval
- **Semantic RAG** — the profile is split into chunks and indexed using `sentence-transformers` (`all-MiniLM-L6-v2`). Each question is matched to the most relevant chunks by *meaning*, not just keywords — so "how do I contact him?" correctly retrieves the email/phone section even though the words don't overlap
- **Automatic fallback** — if the semantic model can't load (e.g. resource limits), the app silently falls back to TF-IDF keyword search. The sidebar shows which mode is active: `🧠 Semantic` or `🔤 Keyword`
- **Grounded persona** — the AI answers exclusively from Dr. Awal's verified profile (`summary.txt`). It will not invent facts, dates, or certifications
- **Streaming replies** — responses type out in real time for a natural feel
- **Adjustable context depth** — a sidebar slider controls how many profile sections the AI reads per question (1–5)

### Explainability
- **Relevance badge** — every answer carries a calibrated badge showing how well the retrieved section matched the question. Labels are tuned for real semantic similarity scores:
  - `🟢 Strong match` — ≥ 30% relevance
  - `🟡 Partial match` — 18–29% relevance
  - `🔵 General answer` — below 18% (neutral, not alarming)
- **Sources panel** — an expandable drawer shows exactly which parts of the profile were used to construct each answer, with relevance percentages

### Analytics Dashboard
- **Usage tracking** — every question is silently logged to a local SQLite database (WAL mode, thread-safe)
- **Dashboard metrics** — total questions asked · unique visitors · average relevance score
- **Daily activity chart** — bar chart of questions per day
- **Top questions table** — most frequently asked questions, ranked
- **Recent activity feed** — last 10 questions with timestamps and relevance scores
- **Optional admin password** — set `ADMIN_PASSWORD` in Streamlit secrets to gate the dashboard; leave it unset to keep it open

### Interface & Branding
- **HayMedics brand** — navy `#16235A`, royal blue `#2D5BB8`, orange `#F5A623`; Poppins + Inter typography; orange-top-striped header card matching the HayMedics portfolio style
- **Suggested question chips** — four starter questions on first load, disappear once the conversation begins
- **Two-view navigation** — `💬 Chat` and `📊 Analytics` radio buttons in the sidebar
- **Logo with fallback** — loads `HMA.jpg` from the Resources folder; falls back to a styled text logo if the file is missing, so the app never crashes
- **Persistent sidebar arrow** — the expand/collapse arrow is always visible, regardless of browser state

---

## 🗂 Project Structure

```
AgenticAI/
│
├── app.py                  # Main Streamlit application (all logic in one file)
├── requirements.txt        # Python dependencies for local and cloud
├── .gitignore              # Keeps .env, .venv, and analytics.db off GitHub
├── README.md               # This file
│
└── Resources/
    ├── summary.txt         # Dr. Awal's knowledge file — what the AI reads
    ├── HMA.jpg             # HayMedics Academy horizontal logo (header card)
    └── HMA_ICON.jpg        # HayMedics Academy icon (browser tab favicon)
```

> ⚠️ `.env` is **never** uploaded to GitHub. It contains your private API key.
> ⚠️ `analytics.db` is **never** uploaded to GitHub. It's a local runtime file.

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web app framework and UI |
| [OpenRouter](https://openrouter.ai) | Free LLM API gateway (`openrouter/free`) |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | API client (OpenRouter is OpenAI-compatible) |
| [sentence-transformers](https://sbert.net) | Semantic embedding model (`all-MiniLM-L6-v2`) |
| [scikit-learn](https://scikit-learn.org) | TF-IDF fallback search + cosine similarity |
| [pandas](https://pandas.pydata.org) | Analytics dashboard data processing |
| [SQLite](https://www.sqlite.org) | Lightweight usage analytics database |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Load `.env` secrets locally |
| Python 3.11+ | Language |

---

## 🚀 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/HayMedics/AgenticAI.git
cd AgenticAI
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### 3. Install all dependencies
```bash
pip install -r requirements.txt
```
> Note: `sentence-transformers` is a large library (~500 MB with dependencies). Installation may take several minutes on a slow connection.

### 4. Create your `.env` file
```
API_TOKEN=sk-or-v1-your-key-here
```
Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys) — no credit card required.

### 5. Add your knowledge file
Put Dr. Awal's profile content in `Resources/summary.txt`. This is the only document the AI reads to answer questions.

### 6. Run the app
```bash
streamlit run app.py
```
Open `http://localhost:8501`. The semantic model downloads automatically on first run (~90 MB), then is cached.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repository to a **public** GitHub repo (Streamlit's free plan requires public repos).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** and fill in:
   - **Repository:** `HayMedics/AgenticAI`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy** and wait ~3–5 minutes (longer on first deploy due to library installation).
5. Go to **⋮ → Settings → Secrets** and add:
```toml
API_TOKEN = "sk-or-v1-your-key-here"
```
6. Optionally add an admin password for the analytics dashboard:
```toml
ADMIN_PASSWORD = "your-chosen-password"
```

---

## ⚙️ Configuration Reference

All key settings are at the top of `app.py`:

```python
MODEL = "openrouter/free"        # LLM: auto-picks any working free model
EMBED_MODEL = "all-MiniLM-L6-v2" # Semantic embedding model (free, local)
DB_PATH = "analytics.db"          # Analytics database location
```

**To pin a specific LLM:** replace `"openrouter/free"` with any `:free` model ID from [openrouter.ai/models](https://openrouter.ai/models).

---

## 🧠 How It Works

```
User asks a question
        ↓
Profile (summary.txt) is split into ~60-word chunks
        ↓
Each chunk is encoded into a meaning vector (embedding)
        ↓
The question is also encoded into a meaning vector
        ↓
Cosine similarity finds the most relevant chunks
        ↓
Top chunks + question → sent to LLM via OpenRouter
        ↓
LLM generates an answer grounded in those chunks only
        ↓
Answer streams back · relevance badge shown · sources displayed
        ↓
Question + relevance score silently logged to SQLite
```

**Why semantic search beats keyword search:**
Keyword search matches exact words. Semantic search matches meaning. "How do I reach him?" and "email / phone number" share no words — but their meanings are related, so semantic embeddings correctly retrieve the contact section. Keyword search scores 0.00 on this; semantic search retrieves it reliably.

---

## 📊 Analytics Notes

The analytics database (`analytics.db`) is stored locally and **resets when Streamlit's free tier restarts the app** (ephemeral filesystem). This is fine for demos and interviews — ask a few questions to populate it, then open the Analytics view.

For persistent analytics that survive restarts, the next upgrade is a cloud database (e.g. [Supabase](https://supabase.com) free tier), which is a drop-in replacement for the SQLite connection in `app.py`.

---

## 📁 Updating the Knowledge File

To add new information (projects, certifications, research):

1. Open `Resources/summary.txt` in any text editor.
2. Add your new content — separate sections with a blank line between them so the chunking works correctly.
3. Save the file.
4. **Locally:** restart the app (`Ctrl + C` → `streamlit run app.py`) — the index rebuilds automatically.
5. **On Streamlit Cloud:** upload the updated file to GitHub — the app redeploys automatically.

---

## 👨‍⚕️ About Dr. Awal Olalekan Abdulrahman

Medical Doctor · Data Scientist · Medical Educator · Founder, HayMedics Academy

- 🌐 Portfolio: [haymedics.github.io](https://haymedics.github.io)
- 💼 LinkedIn: [Awal Abdulrahman, MD](https://www.linkedin.com/in/awal-abdulrahman-a53483219)
- 📺 YouTube: [HayMedics Academy](https://www.youtube.com/@HayMedicsAcademy)
- 🐙 GitHub: [github.com/HayMedics](https://github.com/HayMedics)
- 📧 Email: haymedicsacademy@gmail.com

---

## 📄 Licence

This project is for portfolio and educational demonstration purposes.
© 2026 Awal Abdulrahman · HayMedics Academy — Data | Research | Innovation
