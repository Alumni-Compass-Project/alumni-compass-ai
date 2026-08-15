from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ── Structured CV Sections ──────────────────────────────────────────────────

class PersonalInformation(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class ExperienceEntry(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = []


class EducationEntry(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None


class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []
    url: Optional[str] = None


class CertificationEntry(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None


class StructuredCV(BaseModel):
    personal_information: PersonalInformation = Field(default_factory=PersonalInformation)
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    projects: List[ProjectEntry] = []
    certifications: List[CertificationEntry] = []
    languages: List[str] = []
    raw_sections: Dict[str, str] = {}


# ── Analysis Models ─────────────────────────────────────────────────────────

class GrammarIssue(BaseModel):
    message: str
    context: Optional[str] = None
    suggestions: List[str] = []
    offset: Optional[int] = None
    length: Optional[int] = None
    rule_id: Optional[str] = None


class ActionVerbAnalysis(BaseModel):
    found: List[str] = []
    missing_count: int = 0
    score: float = 0.0


class KeywordAnalysis(BaseModel):
    matched: List[str] = []
    missing: List[str] = []
    density_score: float = 0.0


class ImprovementSuggestion(BaseModel):
    category: str
    priority: str  # high | medium | low
    issue: str
    suggestion: str


class ComparisonChange(BaseModel):
    section: str
    change_type: str  # added | modified | removed
    original: Optional[str] = None
    improved: Optional[str] = None


# ── Response Models ─────────────────────────────────────────────────────────

class CVAnalysisRequest(BaseModel):
    text: Optional[str] = None
    target_role: str


class CVAnalysisResponse(BaseModel):
    # Score Breakdown
    overall_score: float = 0.0
    ats_score: float = 0.0
    improved_ats_score: float = 0.0
    grammar_score: float = 0.0
    formatting_score: float = 0.0
    keyword_score: float = 0.0
    readability_score: float = 0.0
    action_verb_score: float = 0.0

    # Parsed Structure
    original_structured: StructuredCV = Field(default_factory=StructuredCV)
    improved_structured: StructuredCV = Field(default_factory=StructuredCV)

    # Keywords & Skills
    skills: List[str] = []
    missing_skills: List[str] = []
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    keyword_suggestions: List[str] = []

    # Action Verbs
    action_verb_analysis: ActionVerbAnalysis = Field(default_factory=ActionVerbAnalysis)

    # Grammar
    grammar_issues: List[GrammarIssue] = []

    # Improvements
    recommendations: List[str] = []
    improvements: List[ImprovementSuggestion] = []

    # Comparison
    comparison: List[ComparisonChange] = []

    # Legacy fields for backward-compat
    improved_summary: Optional[str] = None
    experience_improvements: List[str] = []
    optimized_text: Optional[str] = None
