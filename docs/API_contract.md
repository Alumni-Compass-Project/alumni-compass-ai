# API Contract — Alumni Compass AI Service

Base URL (local): `http://localhost:8000`

Production: `https://<your-railway-fastapi-domain>`

All versioned endpoints are under `/api/v1`.

Legacy aliases without the prefix remain available for backward compatibility.

---

## Health

### `GET /health`

**Response**

```json
{
  "status": "healthy",
  "service": "Alumni Compass AI",
  "db_connected": true,
  "version": "1.0.0"
}
```

---

## 1. Mentor Recommendations

### `POST /api/v1/recommend`

Returns ranked mentors based on graduate profile using weighted cosine similarity + skill overlap + experience bonus.

#### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `major` | string | no | Academic major |
| `target_role` | string | no | Target job role |
| `skills` | string[] | yes | At least one skill |
| `experience_years` | number | no | Graduate experience in years |

```json
{
  "major": "Computer Science",
  "target_role": "software engineer",
  "skills": ["Python", "FastAPI", "Docker"],
  "experience_years": 1.5
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `recommendations` | array | Ranked mentor list |
| `total_found` | integer | Number of mentors scored |
| `data_source` | string | `database` or `fallback` |

**MentorRecommendation**

| Field | Type | Description |
|-------|------|-------------|
| `mentor_id` | string | Mentor user id |
| `name` | string | Mentor name |
| `match_score` | float | Score from 0 to 100 |
| `matched_skills` | string[] | Shared skills |
| `bio` | string | Mentor bio |

```json
{
  "recommendations": [
    {
      "mentor_id": "12",
      "name": "Ahmed Ali",
      "match_score": 85.75,
      "matched_skills": ["Python", "FastAPI"],
      "bio": "AI expert"
    }
  ],
  "total_found": 10,
  "data_source": "database"
}
```

#### Data source

When PostgreSQL is connected, mentors are loaded from Laravel tables:

- `users`
- `profiles`
- `mentor_profiles` (`approval_status = approved`)
- `mentor_skill`
- `skills`

---

## 2. CV ATS Analysis

### `POST /api/v1/cv/analyze`

Content-Type: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_role` | string | yes | Target role (English or Arabic) |
| `file` | file | no | PDF or DOCX |
| `text_content` | string | no | Raw CV text |

At least one of `file` or `text_content` is required.

#### Response

| Field | Type | Description |
|-------|------|-------------|
| `ats_score` | float | Score 0–100 |
| `matched_keywords` | string[] | Found role keywords |
| `missing_keywords` | string[] | Missing role keywords |
| `recommendations` | string[] | Improvement suggestions (Arabic) |
| `grammar_issues` | object[] | LanguageTool results |

```json
{
  "ats_score": 75.0,
  "matched_keywords": ["python", "docker", "sql"],
  "missing_keywords": ["agile", "microservices"],
  "recommendations": [
    "أضف هذه المهارات أو الكلمات المفتاحية في السيرة الذاتية: agile, microservices."
  ],
  "grammar_issues": []
}
```

#### Supported target roles

- `software engineer` / `مهندس برمجيات`
- `frontend developer` / `مطور واجهات`
- `data scientist` / `عالم بيانات`

---

## Legacy aliases

| Versioned | Legacy alias |
|-----------|--------------|
| `POST /api/v1/recommend` | `POST /recommend` |
| `POST /api/v1/cv/analyze` | `POST /cv/analyze` |
