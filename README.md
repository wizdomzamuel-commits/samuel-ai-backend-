# Samuel AI

A personal AI assistant backend built with FastAPI: stores notifications and
uses OpenAI to generate daily and weekly natural-language summaries.

## Features

- Modular FastAPI structure (routes / services / models / schemas separated)
- Notification storage via SQLAlchemy (SQLite locally, Postgres-ready for Railway)
- OpenAI integration for daily/weekly summary generation
- In-process scheduler (APScheduler) that auto-generates summaries on a cron schedule
- Simple API-key auth suitable for a single-user personal assistant
- Railway deployment config included (`Procfile` + `railway.json`)

## Local setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set API_KEY and OPENAI_API_KEY at minimum

uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

All endpoints (except `/` and `/health`) require an `X-API-Key` header
matching the `API_KEY` value in your `.env`.

## Endpoints

| Method | Path                            | Description                    |
|--------|----------------------------------|---------------------------------|
| POST   | /api/v1/notifications             | Create a notification          |
| GET    | /api/v1/notifications             | List notifications             |
| GET    | /api/v1/notifications/{id}        | Get one notification           |
| PATCH  | /api/v1/notifications/{id}        | Update a notification          |
| DELETE | /api/v1/notifications/{id}        | Delete a notification          |
| GET    | /api/v1/summaries/daily           | Generate summary of last 24h   |
| GET    | /api/v1/summaries/weekly          | Generate summary of last 7d    |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "X-API-Key: change-me" \
  -H "Content-Type: application/json" \
  -d '{"title": "Standup at 9am", "body": "Discuss sprint blockers", "source": "manual", "priority": "normal"}'

curl http://localhost:8000/api/v1/summaries/daily -H "X-API-Key: change-me"
```

## Deploying to Railway

1. Push this project to a GitHub repo.
2. In Railway: **New Project → Deploy from GitHub repo**.
3. Add environment variables in the Railway dashboard (from `.env.example`):
   - `API_KEY`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (optional, defaults to `gpt-4o-mini`)
   - `TIMEZONE`, `DAILY_SUMMARY_HOUR`, etc. (optional)
4. (Recommended) Attach a Railway Postgres plugin and let it inject
   `DATABASE_URL` automatically — otherwise the app falls back to a local
   SQLite file, which won't persist reliably across redeploys.
5. Railway will detect `railway.json` / `Procfile` and run:
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Notes / next steps

- The scheduler runs in-process. For a heavier production setup, split it
  into a separate Railway worker service instead of running it inside the
  web dyno.
- Swap the simple `X-API-Key` auth for OAuth/JWT if you ever expose this
  beyond yourself.
- `notification.source == "android"` is scaffolded so an Android
  notification-listener client can push directly into this API.
