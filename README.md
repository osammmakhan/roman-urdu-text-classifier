# RomanUrdu.ai

<div align="center">

![RomanUrdu.ai Logo](frontend/public/favicon.svg)

**Classify Roman Urdu text sentiment in real-time**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## Overview

RomanUrdu.ai is a full-stack web application that classifies Roman Urdu text (Urdu written in Latin script) into sentiment categories (positive, negative, neutral) with probability distributions. Built with FastAPI, React, and powered by Groq API.

### Features

- **Real-time Classification**: Instant sentiment analysis of Roman Urdu text
- **Probability Distribution**: Visual breakdown of sentiment probabilities
- **Dark/Light Theme**: Toggle between themes with localStorage persistence
- **Filterable History**: View and filter past classifications
- **Responsive Design**: Works on desktop and mobile devices
- **Rate Limited**: 10 requests per minute per IP
- **Fallback Classification**: Rule-based classification when API unavailable

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite |
| **LLM** | Groq API (`openai/gpt-oss-20b`) |
| **Frontend** | React + Vite |
| **Styling** | Tailwind CSS v3 |
| **Fonts** | Space Grotesk, Geist, JetBrains Mono |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/roman-urdu-text-classifier.git
   cd roman-urdu-text-classifier
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Development Servers**

   Terminal 1 (Backend):
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Open** http://localhost:5173 in your browser

## API Documentation

### POST /api/classify

Classify Roman Urdu text.

```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "achha din hai"}'
```

**Response:**
```json
{
  "id": 1,
  "text": "achha din hai",
  "label": "positive",
  "confidence": 0.85,
  "probabilities": {
    "positive": 0.85,
    "neutral": 0.10,
    "negative": 0.05
  },
  "created_at": "2026-09-14T05:30:00Z"
}
```

### GET /api/results

Retrieve classification results.

```bash
# Get all results
curl http://localhost:8000/api/results

# Filter by label
curl "http://localhost:8000/api/results?label=positive"
```

For complete API documentation, visit http://localhost:8000/docs after starting the backend.

## Project Structure

```
roman-urdu-text-classifier/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic models
│   │   ├── routes/              # API endpoints
│   │   └── services/            # Business logic
│   ├── tests/                   # Unit tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main component
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── public/                  # Static assets
│   └── package.json
├── PLANNING.md                  # Project plan
├── DECISIONS.md                 # Decision log
└── README.md
```

## Configuration

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Your Groq API key (required) |
| `GROQ_MODEL` | `openai/gpt-oss-20b` | Model to use |
| `DATABASE_URL` | `sqlite:///./urdu_classifier.db` | Database connection |
| `API_PORT` | `8000` | Server port |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `http://localhost:8000/api` | Backend API URL |

## Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend lint
cd frontend
npm run lint

# Frontend build
cd frontend
npm run build
```

## Deployment

### Quick Deploy to Render.com

1. Push to GitHub
2. Create Web Service for backend (Root Directory: `backend`)
3. Create Static Site for frontend (Root Directory: `frontend`)
4. Set environment variables

## License

This project is licensed under the MIT License.
