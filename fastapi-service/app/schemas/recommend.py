from typing import List, Optional

from pydantic import BaseModel, Field


class GraduateProfile(BaseModel):
    major: Optional[str] = Field(None, description="التخصص الأكاديمي للخريج")
    target_role: Optional[str] = Field(None, description="الدور الوظيفي المستهدف")
    skills: List[str] = Field(default_factory=list, description="قائمة المهارات")
    experience_years: Optional[float] = Field(0.0, description="سنوات الخبرة")
    career_goal: Optional[str] = Field(None, description="الأهداف المهنية")
    interests: Optional[str] = Field(None, description="الاهتمامات")
    cv_analysis: Optional[str] = Field(None, description="تحليل السيرة الذاتية")
    languages: Optional[str] = Field(None, description="اللغات")
    preferred_meeting_type: Optional[str] = Field(None, description="نوع الاجتماع المفضل")
    university: Optional[str] = Field(None, description="الجامعة")


class MentorRecommendation(BaseModel):
    mentor_id: str
    name: str
    match_score: float
    matched_skills: List[str]
    bio: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendations: List[MentorRecommendation]
    total_found: int
    data_source: str = Field(
        default="database",
        description="مصدر بيانات المرشدين: database أو fallback",
    )
