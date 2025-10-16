# Normo - Quick Docker Setup

## 🚀 Run with Docker (5 minutes)

### 1. Prerequisites
- Docker Desktop installed
- OpenAI API key

### 2. Setup
```bash
# Clone the repository
git clone <repository-url>
cd Normo

# Add your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > normo_backend/.env
```

### 3. Start Everything
```bash
docker-compose up -d
```

### 4. Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

### 5. Test
Open http://localhost:3000 and ask:
- "Hello" (simple response)
- "What are building requirements in Austria?" (full analysis)

## 🛑 Stop
```bash
docker-compose down
```

## 🔧 Troubleshooting

**Port already in use?**
```bash
# Stop existing services
docker-compose down
# Or change ports in docker-compose.yml
```

**Need to reset everything?**
```bash
docker-compose down -v
docker-compose up -d
```

**Check logs:**
```bash
docker-compose logs -f
```

## 📁 What's Included
- ✅ Backend API with AI agents
- ✅ React frontend
- ✅ MongoDB database
- ✅ Vector store for document search
- ✅ All Austrian legal documents

That's it! The system will automatically process documents on first use.