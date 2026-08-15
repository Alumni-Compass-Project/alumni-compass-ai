# Alumni Compass AI Service (S3)

FastAPI service for mentor recommendations, CV ATS analysis, and grammar checking.

## Setup

```bash
cd fastapi-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with the same PostgreSQL database used by Laravel (S1):

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/alumni_compass_db
```

## Run locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health + DB status |
| POST | `/api/v1/recommend` | Mentor recommendations |
| POST | `/api/v1/cv/analyze` | CV ATS analysis |
| POST | `/recommend` | Legacy alias |
| POST | `/cv/analyze` | Legacy alias |

## Database integration

Recommendations read approved mentors from Laravel tables:

- `users`
- `profiles`
- `mentor_profiles`
- `mentor_skill`
- `skills`

If PostgreSQL is unavailable, the service falls back to demo mentor data and returns `"data_source": "fallback"`.

## Tests

```bash
pytest tests/ -v
```

## Deploy on Railway

1. Create a Railway service from this folder.
2. Set `DATABASE_URL` to the same PostgreSQL instance as Laravel.
3. Railway uses `Dockerfile` and checks `/health`.

## Example requests

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d "{\"major\":\"Computer Science\",\"target_role\":\"software engineer\",\"skills\":[\"Python\",\"FastAPI\",\"Docker\"],\"experience_years\":1.5}"

curl -F "target_role=software engineer" \
  -F "text_content=Experienced software engineer with Python, FastAPI, Docker." \
  http://127.0.0.1:8000/api/v1/cv/analyze
```

See also:

- `../docs/API_contract.md`
- `../docs/integration_guide.md`
- `../docs/DEMO_SCENARIOS.md`
