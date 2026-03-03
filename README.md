# Python URL Shortener

A minimal URL shortener API built with FastAPI and SQLite.

## Live Demo

- Demo URL: `https://your-live-demo-url.onrender.com/`
- API docs: `https://your-live-demo-url.onrender.com/docs`

Replace `your-live-demo-url` after deployment.

## Showcase Pitch

Python URL Shortener is a lightweight, production-style MVP built with FastAPI. It creates short links, supports custom aliases, and redirects reliably through a clean web interface. The app is intentionally simple to demonstrate end-to-end backend + frontend integration, API-first design, and fast deployment on free hosting.

## Demo Ready Deployment (GitHub + Render)

This project is ready for a shareable demo:

1. Push this folder to a GitHub repository.
2. Create a free Render account and click **New +** -> **Blueprint**.
3. Connect your GitHub repo and select this project.
4. Render will detect `render.yaml` and deploy automatically.
5. Open your live URL, for example: `https://your-app-name.onrender.com/`

Notes:
- The demo uses SQLite with `DB_PATH=/tmp/urls.db` on Render.
- Free-tier instances can sleep after inactivity.
- Data may reset when the instance restarts (fine for demo concept).

## Features

- Create short links for long URLs
- Optional custom alias support
- Redirect from short code to original URL
- Lightweight SQLite persistence

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest -q
```

Server starts at `http://127.0.0.1:8000`.

Open `http://127.0.0.1:8000/` to use the web page UI.

## API Endpoints

- `GET /health` - health check
- `POST /shorten` - create short URL
- `GET /{short_code}` - redirect to original URL

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.python.org", "custom_alias":"python"}'
```

### Example Response

```json
{
  "original_url": "https://www.python.org/",
  "short_code": "python",
  "short_url": "http://127.0.0.1:8000/python"
}
```
