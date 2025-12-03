# NLP Agentic AI Feedback Analysis System

A production-grade multi-agent AI system for feedback analysis using LangChain, ChromaDB, and FastAPI with sentiment analysis, topic modeling, and RAG capabilities.

## Project Status

**Current Phase:** Iteration 1 Complete ✅
**Next Phase:** Iteration 2 - Agent Implementation

## Tech Stack

- **Agent Framework:** LangChain
- **API:** FastAPI (Async)
- **Vector Store:** ChromaDB
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Sentiment Analysis:** VADER
- **Topic Modeling:** BERTopic + UMAP
- **Summarization:** TextRank (spaCy)

## Current Features (Iteration 1)

✅ Project structure with modular architecture
✅ Configuration management (YAML + environment variables)
✅ Embedding service with sentence-transformers
✅ ChromaDB vector store integration
✅ FastAPI application with health check
✅ Structured logging with JSON support
✅ Docker containerization setup

## Quick Start

### Local Development

1. **Create virtual environment**
```powershell
python -m venv .venv
# Activate on Windows PowerShell:
.venv\Scripts\Activate.ps1
# Or on Unix/Mac:
# source .venv/bin/activate
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. **Create .env file** (copy from .env.example)
```powershell
# Windows PowerShell:
Copy-Item .env.example .env
# Or on Unix/Mac:
# cp .env.example .env
```

4. **Run the application**
```powershell
python -m uvicorn src.api.main:app --reload
```

5. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the API**
```bash
curl http://localhost:8000/health
```

## API Endpoints

### Current Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check with service status
- `GET /info` - System information

### Coming in Iteration 2

- `POST /upload` - Upload feedback data
- `POST /analyze` - Analyze feedback and generate report
- `GET /analysis/{id}` - Get analysis results

## Project Structure

```
project_root/
├── src/
│   ├── agents/              # LangChain agents (Iteration 2)
│   ├── api/
│   │   └── main.py          # FastAPI application ✅
│   ├── models/              # Pydantic schemas (Iteration 2)
│   ├── services/
│   │   ├── embeddings.py    # Embedding service ✅
│   │   └── vectorstore.py   # ChromaDB service ✅
│   └── utils/
│       ├── config.py        # Configuration loader ✅
│       └── logging_config.py # Logging setup ✅
├── tests/                   # Test suite (Iteration 3)
├── test_data/              # Sample data (Iteration 3)
├── config.yaml             # Configuration ✅
├── .env.example            # Environment template ✅
├── requirements.txt        # Dependencies ✅
├── Dockerfile              # Docker config ✅
└── docker-compose.yml      # Docker Compose ✅
```

## Configuration

### config.yaml
Main configuration file with model settings, API config, and NLP parameters.

### .env
Environment-specific settings (create from .env.example).

## Testing

```bash
# Run all tests (Iteration 3)
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Development Roadmap

### ✅ Iteration 1: Foundation (Complete)
- Project structure
- Configuration management
- Core services (embeddings, vector store)
- FastAPI scaffold
- Docker setup

### 🔄 Iteration 2: Agents & Pipeline (Next)
- Data Ingestion Agent
- Analysis Agent (VADER + BERTopic)
- Retrieval Agent (RAG)
- Synthesis Agent (Report generation)
- NLP processors
- API endpoints for upload/analysis

### ⏳ Iteration 3: Production Ready (Upcoming)
- Unit & integration tests
- Exception handling
- Comprehensive logging
- API documentation
- Deployment optimization

## Team

6-person development team
CS4063 - Natural Language Processing
Development Track Project

## Documentation

- [CLAUDE.md](CLAUDE.md) - Detailed architecture and implementation guide
- [Plan File](~/.claude/plans/) - Complete implementation plan

## License

Educational Project - CS4063 NLP Course

---

**Last Updated:** 2025-12-03
**Version:** 1.0.0 (Iteration 1)
