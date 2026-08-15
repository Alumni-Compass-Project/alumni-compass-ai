"""
ATS Scorer Service – production-quality analysis engine.
Scores: ATS keyword match, grammar, formatting, readability, action verbs.
"""
from __future__ import annotations

import re
import unicodedata
from typing import List

from ..schemas.cv import (
    CVAnalysisResponse, StructuredCV, ActionVerbAnalysis, GrammarIssue,
    ImprovementSuggestion,
)
from ..utils.ats_data import (
    ROLE_ALIASES, ROLE_KEYWORDS, COMMON_SKILLS, COMMON_ACTION_VERBS,
    ACTION_VERBS_BY_ROLE,
)
from ..utils.cv_improver import build_improved_cv, build_comparison, build_improvements


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value or "").strip().lower())


def _resolve_role(target_role: str) -> str:
    role = _normalize(target_role)
    if role in ROLE_ALIASES:
        return ROLE_ALIASES[role]
    for alias, canonical in ROLE_ALIASES.items():
        if alias in role or role in alias:
            return canonical
    return role


def _keyword_score(text: str, required: List[str]) -> tuple[List[str], List[str], float]:
    matched, missing = [], []
    for kw in required:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            matched.append(kw)
        else:
            missing.append(kw)
    score = (len(matched) / len(required) * 100) if required else 85.0
    return matched, missing, round(score, 1)


def _skill_score(text: str) -> List[str]:
    return [s for s in COMMON_SKILLS if re.search(rf"\b{re.escape(s)}\b", text)]


def _grammar_score(grammar_issues: List[GrammarIssue]) -> float:
    return round(max(50.0, 100.0 - len(grammar_issues) * 5.0), 1)


def _formatting_score(structured: StructuredCV) -> float:
    score = 50.0
    if structured.personal_information.email:
        score += 10
    if structured.summary:
        score += 8
    if structured.experience:
        score += 10
    if structured.education:
        score += 8
    if structured.skills:
        score += 8
    if structured.projects:
        score += 6
    return round(min(score, 100.0), 1)


def _readability_score(text: str) -> float:
    words = len(text.split())
    if words >= 300:
        return 95.0
    if words >= 180:
        return 85.0
    if words >= 100:
        return 70.0
    return 55.0


def _action_verb_analysis(structured: StructuredCV, role: str) -> ActionVerbAnalysis:
    role_verbs = ACTION_VERBS_BY_ROLE.get(role, COMMON_ACTION_VERBS)
    all_bullets = []
    for exp in structured.experience:
        all_bullets.extend(exp.bullets)

    if not all_bullets:
        return ActionVerbAnalysis(found=[], missing_count=len(role_verbs), score=0.0)

    found = []
    for verb in role_verbs:
        for bullet in all_bullets:
            if bullet.lower().startswith(verb):
                found.append(verb)
                break

    score = round((len(found) / max(len(role_verbs), 1)) * 100, 1)
    missing_count = len(role_verbs) - len(found)
    return ActionVerbAnalysis(found=found, missing_count=missing_count, score=score)


class ATSScorerService:
    @staticmethod
    def analyze_cv(
        text: str,
        target_role: str,
        grammar_issues: List[GrammarIssue] = None,
        structured: StructuredCV = None,
    ) -> CVAnalysisResponse:
        grammar_issues = grammar_issues or []
        norm_text      = _normalize(text)
        role           = _resolve_role(target_role)

        # -- Structured parse (if not pre-parsed)
        if structured is None:
            from ..utils.cv_parser import CVParser
            structured = CVParser.parse_to_structured(text)

        required_kws              = ROLE_KEYWORDS.get(role, ["communication", "teamwork", "leadership"])
        matched_kws, missing_kws, kw_score = _keyword_score(norm_text, required_kws)
        found_skills              = _skill_score(norm_text)

        ats_score     = round(min(kw_score + min(10, len(found_skills) * 1.5), 100.0), 1)
        grammar_sc    = _grammar_score(grammar_issues)
        formatting_sc = _formatting_score(structured)
        readability_sc = _readability_score(text)
        av_analysis   = _action_verb_analysis(structured, role)

        overall = round(
            ats_score      * 0.30 +
            kw_score       * 0.20 +
            grammar_sc     * 0.15 +
            readability_sc * 0.15 +
            formatting_sc  * 0.10 +
            av_analysis.score * 0.10,
            1
        )

        # -- Build improved CV
        improved_structured = build_improved_cv(structured, role, matched_kws, missing_kws)
        improved_ats = round(min(ats_score + 12.0, 100.0), 1)

        # -- Comparison
        comparison = build_comparison(structured, improved_structured)

        # -- Improvement suggestions
        improvements = build_improvements(
            original         = structured,
            missing_keywords = missing_kws,
            grammar_issues   = grammar_issues,
            action_verb_score = av_analysis.score,
            formatting_score  = formatting_sc,
            readability_score = readability_sc,
        )

        # -- Human-readable recommendations (backward compat)
        recommendations = [imp.suggestion for imp in improvements]

        return CVAnalysisResponse(
            overall_score         = overall,
            ats_score             = ats_score,
            improved_ats_score    = improved_ats,
            grammar_score         = grammar_sc,
            formatting_score      = formatting_sc,
            keyword_score         = kw_score,
            readability_score     = readability_sc,
            action_verb_score     = av_analysis.score,
            original_structured   = structured,
            improved_structured   = improved_structured,
            skills                = found_skills,
            missing_skills        = missing_kws,
            matched_keywords      = matched_kws,
            missing_keywords      = missing_kws,
            keyword_suggestions   = missing_kws[:5],
            action_verb_analysis  = av_analysis,
            grammar_issues        = grammar_issues,
            recommendations       = recommendations,
            improvements          = improvements,
            comparison            = comparison,
            improved_summary      = improved_structured.summary,
            experience_improvements = [
                f"Improved bullet: '{b}'" for exp in improved_structured.experience for b in exp.bullets[:1]
            ],
            optimized_text        = None,
        )
