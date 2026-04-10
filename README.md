# 🤖 Agentic RAG Enterprise AI

A production-ready **multi-agent AI system** for enterprise document analysis, built with Python (FastAPI) and React. The system automates document ingestion, intelligent Q&A, compliance validation, and report generation using a Retrieval-Augmented Generation (RAG) pipeline.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)                │
│   Document Upload │ Query Interface │ Report Viewer          │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                │
│                                                             │
│  ┌──────────────────── Agent Orchestrator ─────────────┐   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  Ingestion  │  │  Retrieval  │  │  Reasoning │  │   │
│  │  │    Agent    │  │    Agent    │  │    Agent   │  │   │
│  │  │ PDF/Word/   │  │ FAISS RAG   │  │  Gemini    │  │   │
│  │  │ Web Sources │  │  Pipeline   │  │    LLM     │  │   │
│  │  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              Action Agent                    │    │   │
│  │  │  Summarize │ Validate │ Generate Reports     │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Services: FAISS Vector Store │ Gemini LLM │ Memory Mgmt   │
│  Utils: Guardrails │ Evaluator │ Structured Logging         │
└─────────────────────────────────────────────────────────────┘
```

### Agents

| Agent | Responsibility |
|-------|----------------|
| **Ingestion Agent** | Processes PDF, Word (.docx), text files, and web URLs into chunks |
| **Retrieval Agent** | Semantic search using FAISS vector database with HuggingFace embeddings |
| **Reasoning Agent** | Contextual understanding using Google Gemini LLM with conversation memory |
| **Action Agent** | Triggers actions: summarization, compliance validation, report generation |
| **Orchestrator** | Coordinates all agents in the multi-step pipeline |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A [Google AI Studio API Key](https://aistudio.google.com/app/apikey) (free tier available)

### 1. Clone and Configure

```bash
git clone https://github.com/lasithapro/agentic-rag-enterprise-ai.git
cd agentic-rag-enterprise-ai

# Copy and edit environment config
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This starts:
- **Backend API** → http://localhost:8000
- **Frontend UI** → http://localhost:3000
- **API Docs** → http://localhost:8000/api/docs

### 3. Use the Application

1. Open http://localhost:3000
2. Go to **Documents** tab → Upload a PDF, Word file, or enter a URL
3. Go to **Query Assistant** → Ask questions about your documents
4. Go to **Reports** → Generate summaries, compliance checks, or analysis reports

---

## 💻 Local Development (without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Set API URL (optional, defaults to proxy)
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm start
```

---

## 📚 API Reference

Full interactive documentation is available at **http://localhost:8000/api/docs**

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload a document (PDF, DOCX, TXT) |
| `POST` | `/api/v1/documents/ingest-url` | Ingest content from a web URL |
| `GET` | `/api/v1/documents` | List all documents in knowledge base |
| `DELETE` | `/api/v1/documents/{id}` | Remove a document |
| `POST` | `/api/v1/query` | Query documents using RAG pipeline |
| `GET` | `/api/v1/memory/{session_id}` | Get conversation history |
| `DELETE` | `/api/v1/memory/{session_id}` | Clear conversation history |
| `POST` | `/api/v1/reports/generate` | Generate full analysis report |
| `POST` | `/api/v1/reports/summarize` | Generate document summary |
| `POST` | `/api/v1/reports/compliance` | Run compliance validation |
| `GET` | `/api/v1/health` | Health check |

### Example: Upload and Query

```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@policy.pdf"

# Query the knowledge base
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key compliance requirements?",
    "session_id": "my-session-123",
    "top_k": 5
  }'

# Generate compliance report
curl -X POST http://localhost:8000/api/v1/reports/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["<doc-id-from-upload>"],
    "compliance_areas": ["GDPR", "data privacy"]
  }'
```

---

## 🧪 Running Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
pytest tests/test_services.py -v
```

---

## 🏢 Real-World Use Cases

### 1. Policy Document Compliance Validation
- Upload company policy documents
- Run compliance checks against GDPR, SOX, HIPAA, or custom frameworks
- Get detailed compliance reports with severity ratings and recommendations

### 2. Enterprise Knowledge Assistant
- Ingest internal documentation, wikis, and reports
- Enable employees to query the knowledge base in natural language
- Maintain conversation context across sessions

### 3. Contract Analysis
- Upload contracts and legal documents
- Extract key clauses, obligations, and risk factors
- Generate structured analysis reports

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | *(required)* | Google Gemini API key |
| `LLM_MODEL` | `gemini-1.5-flash` | Gemini model to use |
| `LLM_TEMPERATURE` | `0.1` | Response creativity (0-1) |
| `CHUNK_SIZE` | `1000` | Document chunk size in characters |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size |

---

## 🛡️ Security & Guardrails

- **Input validation**: Length limits, harmful pattern detection
- **Output validation**: Response safety checks, truncation
- **PII detection**: Identifies and can mask personally identifiable information
- **CORS**: Configurable allowed origins
- **Rate limiting**: Built-in via uvicorn worker configuration

---

## 🗂️ Project Structure

```
agentic-rag-enterprise-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/routes/          # REST API endpoints
│   │   ├── agents/              # Multi-agent system
│   │   │   ├── orchestrator.py  # Agent coordination
│   │   │   ├── ingestion_agent.py
│   │   │   ├── retrieval_agent.py
│   │   │   ├── reasoning_agent.py
│   │   │   └── action_agent.py
│   │   ├── services/            # Core services
│   │   │   ├── vector_store.py  # FAISS integration
│   │   │   ├── llm_service.py   # Gemini LLM
│   │   │   ├── document_processor.py
│   │   │   └── report_service.py
│   │   ├── core/                # Config, logging, memory
│   │   ├── models/schemas.py    # Pydantic schemas
│   │   └── utils/               # Guardrails, evaluator
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component
│   │   ├── components/          # React components
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── QueryInterface.jsx
│   │   │   ├── ReportViewer.jsx
│   │   │   └── Sidebar.jsx
│   │   └── services/api.js      # API client
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run tests: `cd backend && pytest tests/ -v`
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.