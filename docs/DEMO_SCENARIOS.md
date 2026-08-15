# Demo Scenarios — Alumni Compass AI (S3)

Use these three scenarios during the graduation demo.

## Scenario 1 — Software graduate gets backend mentors

**Goal:** Show AI recommendations change based on profile.

**Request**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "major": "Computer Science",
    "target_role": "software engineer",
    "skills": ["Python", "FastAPI", "Docker", "SQL"],
    "experience_years": 1
  }'
```

**Expected**

- Top mentor has highest `match_score`
- `matched_skills` includes Python/FastAPI
- `data_source` is `database` when PostgreSQL is connected, otherwise `fallback`

**Demo line**

> "When the graduate profile focuses on backend skills, the platform ranks mentors with matching technical expertise."

---

## Scenario 2 — Frontend graduate gets different ranking

**Request**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "major": "Design",
    "target_role": "frontend developer",
    "skills": ["React", "JavaScript", "UI/UX", "Tailwind"],
    "experience_years": 0.5
  }'
```

**Expected**

- Top mentor differs from Scenario 1
- Higher score for mentors with React/UI skills

**Demo line**

> "Two graduates with different goals receive different mentor matches — the engine adapts to the profile."

---

## Scenario 3 — CV score improves live

**Step A — weak CV**

```bash
curl -F "target_role=software engineer" \
  -F "text_content=Graduate looking for first job." \
  http://127.0.0.1:8000/api/v1/cv/analyze
```

**Step B — improved CV**

```bash
curl -F "target_role=software engineer" \
  -F "text_content=Software engineer with Python, FastAPI, Docker, SQL, Git, agile testing, REST API, and microservices experience." \
  http://127.0.0.1:8000/api/v1/cv/analyze
```

**Expected**

- Step A: lower `ats_score`, more `missing_keywords`
- Step B: score rises toward 70+, fewer missing keywords

**Demo line**

> "As the graduate adds role-specific keywords, the ATS score increases in real time."

---

## WebRTC demo

1. Start signaling server: `cd signaling-server && npm start`
2. Open two browser tabs with the same `roomId`
3. Show video + audio between both tabs
4. Click **صوت فقط** to disable video while keeping audio

---

## Pre-demo checklist

- [ ] PostgreSQL running and seeded by S1
- [ ] `DATABASE_URL` set in FastAPI `.env`
- [ ] `/health` returns `"db_connected": true`
- [ ] Signaling server running
- [ ] Run all 3 curl scenarios once before presentation
