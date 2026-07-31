# AI Document Summarizer

A full-stack application that summarizes long documents (PDF, DOCX, or TXT) using an LLM (via Groq), producing an executive summary, key bullet points, key takeaways, and action items — with support for structured output, live streaming, and Markdown download.

## Features

- Upload a PDF, DOCX, or TXT document and extract its text automatically
- Automatically chunks long documents and summarizes them using a map-reduce pattern (summarize each section, then synthesize into one cohesive result)
- Three output modes:
  - **Structured summary** — JSON with executive summary, bullet points, key takeaways, and action items
  - **Live streaming summary** — real-time, token-by-token summary generation
  - **Markdown download** — the structured summary formatted as a downloadable `.md` file
- Validates both user input (file type) and AI output (via Pydantic) to catch malformed or incomplete LLM responses
- Handles failures gracefully: invalid file types, rate limits, connection errors, invalid auth, malformed/incomplete AI responses, and backend connectivity loss
- Structured logging of both successful summaries and specific failure types
- Auto-generated interactive API docs via Swagger UI and ReDoc
- Streamlit UI supporting all three output modes

## Tech Stack

- FastAPI (backend)
- Streamlit (frontend)
- PyMuPDF (`fitz`) — PDF text extraction
- python-docx — DOCX text extraction
- Groq API (LLM provider)
- Pydantic (validation)
- Uvicorn (ASGI server)
- python-dotenv

## Setup

This project has **two parts that must run at the same time**: the FastAPI backend and the Streamlit frontend.

1. Clone the repository and navigate into it:
```bash
git clone <your-repo-url>
cd ai-document-summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=openai/gpt-oss-20b
```

5. Start the backend (Terminal 1):
```bash
uvicorn backend.main:app --reload
```
Runs on `http://127.0.0.1:8000`. Visit `/docs` to test the API directly via Swagger UI.

6. Start the frontend (Terminal 2 — keep the backend running):
```bash
streamlit run frontend/app.py
```
Runs on `http://localhost:8501` and opens automatically in your browser.

> **Note:** Both processes must be running simultaneously — the Streamlit app sends requests to the FastAPI backend over HTTP.

## API Usage

**POST** `/summarize` — structured JSON summary

Response:
```json
{
  "executive_summary": "...",
  "bullet_points": ["...", "..."],
  "key_takeaways": ["...", "..."],
  "action_items": ["...", "..."]
}
```

**POST** `/summarize/stream` — live streaming plain-text summary (chunked transfer encoding)

**POST** `/summarize/download` — returns a downloadable `summary.md` file

All three accept a `multipart/form-data` file upload (PDF, DOCX, or TXT).

## Project Structure
```bash
ai-document-summarizer/
├── backend/
│ ├── init.py
│ ├── main.py # FastAPI app instance, router registration
│ ├── api.py # /summarize, /summarize/stream, /summarize/download routes
│ ├── services.py # LLM integration, chunked summarization, streaming, error handling
│ ├── prompts.py # Chunk-level and final-summary prompt construction
│ ├── models.py # Pydantic response schema (DocumentSummary)
│ ├── config.py # Environment variable loading
│ ├── extractors.py # Multi-format text extraction (PDF, DOCX, TXT)
│ ├── chunking.py # Text chunking for long documents
│ └── logger.py # Logging setup
├── frontend/
│ └── app.py # Streamlit UI (structured / streaming / download modes)
├── .env
├── requirements.txt
├── README.md
└── .gitignore
```

## Known Limitations

- Chunking splits on paragraph boundaries; a single unusually large paragraph (no internal line breaks) cannot be split further and may exceed the target chunk size.
- Scanned/image-based PDFs with no extractable text will produce empty or low-quality summaries (no OCR support yet).
- If any chunk's summarization call fails, the entire request fails rather than continuing with partial results (a deliberate simplicity tradeoff — see extension ideas below).
- No authentication on the API — intended for local/development use.
- Bonus features from the original spec (adjustable summary length, translation, auto-generated titles, PDF download) are not yet implemented.