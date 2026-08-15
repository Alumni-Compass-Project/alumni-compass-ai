"""
CV Improvement Engine.
Generates a structurally improved CV (StructuredCV) from the original
parsed CV + analysis results. No paid APIs – pure rule-based + templates.
"""
from __future__ import annotations

import re
from typing import List

from ..schemas.cv import (
    StructuredCV, ExperienceEntry, ImprovementSuggestion, ComparisonChange,
)
from .ats_data import ROLE_KEYWORDS, ACTION_VERBS_BY_ROLE, COMMON_ACTION_VERBS

_WEAK_VERBS = {"responsible for", "worked on", "helped with", "involved in", "did", "made"}
_STRONG_STARTERS = {
    "software engineer":  "Engineered",
    "frontend developer": "Developed",
    "data scientist":     "Analyzed",
    "default":            "Delivered",
}


def _capitalize_first(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _improve_bullet(bullet: str, role: str) -> str:
    """Rewrite weak bullets to start with strong action verbs."""
    lower = bullet.lower()
    for weak in _WEAK_VERBS:
        if lower.startswith(weak):
            strong = _STRONG_STARTERS.get(role, _STRONG_STARTERS["default"])
            remainder = bullet[len(weak):].lstrip()
            return f"{strong} {remainder}"
    # Ensure first word is capitalized
    return _capitalize_first(bullet)


def _generate_improved_summary(original_summary: str | None, role: str, skills: List[str]) -> str:
    top_skills = ", ".join(skills[:5]) if skills else "software development"
    if original_summary and len(original_summary) > 50:
        # Prepend a strong opening sentence
        return (
            f"Results-driven {role.title()} with demonstrated expertise in {top_skills}. "
            + original_summary.strip()
        )
    return (
        f"Results-driven {role.title()} with expertise in {top_skills}. "
        f"Proven track record of delivering high-quality solutions in agile environments, "
        f"applying clean code principles and industry best practices to drive measurable impact."
    )


def build_improved_cv(
    original: StructuredCV,
    role: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
) -> StructuredCV:
    import copy
    improved = copy.deepcopy(original)

    # 1. Enhance summary
    improved.summary = _generate_improved_summary(original.summary, role, original.skills)

    # 2. Inject missing keywords into skills
    existing_lower = {s.lower() for s in original.skills}
    for kw in missing_keywords[:8]:
        if kw.lower() not in existing_lower:
            improved.skills.append(kw)
            existing_lower.add(kw.lower())

    # 3. Improve experience bullets
    improved_exp: List[ExperienceEntry] = []
    for exp in original.experience:
        new_exp = copy.deepcopy(exp)
        new_exp.bullets = [_improve_bullet(b, role) for b in exp.bullets]
        if not new_exp.bullets and not exp.bullets:
            # add generic impactful bullet if none exist
            new_exp.bullets = [
                f"Contributed to full-cycle development of production-grade {role} solutions."
            ]
        improved_exp.append(new_exp)
    improved.experience = improved_exp

    return improved


def build_comparison(original: StructuredCV, improved: StructuredCV) -> List[ComparisonChange]:
    changes: List[ComparisonChange] = []

    # Summary
    if original.summary != improved.summary:
        changes.append(ComparisonChange(
            section     = "Summary",
            change_type = "modified" if original.summary else "added",
            original    = original.summary,
            improved    = improved.summary,
        ))

    # Skills
    orig_skills = set(original.skills)
    imp_skills  = set(improved.skills)
    added_skills = imp_skills - orig_skills
    if added_skills:
        changes.append(ComparisonChange(
            section     = "Skills",
            change_type = "added",
            original    = None,
            improved    = ", ".join(sorted(added_skills)),
        ))

    # Experience bullets
    for i, (orig_exp, imp_exp) in enumerate(zip(original.experience, improved.experience)):
        orig_bullets = set(orig_exp.bullets)
        imp_bullets  = set(imp_exp.bullets)
        for b in imp_bullets - orig_bullets:
            changes.append(ComparisonChange(
                section     = f"Experience – {orig_exp.job_title or f'Entry {i+1}'}",
                change_type = "modified",
                original    = next(iter(orig_bullets), None),
                improved    = b,
            ))

    return changes


def build_improvements(
    original: StructuredCV,
    missing_keywords: List[str],
    grammar_issues: list,
    action_verb_score: float,
    formatting_score: float,
    readability_score: float,
) -> List[ImprovementSuggestion]:
    suggestions: List[ImprovementSuggestion] = []

    if missing_keywords:
        suggestions.append(ImprovementSuggestion(
            category   = "Keywords & ATS",
            priority   = "high",
            issue      = f"Missing {len(missing_keywords)} target keywords",
            suggestion = f"Add these ATS-critical keywords: {', '.join(missing_keywords[:6])}.",
        ))

    if grammar_issues:
        suggestions.append(ImprovementSuggestion(
            category   = "Grammar & Writing",
            priority   = "high" if len(grammar_issues) > 5 else "medium",
            issue      = f"{len(grammar_issues)} grammar/style issue(s) detected",
            suggestion = "Review and correct grammar issues to improve professionalism.",
        ))

    if action_verb_score < 70:
        suggestions.append(ImprovementSuggestion(
            category   = "Action Verbs",
            priority   = "medium",
            issue      = "Experience bullets lack strong action verbs",
            suggestion = "Begin each bullet with a strong action verb (e.g., Architected, Engineered, Delivered, Optimized).",
        ))

    if formatting_score < 75:
        suggestions.append(ImprovementSuggestion(
            category   = "Formatting",
            priority   = "medium",
            issue      = "Missing or incomplete CV sections",
            suggestion = "Ensure all sections are clearly labeled: Summary, Experience, Education, Skills, Projects.",
        ))

    if readability_score < 80:
        suggestions.append(ImprovementSuggestion(
            category   = "Readability",
            priority   = "low",
            issue      = "CV content may be too short or dense",
            suggestion = "Expand experience bullets with quantifiable achievements (e.g., 'Reduced load time by 40%').",
        ))

    if not original.personal_information.email:
        suggestions.append(ImprovementSuggestion(
            category   = "Contact Information",
            priority   = "high",
            issue      = "Email address not detected",
            suggestion = "Ensure your email address is clearly visible at the top of your CV.",
        ))

    return suggestions
