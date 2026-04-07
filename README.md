# Fake News Generator

Scrapes real news from major RSS feeds, transforms headlines and descriptions into satirical versions using AI (GPT-4o-mini via OpenAI-compatible API), and provides a per-article chat interface for discussing the content.

## Quick Start

1. Clone the repo
2. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
3. Set your API key in `.env`:
   ```env
   OPENAI_API_KEY=sk-...

   # If using OpenRouter or another OpenAI-compatible provider:
   # OPENAI_BASE_URL=https://openrouter.ai/api/v1
   ```
4. Run everything with Docker:
   ```bash
   docker compose up --build
   ```
5. Open [http://localhost:3000](http://localhost:3000)
6. Click **"Scrape New Articles"** to fetch and transform news

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
    |--- POST /api/articles/:id/chat -> OpenAI-compatible Chat API
    |--- GET  /api/articles/:id/chat -> PostgreSQL query
    |
    v
Celery Worker
    |
    +--> transform_article task
         - Calls LLM API (gpt-4o-mini)
         - Updates article with satirical content
         - Retries 3x with exponential backoff
```

### Services

| Service        | Port | Description                                    |
|----------------|------|------------------------------------------------|
| `frontend`     | 3000 | React + Vite + TailwindCSS                    |
| `backend`      | 3001 | FastAPI with auto-docs at `/docs`              |
| `celery_worker`| -    | Processes LLM transformations asynchronously   |
| `db`           | 5432 | PostgreSQL 16                                  |
| `redis`        | 6379 | Message broker for Celery                      |

## Tech Stack

**Why Python for the backend:** FastAPI provides async-first HTTP handling (ideal for parallel RSS fetching with `asyncio.gather`), automatic OpenAPI docs, and first-class Pydantic integration. Celery is the de-facto standard for distributed task queues in Python, and SQLModel bridges SQLAlchemy and Pydantic cleanly, reducing boilerplate for a project where models serve both DB and API layers.

- **Backend:** Python 3.12, FastAPI, SQLModel (SQLAlchemy), Alembic, Celery + Redis, httpx, feedparser
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, React Router
- **AI:** OpenAI-compatible API (gpt-4o-mini) with JSON response format — supports OpenAI, OpenRouter, and other compatible providers
- **Infrastructure:** Docker Compose, PostgreSQL 16, Redis 7

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | API key for the LLM provider |
| `OPENAI_BASE_URL` | No | Custom base URL for OpenAI-compatible providers (e.g. `https://openrouter.ai/api/v1`) |
| `DATABASE_URL` | No | PostgreSQL connection string (defaults to Docker DB) |
| `REDIS_URL` | No | Redis connection string (defaults to Docker Redis) |

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
│   │   └── versions/
│   │       └── 001_initial_schema.py  # Initial migration
│   └── app/
│       ├── main.py             # FastAPI app, CORS, lifespan
│       ├── config.py           # Settings from env vars (Pydantic)
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
│       │   ├── transformer.py  # LLM satirical transformation
│       │   └── chat.py         # LLM chat with article context
│       └── tasks/
│           ├── celery_app.py   # Celery configuration
│           └── transform.py    # Async transform task with retry
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts          # Dev proxy to backend (configurable)
    ├── tailwind.config.js
    └── src/
        ├── main.tsx            # React entry point
        ├── App.tsx             # Router setup
        ├── api/
        │   └── client.ts       # API client (typed fetch wrapper)
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

Three tables managed via Alembic migrations:

- **sources** — RSS feed sources (NYT, NPR, Guardian)
- **articles** — original + satirical content, transform status, timestamps
- **chat_messages** — per-article chat history (user + assistant messages)

Key design decisions:
- `original_url` is UNIQUE for deduplication across scrape runs
- `fake_title`/`fake_description` are NULL until transformation completes
- `transform_status` enum (`pending` → `processing` → `completed`/`failed`) tracks the pipeline state
- `updated_at` auto-updates on every article modification via SQLAlchemy `onupdate`
- `published_at` is parsed from RSS feed entries (supports `published`, `updated`, `created` fields)

### Migrations

The project uses Alembic for database migrations. The initial migration (`001_initial_schema.py`) creates all three tables with proper constraints, indexes, and foreign keys. Migrations run automatically on startup via `alembic upgrade head` in the Docker entrypoint.

```bash
# Generate a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head
```

## Async Pipeline

1. User clicks "Scrape" → `POST /api/scrape`
2. Scraper fetches 3 RSS feeds in parallel (`asyncio.gather`)
3. New articles are upserted to DB (deduped by URL)
4. Each new article gets a Celery task: `transform_article.delay(id)`
5. Celery worker calls the LLM API, updates article with satirical content
6. On failure: auto-retry 3x with exponential backoff (10s, 20s, 40s)

The transformation is fully asynchronous — the scrape endpoint returns immediately with the count of scraped articles and enqueued jobs. The frontend polls for completed articles.

## Error Handling

- **RSS fetch failures**: Individual feed errors don't block other feeds (`return_exceptions=True` in `asyncio.gather`)
- **LLM API failures**: Celery retries 3x with exponential backoff; article status set to `failed` on final failure
- **Duplicate articles**: Deduplication by `original_url` (UNIQUE constraint + pre-insert check)
- **Missing articles**: 404 responses for invalid article IDs in detail/chat endpoints
- **Frontend**: Error states displayed in UI, loading indicators during async operations

## Development

**Backend auto-docs:** [http://localhost:3001/docs](http://localhost:3001/docs) (Swagger UI)

**Hot reload:** Both backend (uvicorn `--reload`) and frontend (Vite HMR) support hot reload via Docker volume mounts.

**Local development (without Docker):**
```bash
# Backend
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Set env vars (DATABASE_URL, REDIS_URL, OPENAI_API_KEY, OPENAI_BASE_URL)
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload

# Celery worker (separate terminal)
PYTHONPATH=. celery -A app.tasks.celery_app:celery worker --loglevel=info --pool=solo

# Frontend
cd frontend
npm install
npm run dev
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
