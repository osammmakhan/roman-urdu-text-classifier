# Roman Urdu Text Classifier — Planning

## Problem
Social and messaging platforms in Pakistan carry huge volumes of Roman Urdu text (Urdu written in Latin script), which most off-the-shelf NLP tools handle poorly since it's not standardized and mixes languages/spellings freely. This project builds a small full-stack tool that ingests Roman Urdu text and classifies it (sentiment: positive / negative / neutral), storing and displaying results so patterns are visible at a glance.

## Goal
A working end-to-end app: paste or upload Roman Urdu text → backend classifies it via an LLM with guardrails → result is stored → frontend shows it in a filterable table.

This is a scoped personal project built to demonstrate full-stack ownership (DB + API + frontend) and AI-agent-assisted development using Cursor, not a production system.

## Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **Classification:** OpenAI API, prompt-based classification with guardrails (fixed label set, confidence score, no invented categories)
- **Frontend:** React + Tailwind CSS
- **Hosting:** TBD — decided after the app is working locally

## Scope (v1)
- `POST /classify` endpoint: accepts raw text, returns label + confidence
- SQLite table: `id, text, label, confidence, created_at`
- `GET /results` endpoint: returns stored classifications, with optional filter by label
- Frontend: textarea input (single text) + table view of past results, filterable by label
- Basic error handling: empty input, API failures, malformed responses from the model

## Out of scope (v1)
- Topic clustering / narrative grouping
- Real-time alerts
- Multi-language detection (assume input is already Roman Urdu)
- Auth / multi-user support
- CSV batch upload (stretch goal if time allows)

## Guardrails for classification prompt
- Fixed label set only: positive / negative / neutral (no free-text labels)
- Model must return a confidence score, not just a label
- No fabricated or hedged output — if text is empty/gibberish, return a clear "unclassifiable" result instead of guessing
- Log raw model output for debugging before parsing

## Build approach
- Built using Cursor as the primary AI coding tool
- Commits kept small and sequential (not one large commit) to show iterative process
- This file updated as decisions change during the build

## Open questions / decisions to revisit
- Hosting choice (backend + frontend) — decide after core app works locally
- Whether to add CSV batch upload as a stretch feature
- Whether to expand label set (e.g. add "mixed") based on real test data behavior