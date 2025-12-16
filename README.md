# CrisisFlow - Real-Time Disaster Intelligence Platform

A full-stack application that aggregates unstructured disaster data, uses AI to verify and structure that data, and visualizes it on a real-time map for emergency responders.

## Project Structure

```
Catalyst AI/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic (AI processing)
│   │   └── database.py  # Database configuration
│   ├── main.py          # FastAPI application entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js frontend
│   ├── app/             # Next.js App Router
│   ├── components/      # React components
│   └── package.json     # Node.js dependencies
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Add your API keys to `.env` (optional for Phase 7):
```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

6. Run the backend server:
```bash
python main.py
# Or: uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# Or: yarn install
```

3. Run the development server:
```bash
npm run dev
# Or: yarn dev
```

The frontend will be available at `http://localhost:3000`

## Features

### Phase 1: Backend Skeleton ✅
- FastAPI backend structure
- Health check endpoint
- CORS middleware configured

### Phase 2: Database & Data Models ✅
- SQLite database with SQLAlchemy
- Report model with all required fields
- Pydantic schemas for validation

### Phase 3: AI Logic Service ✅
- Dummy AI processor (keyword-based)
- Modular structure for easy LLM integration

### Phase 4: API Endpoints ✅
- `POST /api/v1/reports/` - Create a new report
- `GET /api/v1/reports/` - Get all reports
- `GET /api/v1/reports/{id}` - Get a specific report

### Phase 5: Frontend Setup ✅
- Next.js 14 with App Router
- Tailwind CSS with dark mode
- ReportFeed component for displaying reports

### Phase 6: Map Component ✅
- Leaflet integration
- Real-time map visualization
- Markers for each report (color-coded by severity)
- Mock coordinates for development

### Phase 7: Real AI Integration ✅
- OpenAI GPT-3.5-turbo support
- Google Gemini Pro support
- Graceful error handling with fallback to dummy logic
- JSON parsing with error recovery

## API Usage

### Create a Report

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/reports/" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Fire reported at 5th and Main Street"}'
```

### Get All Reports

```bash
curl "http://127.0.0.1:8000/api/v1/reports/"
```

### Using Real AI (Phase 7)

To use real AI processing, add the `provider` query parameter:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/reports/?provider=openai" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Fire reported at 5th and Main Street"}'
```

Available providers:
- `openai` - Uses OpenAI GPT-3.5-turbo (requires OPENAI_API_KEY)
- `gemini` - Uses Google Gemini Pro (requires GOOGLE_API_KEY)
- `dummy` - Uses keyword-based dummy logic (default)

## Development Notes

- The backend uses SQLite by default (database file: `crisisflow.db`)
- The frontend includes mock data fallback if the backend isn't running
- Map coordinates are currently mocked (random coordinates near San Francisco)
- All AI processing gracefully falls back to dummy logic if LLM calls fail

## Next Steps

- Add geocoding service to convert location strings to coordinates
- Implement real-time updates (WebSockets)
- Add user authentication
- Implement report verification workflow
- Add resource tracking (needed vs. available)
- Deploy to production

