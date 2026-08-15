from dataclasses import dataclass
from typing import List

try:
    from sqlalchemy import text as sa_text
except Exception:
    sa_text = None

try:
    from ..db import check_connection, engine
except Exception:
    # db or sqlalchemy not available in this environment; defer checks to runtime
    check_connection = None
    engine = None

APPROVED_MENTORS_QUERY_STR = """
    SELECT
        u.id::text AS mentor_id,
        u.name,
        COALESCE(p.bio, '') AS bio,
        COALESCE(p.current_role, p.headline, '') AS current_role,
        COALESCE(p.university, '') AS university,
        COALESCE(mp.years_experience, 0) AS years_experience,
        COALESCE(
            array_agg(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL),
            ARRAY[]::varchar[]
        ) AS skills,
        COALESCE(
            array_agg(DISTINCT ma.day_of_week::text || ' ' || ma.start_time::text || '-' || ma.end_time::text) FILTER (WHERE ma.day_of_week IS NOT NULL),
            ARRAY[]::text[]
        ) AS availability
    FROM users u
    INNER JOIN mentor_profiles mp ON mp.user_id = u.id
    LEFT JOIN profiles p ON p.user_id = u.id
    LEFT JOIN mentor_skill ms ON ms.mentor_user_id = u.id
    LEFT JOIN skills s ON s.id = ms.skill_id AND s.is_active = true
    LEFT JOIN mentor_availabilities ma ON ma.mentor_user_id = u.id AND ma.is_active = true
    WHERE mp.approval_status = 'approved'
      AND mp.accepting_new_mentees = true
      AND u.is_active = true
      AND p.is_public = true
      AND p.completion_score >= 100
    GROUP BY u.id, u.name, p.bio, p.current_role, p.headline, p.university, mp.years_experience
    ORDER BY u.name
"""

FALLBACK_MENTORS = [
    {
        "mentor_id": "M1",
        "name": "أحمد علي",
        "skills": ["Python", "FastAPI", "Machine Learning"],
        "bio": "خبير في الذكاء الاصطناعي",
        "current_role": "Senior Software Engineer",
        "university": "جامعة الملك سعود",
        "years_experience": 8,
    },
    {
        "mentor_id": "M2",
        "name": "سارة محمود",
        "skills": ["React", "UI/UX", "JavaScript"],
        "bio": "مصممة واجهات أمامية محترفة",
        "current_role": "Frontend Lead",
        "university": "جامعة الملك عبدالعزيز",
        "years_experience": 6,
    },
    {
        "mentor_id": "M3",
        "name": "خالد حسن",
        "skills": ["DevOps", "Docker", "AWS"],
        "bio": "مهندس سحابي",
        "current_role": "DevOps Engineer",
        "university": "جامعة الأميرة نورة",
        "years_experience": 7,
    },
    {
        "mentor_id": "M4",
        "name": "ليلى يوسف",
        "skills": ["Data Analysis", "SQL", "Tableau"],
        "bio": "محللة بيانات بخبرة 10 سنوات",
        "current_role": "Data Analyst",
        "university": "جامعة الملك فهد",
        "years_experience": 10,
    },
]


@dataclass
class MentorRecord:
    mentor_id: str
    name: str
    skills: List[str]
    bio: str
    current_role: str
    university: str
    years_experience: int
    availability: List[str]


class MentorRepository:
    @staticmethod
    def fetch_approved_mentors() -> tuple[List[MentorRecord], str]:
        # Import DB helpers lazily to avoid import-time failures when SQLAlchemy
        # or DATABASE_URL are not available in the execution environment.
        try:
            from ..db import check_connection as _check_connection, engine as _engine
        except Exception:
            return MentorRepository._from_fallback(), "fallback"

        if not _check_connection() or _engine is None or sa_text is None:
            return MentorRepository._from_fallback(), "fallback"

        try:
            with _engine.connect() as conn:
                query = sa_text(APPROVED_MENTORS_QUERY_STR)
                rows = conn.execute(query).mappings().all()
        except Exception as exc:
            print(f"MentorRepository: DB query failed, using fallback. Error: {exc}")
            return MentorRepository._from_fallback(), "fallback"

        if not rows:
            return MentorRepository._from_fallback(), "fallback"

        mentors = [
            MentorRecord(
                mentor_id=row["mentor_id"],
                name=row["name"],
                skills=list(row["skills"] or []),
                bio=row["bio"] or "",
                current_role=row["current_role"] or "",
                university=row["university"] or "",
                years_experience=int(row["years_experience"] or 0),
                availability=list(row["availability"] or []),
            )
            for row in rows
        ]
        return mentors, "database"

    @staticmethod
    def _from_fallback() -> List[MentorRecord]:
        return [
            MentorRecord(
                mentor_id=item["mentor_id"],
                name=item["name"],
                skills=item["skills"],
                bio=item["bio"],
                current_role=item["current_role"],
                university=item["university"],
                years_experience=item["years_experience"],
                availability=["1 09:00:00-17:00:00", "3 09:00:00-17:00:00"],
            )
            for item in FALLBACK_MENTORS
        ]
