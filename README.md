# 🩺 Dr. Awal's AI Assistant
### Conversational AI · HayMedics Academy

> An AI-powered personal assistant that answers questions about Dr. Awal Olalekan Abdulrahman's career, clinical experience, data science projects, and HayMedics Academy — built with Streamlit and powered by OpenRouter's free LLM tier.

---

## 🌐 Live Demo

🔗 **[Try it live →](https://your-app-name.streamlit.app)**
*(Replace this link with your Streamlit Community Cloud URL after deployment)*

---

## 📸 Preview

| Landing screen | Chat in action |
|---|---|
| Logo card · suggested questions · branded sidebar | Streaming replies · conversation history · clear chat |

---

## ✨ Features

- **Branded interface** — HayMedics navy, blue, and orange colour system; Poppins + Inter typography; custom header card matching the HayMedics portfolio style
- **Persona AI** — answers exclusively from Dr. Awal's verified professional profile (no hallucination of uncited facts)
- **Streaming replies** — responses type out in real time for a natural feel
- **Suggested question chips** — four clickable starters help visitors know what to ask
- **Conversation memory** — full chat history maintained within the session
- **Free to run** — uses `openrouter/free`, which auto-selects a working free model so the app never hits a paid-model wall
- **Graceful error messages** — if the free model is busy (429) or renamed (404), the app tells you exactly what to change instead of just saying "sorry"
- **Logo fallback** — if brand images are missing, the app renders a clean text logo so it never crashes

---

## 🗂 Project Structure

```
AgenticAI/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .gitignore              # Keeps .env and .venv off GitHub
├── README.md               # This file
│
└── Resources/
    ├── summary.txt         # Dr. Awal's knowledge file (AI context)
    ├── HMA.jpg             # HayMedics Academy horizontal logo
    └── HMA_ICON.jpg        # HayMedics Academy icon (browser tab)
```

> ⚠️ The `.env` file is **not** included — it contains your private API key and must never be uploaded to GitHub.

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web app framework |
| [OpenRouter](https://openrouter.ai) | Free LLM API gateway |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | API client (OpenRouter is OpenAI-compatible) |
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

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file
Create a file called `.env` in the project root and add your OpenRouter API key:
```
API_TOKEN=sk-or-v1-your-key-here
```
Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys) — no credit card required.

### 5. Add your knowledge file
Put Dr. Awal's profile text in `Resources/summary.txt`. This is what the AI reads to answer questions.

### 6. Run the app
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (excluding `.env` and `.venv`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** and fill in:
   - **Repository:** `HayMedics/AgenticAI`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy**.
5. After deployment, go to **⋮ → Settings → Secrets** and add:
```toml
API_TOKEN = "sk-or-v1-your-key-here"
```
6. Save — the app restarts with your key loaded. Done.

---

## 🔑 Switching the AI Model

The model is set in one place near the top of `app.py`:

```python
MODEL = "openrouter/free"
```

- `"openrouter/free"` — auto-picks any working free model (recommended, most stable).
- Any `:free` model ID from [openrouter.ai/models](https://openrouter.ai/models) — pin a specific model if you prefer.

---

## 🧠 How It Works

```
User types a question
        ↓
Streamlit sends it to OpenRouter API
        ↓
OpenRouter routes it to a free LLM
        ↓
LLM reads the system prompt (Dr. Awal's profile + guidelines)
        ↓
Answer streams back word by word
        ↓
Streamlit renders it in the chat window
```

The AI only answers from the content in `Resources/summary.txt`. It will not invent qualifications or experiences not listed there.

---

## 📁 Updating the Knowledge File

To add new information (new projects, certifications, experiences):

1. Open `Resources/summary.txt` in any text editor.
2. Add your new content at the bottom.
3. Save the file.
4. Restart the app locally (`Ctrl + C` → `streamlit run app.py`).
5. On Streamlit Cloud — push the updated file to GitHub; the cloud app redeploys automatically.

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
