# 🤖 AI PMArchitect: PRD to Jira Ticket Generator

A Streamlit web app that converts Product Requirement Documents (PRDs) into structured Jira-ready backlogs using a multi-agent AI pipeline powered by Google Gemini.


---

## How It Works

The app simulates a three-agent TPM crew in a single optimized API call:

1. **PM Analyst** — Extracts user stories from the PRD using the "As a... I want to... So that..." format
2. **Technical Lead** — Breaks stories into frontend, backend, and database tasks with technical notes
3. **TPM Critic** — Reviews and formats everything into clean Markdown tables ready for Jira

---

## Stack

- [Streamlit](https://streamlit.io/) — web UI
- [Google Gemini](https://aistudio.google.com/) — AI model (`gemini-2.0-flash`)
- [google-generativeai](https://pypi.org/project/google-generativeai/) — Python SDK
- Python 3.11

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Install dependencies

```bash
pip install streamlit google-generativeai
```

### 3. Set up your API key

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

Get a free API key at **https://aistudio.google.com/apikey**

Then export it:

```bash
export GOOGLE_API_KEY=your_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

1. Click **Load Demo PRD** to try a pre-filled example, or paste your own PRD
2. Click **Generate Jira Backlog**
3. Copy the generated Markdown tables into Jira

---

## Free Tier Notes

This app is designed to work within Google AI Studio's free tier:

- **Model:** `gemini-2.0-flash` (15 RPM, 1,500 RPD free)
- Uses a single API call per run to stay within rate limits
- If you hit a quota error, wait ~1 minute and try again

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google AI Studio API key (required) |

---

## License

Will update soon by keerthi!
