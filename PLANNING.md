# Roman Urdu Text Classifier — Planning

## Problem
Social and messaging platforms in Pakistan carry huge volumes of Roman Urdu text (Urdu written in Latin script), which most off-the-shelf NLP tools handle poorly since it's not standardized and mixes languages/spellings freely. This project builds a small full-stack tool that ingests Roman Urdu text and classifies it (sentiment: positive / negative / neutral), storing and displaying results so patterns are visible at a glance.

## Goal
A working end-to-end app: paste or upload Roman Urdu text → backend classifies it via an LLM with guardrails → result is stored → frontend shows it in a filterable table.

This is a scoped personal project built to demonstrate full-stack ownership (DB + API + frontend) and AI-agent-assisted development using Cursor, not a production system.

## Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **Classification:** Groq API (llama-3.3-70b-versatile), prompt-based classification with guardrails (fixed label set, confidence score, no invented categories)
- **Frontend:** React + Vite + Tailwind CSS v3
- **Hosting:** TBD — decided after the app is working locally

## Scope (v1) — ✅ ALL COMPLETE
- [x] `POST /classify` endpoint: accepts raw text, returns label + confidence
- [x] SQLite table: `id, text, label, confidence, created_at`
- [x] `GET /results` endpoint: returns stored classifications, with optional filter by label
- [x] Frontend: textarea input (single text) + table view of past results, filterable by label
- [x] Basic error handling: empty input, API failures, malformed responses from the model

## Production Hardening (Added) — ✅ ALL COMPLETE
- [x] Rate limiting: 10 requests/minute per IP on `/classify` (slowapi)
- [x] Request logging middleware with request IDs and timing headers
- [x] API key validation on startup (warns if GROQ_API_KEY not configured)
- [x] Backend .gitignore excluding sensitive files
- [x] Frontend .env/.env.example with VITE_API_BASE for configurable API URL
- [x] CSP headers via Vite config for production security
- [x] CORS configured for localhost:3000 and localhost:5173
- [x] Input validation: Pydantic min_length=1, max_length=5000
- [x] SQL injection prevention via SQLAlchemy ORM
- [x] XSS prevention via React auto-escaping + CSP

## Out of scope (v1)
- Topic clustering / narrative grouping
- Real-time alerts
- Multi-language detection (assume input is already Roman Urdu)
- Auth / multi-user support
- CSV batch upload (stretch goal if time allows)

## Guardrails for classification prompt
- Fixed label set only: positive / negative / neutral / unclassifiable (no free-text labels)
- Model must return a confidence score, not just a label (clamped 0.0-1.0)
- No fabricated or hedged output — if text is empty/gibberish, return a clear "unclassifiable" result instead of guessing
- Log raw model output for debugging before parsing
- Malformed JSON responses default to "neutral"/0.5

## Build approach
- Built using Cursor as the primary AI coding tool
- Commits kept small and sequential (not one large commit) to show iterative process
- This file updated as decisions change during the build

## Open questions / decisions to revisit
- Hosting choice (backend + frontend) — decide after core app works locally
- Whether to add CSV batch upload as a stretch feature
- Whether to expand label set (e.g. add "mixed") based on real test data behavior
- Add unit tests for classification service
- Verify working Groq model on console.groq.com

## Current Status (2026-09-05)
**All 20 todos completed.** Application runs locally:
- Backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000` (port 8000)
- Frontend: `cd frontend && npm run dev` (port 5173)
- Groq model: `llama-3.3-70b-versatile` (configured in backend/app/config.py)