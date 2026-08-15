from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "db_connected" in body
    assert body["version"] == "1.0.0"


def test_recommend_endpoint_v1_with_skills():
    payload = {
        "major": "Computer Science",
        "target_role": "software engineer",
        "skills": ["Python", "FastAPI", "Docker"],
        "experience_years": 1.5,
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total_found"] >= 1
    assert isinstance(body["recommendations"], list)
    assert body["recommendations"][0]["name"]
    assert "match_score" in body["recommendations"][0]
    assert body["data_source"] in {"database", "fallback"}


def test_recommend_legacy_route_alias():
    payload = {
        "major": "Computer Science",
        "target_role": "software engineer",
        "skills": ["Python"],
        "experience_years": 0,
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200


def test_recommend_requires_skills():
    response = client.post("/api/v1/recommend", json={"skills": []})
    assert response.status_code == 400


def test_recommendations_differ_by_profile():
    software_payload = {
        "major": "Computer Science",
        "target_role": "software engineer",
        "skills": ["Python", "FastAPI", "Docker"],
        "experience_years": 1,
    }
    design_payload = {
        "major": "Design",
        "target_role": "frontend developer",
        "skills": ["React", "UI/UX", "JavaScript"],
        "experience_years": 1,
    }
    software = client.post("/api/v1/recommend", json=software_payload).json()
    design = client.post("/api/v1/recommend", json=design_payload).json()
    assert software["recommendations"][0]["mentor_id"] != design["recommendations"][0]["mentor_id"]


def test_cv_analyze_with_text_content_v1():
    data = {
        "target_role": "software engineer",
        "text_content": (
            "Experienced software engineer with Python, FastAPI, Docker, SQL, "
            "and agile development."
        ),
    }
    response = client.post("/api/v1/cv/analyze", data=data)
    assert response.status_code == 200
    body = response.json()
    assert body["ats_score"] >= 40
    assert "missing_keywords" in body
    assert isinstance(body["recommendations"], list)


def test_cv_analyze_arabic_target_role():
    data = {
        "target_role": "مهندس برمجيات",
        "text_content": "Python FastAPI Docker SQL agile testing git api",
    }
    response = client.post("/api/v1/cv/analyze", data=data)
    assert response.status_code == 200
    assert response.json()["ats_score"] > 0


def test_cv_analyze_requires_input():
    response = client.post("/api/v1/cv/analyze", data={"target_role": "software engineer"})
    assert response.status_code == 400
