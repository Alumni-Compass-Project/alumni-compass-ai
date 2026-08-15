from typing import List
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAVE_SKLEARN = True
except Exception:
    _HAVE_SKLEARN = False

from ..repositories.mentor_repository import MentorRecord, MentorRepository
from ..schemas.recommend import GraduateProfile, MentorRecommendation


class RecommendationService:
    @staticmethod
    def get_recommendations(profile: GraduateProfile) -> tuple[List[MentorRecommendation], str]:
        mentors, data_source = MentorRepository.fetch_approved_mentors()
        profile_skills = [skill.strip() for skill in profile.skills if skill.strip()]
        graduate_experience = float(profile.experience_years or 0.0)

        user_text_parts = []
        if profile.target_role:
            user_text_parts.append(profile.target_role)
        if profile.major:
            user_text_parts.append(profile.major)
        if profile.career_goal:
            user_text_parts.append(profile.career_goal)
        if profile.interests:
            user_text_parts.append(profile.interests)
        if profile.cv_analysis:
            user_text_parts.append(profile.cv_analysis)
        if profile.university:
            user_text_parts.append(profile.university)
        if profile.languages:
            user_text_parts.append(profile.languages)
        user_text_parts.extend(profile_skills)
        graduate_text = " ".join(user_text_parts)

        recommendations: List[MentorRecommendation] = []
        raw_scores: List[float] = []

        for mentor in mentors:
            score, matched_skills = RecommendationService._score_mentor(
                graduate_text=graduate_text,
                profile_skills=profile_skills,
                mentor=mentor,
                graduate_experience=graduate_experience,
                profile=profile,
            )
            raw_scores.append(score)
            recommendations.append(
                MentorRecommendation(
                    mentor_id=mentor.mentor_id,
                    name=mentor.name,
                    match_score=score,
                    matched_skills=matched_skills,
                    bio=mentor.bio or None,
                )
            )

        # ── Post-processing: min-max normalization into [72%, 98%] ──────────
        # Normalize scores so the best mentor is near 95-98% and others are
        # spread meaningfully in the 72-98 range (min/max calibration).
        if raw_scores:
            min_raw = min(raw_scores)
            max_raw = max(raw_scores)
            score_range = max_raw - min_raw if max_raw != min_raw else 1.0
            TARGET_MIN = 72.0
            TARGET_MAX = 98.0
            for rec in recommendations:
                normalized = TARGET_MIN + (rec.match_score - min_raw) / score_range * (TARGET_MAX - TARGET_MIN)
                rec.match_score = round(min(normalized, 100.0), 1)

        recommendations.sort(key=lambda item: item.match_score, reverse=True)
        return recommendations, data_source

    @staticmethod
    def _score_mentor(
        graduate_text: str,
        profile_skills: List[str],
        mentor: MentorRecord,
        graduate_experience: float,
        profile: GraduateProfile,
    ) -> tuple[float, List[str]]:
        mentor_text_parts = [
            mentor.name,
            mentor.current_role,
            mentor.university,
            " ".join(mentor.skills),
            mentor.bio,
            " ".join(mentor.availability),
        ]
        mentor_text = " ".join(part for part in mentor_text_parts if part)

        # ── 1. Semantic similarity (TF-IDF cosine) — up to 30 pts ────────────
        # Cosine on short/sparse texts rarely exceeds 0.4, so we remap
        # the realistic range [0, 0.5] → [0, 1] before scaling to 30 pts.
        if graduate_text.strip() and mentor_text.strip():
            if _HAVE_SKLEARN:
                try:
                    vectorizer = TfidfVectorizer(min_df=1, stop_words=None)
                    vectors = vectorizer.fit_transform([graduate_text, mentor_text]).toarray()
                    raw_cos = float(cosine_similarity(vectors)[0][1]) if vectors.shape[0] > 1 else 0.0
                except Exception:
                    raw_cos = RecommendationService._jaccard(graduate_text, mentor_text)
            else:
                raw_cos = RecommendationService._jaccard(graduate_text, mentor_text)
        else:
            raw_cos = 0.0

        scaled_cos = min(raw_cos / 0.5, 1.0)   # remap realistic range to [0,1]
        text_component = scaled_cos * 30.0

        # ── 2. Skill overlap (fuzzy bidirectional) — up to 45 pts ─────────────
        matched_skills: List[str] = []
        for skill in profile_skills:
            skill_lower = skill.lower()
            for ms in mentor.skills:
                ms_lower = ms.lower()
                if (
                    skill_lower == ms_lower
                    or skill_lower in ms_lower
                    or ms_lower in skill_lower
                    or RecommendationService._token_overlap(skill_lower, ms_lower) >= 0.5
                ):
                    matched_skills.append(skill)
                    break
        matched_skills = list(dict.fromkeys(matched_skills))  # deduplicate, preserve order

        skill_ratio = len(matched_skills) / max(len(profile_skills), 1)
        any_match_bonus = 5.0 if matched_skills else 0.0   # reward any overlap
        skill_component = skill_ratio * 40.0 + any_match_bonus

        # ── 3. Career/specialization alignment — up to 8 pts ─────────────────
        mentor_spec_text = ((mentor.current_role or "") + " " + (mentor.bio or "")).lower()
        student_goal_tokens = set(
            re.findall(r"\w+", (profile.career_goal or profile.target_role or "").lower())
        ) - {"the", "a", "an", "and", "or", "to", "of", "in", "for", "be", "my"}
        spec_overlap = len(student_goal_tokens & set(re.findall(r"\w+", mentor_spec_text)))

        if spec_overlap >= 2:
            specialization_bonus = 8.0
        elif spec_overlap == 1:
            specialization_bonus = 4.0
        elif profile.target_role and (mentor.current_role or mentor.bio):
            target_lower = profile.target_role.lower()
            if (target_lower in (mentor.current_role or "").lower()
                    or target_lower in (mentor.bio or "").lower()):
                specialization_bonus = 5.0
            else:
                specialization_bonus = 0.0
        else:
            specialization_bonus = 0.0

        # ── 4. Experience bonus — up to 10 pts ───────────────────────────────
        mentor_experience = float(mentor.years_experience or 0)
        experience_bonus = 0.0
        if mentor_experience > 0:
            experience_bonus += 3.0
        if mentor_experience >= graduate_experience + 2:
            experience_bonus += 4.0
        if mentor_experience >= graduate_experience + 5:
            experience_bonus += 3.0

        # ── 5. University match — up to 5 pts ────────────────────────────────
        university_bonus = 0.0
        if profile.university and mentor.university:
            if profile.university.lower() == mentor.university.lower():
                university_bonus = 5.0

        # ── 6. Meeting type match — up to 3 pts ──────────────────────────────
        meeting_type_bonus = 0.0
        if profile.preferred_meeting_type and mentor.bio:
            if profile.preferred_meeting_type.lower() in mentor.bio.lower():
                meeting_type_bonus = 3.0

        # ── 7. Availability bonus — 4 pts ─────────────────────────────────────
        availability_bonus = 4.0 if mentor.availability else 0.0

        # ── 8. Guaranteed base — ensures no mentor starts at zero ─────────────
        base = 35.0

        score = round(
            base
            + text_component
            + skill_component
            + experience_bonus
            + specialization_bonus
            + university_bonus
            + meeting_type_bonus
            + availability_bonus,
            2,
        )
        return score, matched_skills

    @staticmethod
    def _jaccard(a: str, b: str) -> float:
        """Jaccard similarity on word tokens (sklearn fallback)."""
        a_tokens = set(re.findall(r"\w+", (a or "").lower()))
        b_tokens = set(re.findall(r"\w+", (b or "").lower()))
        if not a_tokens and not b_tokens:
            return 0.0
        return float(len(a_tokens & b_tokens)) / max(len(a_tokens | b_tokens), 1)

    @staticmethod
    def _token_overlap(a: str, b: str) -> float:
        """Word-level overlap ratio (symmetric min-coverage)."""
        a_toks = set(a.split())
        b_toks = set(b.split())
        if not a_toks or not b_toks:
            return 0.0
        return float(len(a_toks & b_toks)) / max(min(len(a_toks), len(b_toks)), 1)
