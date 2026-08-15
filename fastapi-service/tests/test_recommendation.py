import pytest

from app.repositories.mentor_repository import MentorRecord
from app.services.recommendation import RecommendationService
from app.schemas.recommend import GraduateProfile


def test_score_uses_experience_years():
    mentor = MentorRecord(
        mentor_id="1",
        name="Senior Mentor",
        skills=["Python", "FastAPI"],
        bio="Backend expert",
        current_role="Software Engineer",
        university="Test University",
        years_experience=8,
    )
    score_with_experience, _ = RecommendationService._score_mentor(
        graduate_text="software engineer python fastapi",
        profile_skills=["Python", "FastAPI"],
        mentor=mentor,
        graduate_experience=1.0,
    )
    score_without_experience, _ = RecommendationService._score_mentor(
        graduate_text="software engineer python fastapi",
        profile_skills=["Python", "FastAPI"],
        mentor=mentor,
        graduate_experience=20.0,
    )
    assert score_with_experience > score_without_experience


def test_get_recommendations_returns_sorted_scores():
    profile = GraduateProfile(
        major="Computer Science",
        target_role="software engineer",
        skills=["Python", "FastAPI", "Docker"],
        experience_years=2,
    )
    recommendations, data_source = RecommendationService.get_recommendations(profile)
    assert data_source in {"database", "fallback"}
    assert recommendations[0].match_score >= recommendations[-1].match_score
