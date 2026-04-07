# Fake News Generator

Scrapes real news from major RSS feeds, transforms headlines and descriptions into satirical versions using AI (GPT-4o-mini), and provides a per-article chat interface for discussing the content.

## Quick Start

1. Clone the repo
2. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=sk-...
   ```
3. Run everything with Docker:
   ```bash
   docker-compose up --build
   ```
4. Open [http://localhost:3000](http://localhost:3000)
5. Click **"Scrape New Articles"** to fetch and transform news

## Architecture

```
User Browser (React)
    |
    | HTTP (port 3000, Vite dev proxy -> 3001)
    v
FastAPI Backend (port 3001)
    |
    |--- POST /api/scrape ---> Scraper Service (httpx + feedparser)
    |                              |
    |                              +--> Upsert articles to PostgreSQL
    |                              +--> Enqueue Celery tasks
    |
    |--- GET /api/articles -----> PostgreSQL query
    |--- GET /api/articles/:id -> PostgreSQL query
    |--- GET /api/sources ------> PostgreSQL query
    |--- POST /api/articles/:id/chat -> OpenAI Chat API
    |--- GET  /api/articles/:id/chat -> PostgreSQL query
    |
    v
Celery Worker
    |
    +--> transform_article task
         - Calls OpenAI API (gpt-4o-mini)
         - Updates article with satirical content
         - Retries 3x with exponential backoff
```

### Services

| Service        | Port | Description                                    |
|----------------|------|------------------------------------------------|
| `frontend`     | 3000 | React + Vite + TailwindCSS                    |
| `backend`      | 3001 | FastAPI with auto-docs at `/docs`              |
| `celery_worker`| -    | Processes OpenAI transformations asynchronously|
| `db`           | 5432 | PostgreSQL 16                                  |
| `redis`        | 6379 | Message broker for Celery                      |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLModel (SQLAlchemy), Alembic, Celery + Redis, httpx, feedparser
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, React Router
- **AI:** OpenAI API (gpt-4o-mini) with JSON response format
- **Infrastructure:** Docker Compose, PostgreSQL 16, Redis 7

## Project Structure

```
/
├── docker-compose.yml          # All services orchestration
├── .env.example                # Required env vars template
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini             # Database migration config
│   ├── alembic/
│   │   ├── env.py              # Migration environment setup
│   │   └── versions/           # Auto-generated migrations
│   └── app/
│       ├── main.py             # FastAPI app, CORS, lifespan
│       ├── config.py           # Settings from env vars
│       ├── database.py         # SQLModel engine + session
│       ├── models.py           # Source, Article, ChatMessage tables
│       ├── schemas.py          # Pydantic request/response models
│       ├── routers/
│       │   ├── scrape.py       # POST /api/scrape
│       │   ├── articles.py     # GET /api/articles, GET /api/articles/:id
│       │   ├── sources.py      # GET /api/sources
│       │   └── chat.py         # GET/POST /api/articles/:id/chat
│       ├── services/
│       │   ├── scraper.py      # RSS fetch + parse + dedup + upsert
│       │   ├── transformer.py  # OpenAI satirical transformation
│       │   └── chat.py         # OpenAI chat with article context
│       └── tasks/
│           ├── celery_app.py   # Celery configuration
│           └── transform.py    # Async transform task with retry
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts          # Dev proxy to backend
    ├── tailwind.config.js
    └── src/
        ├── main.tsx            # React entry point
        ├── App.tsx             # Router setup
        ├── api/
        │   └── client.ts       # API client (fetch wrapper)
        ├── components/
        │   ├── Layout.tsx      # Header + container
        │   ├── NewsFeed.tsx    # Article list + scrape button
        │   ├── ArticleCard.tsx # Card in feed
        │   ├── ArticleDetail.tsx # Full article + original toggle
        │   ├── ChatPanel.tsx   # Chat interface per article
        │   └── SourceFilter.tsx # Filter by news source
        ├── hooks/
        │   ├── useArticles.ts  # Fetch + state for article list
        │   └── useChat.ts      # Chat messages + send logic
        └── types/
            └── index.ts        # TypeScript interfaces
```

## API Endpoints

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | `/api/scrape`               | Trigger RSS scrape + transform |
| GET    | `/api/articles`             | List articles (filterable)     |
| GET    | `/api/articles/:id`         | Single article detail          |
| GET    | `/api/sources`              | List news sources              |
| POST   | `/api/articles/:id/chat`    | Send chat message              |
| GET    | `/api/articles/:id/chat`    | Get chat history               |

**Query params for `/api/articles`:** `source_id`, `status` (pending/processing/completed/failed), `page`, `per_page`

## Database Schema

Three tables:

- **sources** — RSS feed sources (NYT, NPR, Guardian)
- **articles** — original + satirical content, transform status, timestamps
- **chat_messages** — per-article chat history (user + assistant messages)

Key design decisions:
- `original_url` is UNIQUE for deduplication
- `fake_title`/`fake_description` are NULL until transformation completes
- `transform_status` enum tracks the pipeline state
- `updated_at` auto-updates on every article modification via SQLAlchemy `onupdate`
- `published_at` is parsed from RSS feed entries (supports `published`, `updated`, `created` fields)

### Migrations

The project uses Alembic for database migrations. The initial migration (`001_initial_schema.py`) creates all three tables with proper constraints and indexes. Migrations run automatically on startup via `alembic upgrade head` in the Docker entrypoint.

## Async Pipeline

1. User clicks "Scrape" → `POST /api/scrape`
2. Scraper fetches 3 RSS feeds in parallel (`asyncio.gather`)
3. New articles are upserted to DB (deduped by URL)
4. Each new article gets a Celery task: `transform_article.delay(id)`
5. Celery worker calls OpenAI, updates article with satirical content
6. On failure: auto-retry 3x with exponential backoff (10s, 20s, 40s)

## Development

**Backend auto-docs:** [http://localhost:3001/docs](http://localhost:3001/docs) (Swagger UI)

**Hot reload:** Both backend (uvicorn `--reload`) and frontend (Vite HMR) support hot reload via Docker volume mounts.

**Generate a new migration:**
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head
```

## What Could Be Improved

- SSE/WebSocket for real-time transform status updates
- Streaming LLM responses in chat
- Scheduled scraping via Celery Beat
- Article similarity via embeddings (cosine similarity dedup across sources)
- Rate limiting on API endpoints
- Comprehensive test suite (pytest + httpx test client)
- Pagination metadata (total count) in API responses
- Frontend pagination controls
