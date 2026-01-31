# ClipContext

> Find any topic in any YouTube video instantly.

Someone shared a clip from a 2-hour podcast. You want to hear more context. But scrubbing through the full video to find that 30-second segment? Painful.

**ClipContext** lets you paste a YouTube URL, describe what you're looking for, and jump directly to the exact timestamp.

## 🎯 Problem

- Long-form content (podcasts, interviews, lectures) is exploding
- People share clips but finding context in 1-3 hour videos is frustrating  
- YouTube's search only works on titles/descriptions, not actual content
- Existing tools are either creator-focused or require accounts

## 💡 Solution

Semantic search inside any YouTube video:

1. Paste YouTube URL
2. Describe what you're looking for (natural language)
3. Get exact timestamps with context
4. Click to jump directly to that moment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                   (Next.js / React)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                    (FastAPI + Uvicorn)                       │
├─────────────────────────────────────────────────────────────┤
│  POST /api/search                                            │
│  Body: { youtube_url, query }                                │
│  Response: { results: [{ timestamp, text, score }] }         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Transcript│  │ Embedding │  │  Vector   │
│  Service  │  │  Service  │  │   Store   │
│           │  │           │  │           │
│ youtube-  │  │ OpenAI /  │  │ Postgres  │
│ transcript│  │ sentence- │  │ + pgvector│
│ -api      │  │ transform │  │           │
└───────────┘  └───────────┘  └───────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Backend** | FastAPI (Python) | Async, fast, great docs |
| **Database** | PostgreSQL + pgvector | Production-ready vector search |
| **Embeddings** | sentence-transformers | No API costs, fast, local |
| **Cache** | Redis | Transcript caching |
| **Frontend** | Next.js | SSR, good DX |
| **Deployment** | Docker + Kubernetes | Production-grade, demonstrates DevOps skills |
| **CI/CD** | GitHub Actions | Industry standard |


## 🚀 Roadmap

### Week 1: Core Backend
- [x] Project setup & architecture
- [ ] Transcript fetching service
- [ ] Embedding generation
- [ ] Basic vector search (in-memory first)
- [ ] FastAPI endpoints

### Week 2: Database & API
- [ ] PostgreSQL + pgvector setup
- [ ] Redis caching for transcripts
- [ ] Rate limiting
- [ ] Error handling

### Week 3: Frontend
- [ ] Next.js setup
- [ ] Search interface
- [ ] Results display with video preview
- [ ] Mobile responsive

### Week 4: DevOps & Launch
- [ ] Docker containerization
- [ ] Kubernetes manifests
- [ ] GitHub Actions CI/CD
- [ ] Deploy to production
- [ ] Domain & SSL

### Post-Launch
- [ ] User accounts (optional)
- [ ] Search history
- [ ] Browser extension
- [ ] API for developers

## 🏃 Quick Start

```bash
# Clone
git clone https://github.com/yourusername/clipcontext.git
cd clipcontext

# Run with Docker Compose
docker-compose up -d

# Or run locally
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```




## 🧪 Test It

Once running, try searching Steve Jobs' Stanford speech:
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=UF8uR6Z6KLc",
    "query": "stay hungry stay foolish",
    "max_results": 3
  }'
```

**Result:** Finds the exact moment at **14:12** where Stev çJobs says "Stay Hungry. Stay Foolish."

Or open the interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)


## 📊 Metrics to Track

- Search latency (target: <500ms)
- Transcript fetch time
- Embedding generation time
- User searches per day
- Cache hit rate

## 🔗 Building in Public

Follow the journey on X: [@ermias](https://x.com/ermishoo)

## 📝 License

MIT

---
