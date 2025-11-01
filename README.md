# Normo - Austrian Architectural Legal Document Analysis System

An intelligent AI-powered system for analyzing Austrian building codes, regulations, and legal documents with advanced conversation management and MongoDB integration.

## 🏗️ Features

- **Intelligent Query Routing**: LLM gate automatically determines whether to use simple responses or full document analysis
- **Comprehensive Document Database**: Austrian building codes, OIB guidelines, ÖNORM standards, and federal/state laws
- **Advanced RAG System**: Vector-based document retrieval with precise citations
- **Conversation Management**: MongoDB + JSON hybrid storage with conversation history
- **Modern UI**: React-based frontend with Material-UI components
- **Docker Support**: Complete containerization for easy deployment

## 🚀 Quick Start (Docker - 5 minutes)

### Prerequisites
- Docker Desktop installed
- OpenAI API key

### Setup & Run
```bash
# 1. Clone repository
git clone <repository-url>
cd Normo

# 2. Add your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > normo_backend/.env

# 3. Start everything
docker-compose up -d

# 4. Open http://localhost:3000
```

### Test the System
- **Simple query**: "Hello" → Fast response
- **Architectural query**: "What are building requirements in Austria?" → Full analysis with citations

### Stop
```bash
docker-compose down
```

---

## 🛠️ Alternative: Local Development

### Option 2: Local Development

1. **Prerequisites**:
   - Python 3.12+
   - Node.js 18+
   - MongoDB (optional, will fallback to JSON storage)

2. **Backend Setup**:
   ```bash
   cd normo_backend
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   
   # Set environment variables
   export OPENAI_API_KEY=your_openai_api_key_here
   export MONGODB_URL="mongodb://localhost:27017/normo_db"  # Optional
   
   # Start backend
   uv run python -m src.normo_backend.api.app
   ```

3. **Frontend Setup** (new terminal):
   ```bash
   cd normo_frontend
   npm install
   export REACT_APP_API_URL=http://localhost:8000
   npm start
   ```

## 📁 Project Structure

```
Normo/
├── normo_backend/           # Python FastAPI backend
│   ├── src/normo_backend/
│   │   ├── agents/         # AI agents (planner, retriever, summarizer, gate)
│   │   ├── api/            # FastAPI endpoints
│   │   ├── models/         # Pydantic data models
│   │   ├── services/       # Business logic (storage, vector store)
│   │   ├── utils/          # Utilities (PDF processing, LLM)
│   │   └── prompts/        # LLM prompts
│   ├── arch_pdfs/          # Austrian legal documents
│   ├── conversations/      # JSON conversation storage
│   ├── vector_store/       # ChromaDB vector embeddings
│   └── mongodb-init/       # MongoDB initialization scripts
├── normo_frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React context providers
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript type definitions
│   └── public/             # Static assets
├── docker-compose.yml      # Docker orchestration
└── start-normo.sh         # Quick start script
```

## 🧠 System Architecture

### LLM Gate
- **Smart Routing**: Automatically determines query complexity
- **Simple Queries**: General greetings, help requests → Fast LLM response
- **Complex Queries**: Architectural questions → Full agent workflow

### Agent Workflow
1. **Planner**: Determines required actions
2. **PDF Selector**: Identifies relevant documents
3. **Retriever**: Extracts specific information
4. **Summarizer**: Generates comprehensive responses

### Data Storage
- **MongoDB**: Primary database for conversations
- **JSON Files**: Backup storage for redundancy
- **ChromaDB**: Vector embeddings for document search

## 📚 Document Database

The system includes comprehensive Austrian legal documents:

- **Federal Laws**: BauKG, GewO 1994, AStV, BauV
- **State Laws**: Vienna and Upper Austria building codes
- **OIB Guidelines**: 2019 and 2023 editions covering:
  - Mechanical strength and stability
  - Fire protection (commercial, garages, high-rise)
  - Hygiene and environmental protection
  - Accessibility and safety
  - Sound protection
  - Energy efficiency
- **ÖNORM Standards**: B 1600, B 1800, B 5371

## 🔧 Configuration

### Environment Variables

**Backend**:
- `OPENAI_API_KEY`: Required for LLM functionality
- `MONGODB_URL`: Optional, defaults to JSON storage if not provided

**Frontend**:
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)

### MongoDB Setup (Optional)

If using MongoDB, the system will:
- Auto-initialize the database
- Create necessary indexes
- Sync existing conversations

## 🧪 Testing

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What are building requirements in Austria?"}]}'
```

## 📖 Usage Examples

### General Queries (Simple LLM)
- "Hello, how are you?"
- "What can you help me with?"
- "Thank you for your help"

### Architectural Queries (Full Agent)
- "What are the building height requirements in Austria?"
- "I need playground area requirements for a 5-flat building"
- "What are the fire safety regulations for commercial buildings?"
- "How do I calculate minimum room heights?"

## 🚀 Deployment

### Production Docker
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Environment-Specific Configuration
- Development: Uses local MongoDB
- Production: Configure external MongoDB
- Testing: Uses JSON storage only

## 🔍 Monitoring

### Health Checks
- Backend: `GET /health`
- MongoDB: Check container logs
- Vector Store: Check embedding status

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
```

## 🛠️ Development

### Adding New Documents
1. Place PDFs in `normo_backend/arch_pdfs/`
2. Restart the system to re-embed documents
3. Test with relevant queries

### Customizing Prompts
Edit files in `normo_backend/src/normo_backend/prompts/`:
- `planner.py`: Planning logic
- `pdf_selector.py`: Document selection
- `summarizer.py`: Response generation
- `llm_gate.py`: Query routing

### Adding New Agents
1. Create agent in `normo_backend/src/normo_backend/agents/`
2. Add to workflow in `builder.py`
3. Update prompts as needed

## 📊 Performance

### Response Times
- **Simple Queries**: 1-2 seconds
- **Complex Queries**: 30-60 seconds
- **Document Processing**: 2-5 minutes (first run)

### Resource Usage
- **Memory**: ~2GB (with vector store)
- **Storage**: ~500MB (documents + embeddings)
- **CPU**: Moderate during processing
