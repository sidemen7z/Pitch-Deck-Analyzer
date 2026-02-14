# Pitch Deck Analyzer

AI-powered NLP system that automatically extracts and structures key investment information from startup pitch decks (PDF/PPT).

## Features

- Document parsing (PDF and PowerPoint)
- Content classification with 11 categories
- Field-level information extraction with confidence scoring
- Investment signals generation (green/red/yellow flags)
- Risk assessment and recommendations
- **Local LLM support with Ollama** (run completely offline!)
- Web dashboard for visualization
- MongoDB Atlas integration
- Real-time processing pipeline

## Setup

### Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas connection string and Gemini API key
```

3. Start the backend server:
```bash
python -m uvicorn app.main:app --reload
```

Backend API will be available at http://localhost:8000

### Frontend

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the frontend development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Configuration

Key environment variables:
- `LLM_PROVIDER`: Choose "gemini" or "ollama" (default: gemini)
- `GEMINI_API_KEY`: Your Gemini API key (if using Gemini)
- `OLLAMA_URL`: Ollama server URL (if using local LLM)
- `OLLAMA_MODEL`: Model name like "llama3.1:8b" (if using Ollama)
- `MONGODB_URL`: MongoDB Atlas connection string
- `REDIS_URL`: Redis connection string
- `MAX_FILE_SIZE_MB`: Maximum upload file size (default: 50MB)

## Local LLM Setup

Want to run completely offline? See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for instructions on using local LLMs with Ollama.

Benefits:
- ✅ Complete privacy - data never leaves your machine
- ✅ No API costs
- ✅ Works offline
- ✅ Fast processing with GPU acceleration

## Testing

Run tests:
```bash
pytest
```

Run property-based tests:
```bash
pytest -m property
```

## Project Structure

```
app/
├── models/          # Data models and database schemas
├── services/        # Business logic components
├── api/            # API endpoints
├── utils/          # Utility functions
└── main.py         # Application entry point
```
