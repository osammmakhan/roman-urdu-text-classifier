# Roman Urdu Text Classifier — Decisions Log

## Project Overview
A full-stack application for classifying Roman Urdu text (Urdu written in Latin script) into sentiment categories (positive/negative/neutral) using Groq API with guardrails.

---

## Technical Decisions Made

### 1. Stack Selection
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend Framework | FastAPI | Modern, async, automatic OpenAPI docs, type-safe |
| Database | SQLite | Zero-config, file-based, sufficient for personal project |
| LLM Provider | Groq API | Fast inference, free tier available, OpenAI-compatible API |
| Frontend Framework | React + Vite | Fast dev server, modern build tool (CRA deprecated) |
| Styling | Tailwind CSS v3 | Utility-first, rapid UI development, v4 had PostCSS issues |
| Rate Limiting | slowapi | Simple in-memory, integrates with FastAPI |

### 2. Architecture Decisions

#### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app, middleware, lifespan
│   ├── config.py            # Pydantic Settings (env-based config)
│   ├── database.py          # SQLAlchemy engine, session, models
│   ├── schemas.py           # Pydantic request/response models
│   ├── routes/
│   │   └── classification.py # REST endpoints
│   ├── services/
│   │   └── classification.py # Groq integration, prompt engineering
│   └── rate_limiter.py      # Limiter instance (avoids circular imports)
├── requirements.txt
├── .env / .env.example
└── .gitignore
```

#### Database Schema
```sql
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    label VARCHAR(20) NOT NULL,      -- positive, negative, neutral, unclassifiable
    confidence REAL NOT NULL,        -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/classify | Classify text, store result, return label + confidence |
| GET | /api/results | List stored results with optional label filter |

### 3. Classification Guardrails (Critical)

Implemented in `app/services/classification.py`:

1. **Fixed Label Set**: Only `positive`, `negative`, `neutral`, `unclassifiable` allowed
2. **Confidence Score**: Model must return 0.0-1.0, clamped in code
3. **Empty/Short Text Handling**: Returns `unclassifiable` before calling API
4. **Malformed Response Handling**: Defaults to `neutral`/0.5 if JSON parsing fails
5. **Raw Output Logging**: Full model response logged for debugging
6. **Prompt Engineering**: Explicit instructions to return only valid JSON with label + confidence

### 4. Security & Production Hardening

| Feature | Implementation |
|---------|----------------|
| Rate Limiting | 10 requests/minute per IP on `/classify` via slowapi |
| Request Logging | Structured middleware with request IDs, timing headers (X-Process-Time, X-Request-ID) |
| API Key Validation | Startup warning if `GROQ_API_KEY` not configured |
| CORS | Configured for localhost:3000 and localhost:5173 |
| Input Validation | Pydantic: min_length=1, max_length=5000 on classify request |
| SQL Injection Prevention | SQLAlchemy ORM (parameterized queries) |
| XSS Prevention | React auto-escapes, CSP headers in Vite config |
| Environment Config | `.env.example` files for both frontend/backend |
| .gitignore | Excludes `__pycache__`, `.env`, `*.db`, `venv/`, `node_modules/` |

### 5. Frontend Decisions

| Decision | Details |
|----------|---------|
| Build Tool | Vite (not CRA - deprecated) |
| CSS Framework | Tailwind CSS v3 (v4 PostCSS plugin incompatible) |
| State Management | React useState + useEffect (simple, no Redux needed) |
| API Config | `VITE_API_BASE` env variable (defaults to http://localhost:8000/api) |
| UI Components | Textarea input, classification result card, filterable results table |
| Filter Options | All, Positive, Negative, Neutral, Unclassifiable |

### 6. Groq Model Selection Journey

| Model Tried | Status |
|-------------|--------|
| llama-3.1-8b-instant | Decommissioned |
| llama3-8b-8192 | Decommissioned |
| llama-3.3-70b-versatile | **Current (working)** |
| gemma2-9b-it | Available but smaller |
| llama3-70b-8192 | Decommissioned |

**Current**: `llama-3.3-70b-versatile` (configured in `config.py`)

### 7. Key Bug Fixes During Development

1. **pydantic-core build failure** (Python 3.14 + Rust): Fixed with `pip install --only-binary :all:`
2. **Tailwind v4 PostCSS issue**: Downgraded to v3 for Vite compatibility
3. **Circular import** (main.py ↔ routes): Created separate `rate_limiter.py` module
4. **Indentation errors** in config.py: Fixed multiple times during model iteration
5. **Groq model deprecation**: Updated model name 3+ times as models were decommissioned

---

## Current State (as of 2026-09-05)

### ✅ Completed (All 20 Todos Done)

**Backend:**
- [x] FastAPI + SQLite setup
- [x] Database schema creation
- [x] POST /classify endpoint with Groq integration
- [x] GET /results endpoint with label filtering
- [x] Rate limiting (10 req/min)
- [x] Request logging middleware
- [x] API key validation on startup
- [x] Backend .gitignore
- [x] Switch from OpenAI to Groq API

**Frontend:**
- [x] React + Vite + Tailwind setup
- [x] Text input component
- [x] Results table with filtering
- [x] Frontend-backend integration
- [x] Frontend .env for API base URL
- [x] CSP headers via Vite config

**Testing & Validation:**
- [x] End-to-end flow tested
- [x] Guardrails verified (empty text, short text, API errors)
- [x] Filter dropdown works
- [x] Security audit (no critical issues)

### 🔄 Running Locally
- Backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
- Backend runs on http://localhost:8000
- Frontend runs on http://localhost:5173

### ⚠️ Known Issues / Next Steps

1. **Groq Model**: Need to verify `llama-3.3-70b-versatile` works on console.groq.com
2. **Unit Tests**: No automated tests yet (manual testing only)
3. **CSV Batch Upload**: Stretch goal from Planning.md
4. **Hosting**: Decision pending (Railway, Render, Fly.io, etc.)
5. **Authentication**: Not needed for single-user but would be required for multi-user

---

## Files Modified/Created in This Session

### Backend
- `backend/requirements.txt` - Added groq, slowapi
- `backend/.env.example` / `backend/.env` - Groq config
- `backend/app/config.py` - Groq settings (model updated multiple times)
- `backend/app/services/classification.py` - Groq service with guardrails
- `backend/app/routes/classification.py` - Endpoints with rate limiting
- `backend/app/main.py` - FastAPI app with middleware, lifespan
- `backend/app/rate_limiter.py` - New: limiter instance
- `backend/.gitignore` - New: excludes sensitive files

### Frontend
- `frontend/src/App.jsx` - Uses `import.meta.env.VITE_API_BASE`
- `frontend/.env.example` / `frontend/.env` - New: API base URL
- `frontend/.gitignore` - Added .env exclusion
- `frontend/vite.config.js` - Added CSP headers

---

## Commands to Run the Project

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm run dev
```

Then open http://localhost:5173 in browser.