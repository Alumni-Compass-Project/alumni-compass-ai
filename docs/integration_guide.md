# Laravel Integration Guide (S1 ↔ S3)

This guide explains how the Laravel backend should call the FastAPI AI service.

## Environment variable

Add to Laravel `.env`:

```dotenv
FASTAPI_AI_SERVICE_URL=http://localhost:8000
```

In production:

```dotenv
FASTAPI_AI_SERVICE_URL=https://your-fastapi-service.up.railway.app
```

## 1. Mentor recommendations

### Endpoint

`POST {FASTAPI_AI_SERVICE_URL}/api/v1/recommend`

### Laravel example

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RecommendationService
{
    public function getMentorRecommendations(array $graduateProfile): array
    {
        $baseUrl = rtrim(config('services.ai.url', env('FASTAPI_AI_SERVICE_URL')), '/');

        $response = Http::timeout(10)->post("{$baseUrl}/api/v1/recommend", [
            'major' => $graduateProfile['major'] ?? null,
            'target_role' => $graduateProfile['target_role'] ?? null,
            'skills' => $graduateProfile['skills'] ?? [],
            'experience_years' => $graduateProfile['experience_years'] ?? 0,
        ]);

        if ($response->failed()) {
            return ['error' => $response->json(), 'status' => $response->status()];
        }

        return $response->json();
    }
}
```

### Expected response fields

- `recommendations[].mentor_id`
- `recommendations[].name`
- `recommendations[].match_score`
- `recommendations[].matched_skills`
- `recommendations[].bio`
- `data_source` (`database` or `fallback`)

Store results in Redis/cache and log the request in `ai_requests`.

---

## 2. CV analysis

### Endpoint

`POST {FASTAPI_AI_SERVICE_URL}/api/v1/cv/analyze`

### Laravel example — file upload

```php
public function analyzeCVFromFile(UploadedFile $cvFile, string $targetRole): array
{
    $baseUrl = rtrim(env('FASTAPI_AI_SERVICE_URL'), '/');

    $response = Http::timeout(20)
        ->attach('file', file_get_contents($cvFile->getRealPath()), $cvFile->getClientOriginalName())
        ->post("{$baseUrl}/api/v1/cv/analyze", [
            'target_role' => $targetRole,
        ]);

    return $response->successful()
        ? $response->json()
        : ['error' => $response->json(), 'status' => $response->status()];
}
```

### Laravel example — text content

```php
public function analyzeCVFromText(string $cvText, string $targetRole): array
{
    $baseUrl = rtrim(env('FASTAPI_AI_SERVICE_URL'), '/');

    $response = Http::timeout(20)->asMultipart()->post("{$baseUrl}/api/v1/cv/analyze", [
        ['name' => 'target_role', 'contents' => $targetRole],
        ['name' => 'text_content', 'contents' => $cvText],
    ]);

    return $response->successful()
        ? $response->json()
        : ['error' => $response->json(), 'status' => $response->status()];
}
```

### Response shape for S5 CV Builder UI

```json
{
  "ats_score": 72.5,
  "matched_keywords": ["python", "docker"],
  "missing_keywords": ["agile"],
  "recommendations": ["..."],
  "grammar_issues": []
}
```

---

## 3. Database note

FastAPI reads mentor data directly from the shared PostgreSQL database created by Laravel.

Required mentor state:

- `mentor_profiles.approval_status = approved`
- `mentor_profiles.accepting_new_mentees = true`

No separate `mentors` table is needed.

---

## 4. WebRTC integration

S3 provides:

- `webrtc-component/VideoRoom.jsx`
- `signaling-server/` (Socket.io)

S2 should set:

```env
REACT_APP_SIGNALING_URL=https://your-signaling-server.up.railway.app
```

Laravel booking/session APIs should pass `roomId`, `userId`, and role to the session page.

---

## 5. Error handling checklist

- Timeout after 10s for recommend, 20s for CV analyze
- Log failures in `ai_requests`
- Show user-friendly Arabic error in frontend
- Fall back gracefully if `data_source = fallback`
