# API Explorer MVP

API Explorer generates an **AI-friendly Markdown integration guide** from an API documentation URL.

## Project Structure

- `frontend/` – Next.js + React + Tailwind UI (`/generate` page)
- `backend/` – FastAPI app exposing `POST /generate`
- `crawler/` – Recursive documentation crawler + API signal extraction
- `summarizer/` – LLM/rule-based markdown synthesis

## Run Locally

### 1) Backend

```bash
cd /workspace/api-explorer-agent
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Optional for AI summarization:

```bash
export OPENAI_API_KEY=your_key
```

### 2) Frontend

```bash
cd /workspace/api-explorer-agent/frontend
npm install
npm run dev
```

Open: `http://localhost:3000/generate`

Frontend can target a custom backend URL via:

```bash
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## API

### `POST /generate`

Request:

```json
{
  "docs_url": "https://developer.getjobber.com/docs"
}
```

Response:

```json
{
  "status": "complete",
  "markdown": "# API Integration Guide ...",
  "sources": ["https://..."]
}
```

## Notes

- Crawler stays on the same domain and limits to 50 pages.
- Extractor detects endpoints, authentication, pagination, webhooks, rate limits, and JSON examples.
- If no OpenAI API key is set, the backend still returns a deterministic markdown guide.
