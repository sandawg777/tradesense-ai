# TradeSense AI

Enterprise-grade AI trading research assistant with multi-agent architecture, RAG, governance, evals, and live market data.

## Features

- **Multi-agent architecture** — ReAct agent with 7 specialized tools
- **Live market data** — yfinance for real-time prices, technicals, fundamentals
- **Real-time sector performance** — tracks 20 sector ETFs to identify hot themes
- **Dynamic stock screening** — Yahoo Finance screener for live opportunities
- **News integration** — Yahoo Finance news API for current market sentiment
- **RAG knowledge base** — FAISS vector store over trading strategies
- **AI Governance** — PII detection, prompt injection guards, audit logging
- **MLOps** — eval suite, automated tests, LangSmith tracing
- **Conversational memory** — multi-turn analysis with context retention

## Stack

- FastAPI + Pydantic
- LangChain + LangSmith
- Groq (llama-3.3-70b-versatile)
- FAISS + HuggingFace embeddings
- yfinance + Yahoo Finance APIs
- Docker + Railway (deployment)

## Project Structure

```
TradeSenseAI/
├── api/
│   ├── main.py          FastAPI app
│   ├── agent.py         LangChain agent + memory
│   ├── tools.py         7 production tools
│   ├── governance.py    PII, injection, audit
│   └── evals.py         Eval suite (MLOps)
├── data/
│   └── knowledge.txt    Trading knowledge base (RAG)
├── frontend/
│   ├── index.html
│   ├── styles/main.css
│   └── js/app.js
├── tests/
│   └── test_evals.py    Pytest suite
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

1. Get free API keys:
   - Groq: https://console.groq.com
   - LangSmith: https://smith.langchain.com

2. Copy environment template and add keys:
   ```bash
   cp .env.example .env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run Locally

**Terminal 1 — Backend:**
```bash
python -m uvicorn api.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000`.

## Run Tests

```bash
pytest tests/ -v
```

## Run Evals (MLOps)

```bash
python -m api.evals
```

## Deploy to Railway (Public URL)

1. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create tradesense-ai --public --source=. --push
   ```

2. Go to https://railway.app, sign in with GitHub, click **New Project** → **Deploy from GitHub repo**

3. Select your repo. Railway detects the Dockerfile automatically.

4. Add environment variables in Railway dashboard:
   - `GROQ_API_KEY`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_PROJECT`
   - `LANGSMITH_TRACING_V2=true`

5. Railway gives you a public URL like `tradesense-ai.up.railway.app`

6. Update `frontend/js/app.js`:
   ```javascript
   const API_URL = 'https://your-app.up.railway.app/analyze';
   ```

7. Deploy frontend on Vercel (drag-and-drop the `frontend/` folder) or Netlify.

## Endpoints

- `GET /` — service info
- `GET /health` — health check
- `POST /analyze` — run agent analysis
- `GET /audit-log` — governance audit trail
- `GET /sessions` — active sessions
- `GET /docs` — interactive Swagger UI

## Example Queries

- "What sectors are hot right now?"
- "Analyze NVDA for a swing trade opportunity"
- "Find small cap gainers in technology"
- "What signals indicate a stock about to make a big move?"

## Architecture

This project demonstrates enterprise AI engineering across the full stack:

**Design**: Multi-agent system with tool routing, memory, and structured outputs

**Build**: Production API with FastAPI, Docker container, modular Python package

**Operate**: LangSmith tracing, automated evals, pytest suite, governance audit log

**Govern**: PII detection, prompt injection guards, off-topic filters, structured logging
