"""
ATS keyword and action-verb data.
Centralised so scorer and improver share the same source of truth.
"""
from __future__ import annotations

from typing import Dict, List

ROLE_ALIASES: Dict[str, str] = {
    "software engineer": "software engineer",
    "مهندس برمجيات": "software engineer",
    "backend developer": "software engineer",
    "backend engineer": "software engineer",
    "full stack developer": "software engineer",
    "fullstack developer": "software engineer",
    "frontend developer": "frontend developer",
    "مطور واجهات": "frontend developer",
    "مطور frontend": "frontend developer",
    "ui developer": "frontend developer",
    "data scientist": "data scientist",
    "عالم بيانات": "data scientist",
    "محلل بيانات": "data scientist",
    "ml engineer": "ml engineer",
    "machine learning engineer": "ml engineer",
    "devops engineer": "devops engineer",
    "site reliability engineer": "devops engineer",
    "product manager": "product manager",
    "project manager": "project manager",
}

ROLE_KEYWORDS: Dict[str, List[str]] = {
    "software engineer": [
        "python", "java", "api", "git", "docker", "sql", "testing", "agile",
        "fastapi", "microservices", "rest", "backend", "ci/cd", "linux",
        "object-oriented", "design patterns", "postgresql", "redis", "kubernetes",
    ],
    "frontend developer": [
        "react", "javascript", "css", "html", "typescript", "tailwind",
        "redux", "next.js", "ui/ux", "vite", "webpack", "accessibility",
        "responsive design", "api integration", "testing",
    ],
    "data scientist": [
        "python", "pandas", "machine learning", "statistics", "sql",
        "scikit-learn", "nlp", "data visualization", "tensorflow", "pytorch",
        "feature engineering", "model evaluation", "jupyter",
    ],
    "ml engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "mlops",
        "feature engineering", "model deployment", "docker", "kubernetes",
        "data pipelines", "deep learning", "api",
    ],
    "devops engineer": [
        "docker", "kubernetes", "ci/cd", "linux", "ansible", "terraform",
        "aws", "azure", "monitoring", "bash", "git", "jenkins",
        "infrastructure as code", "helm",
    ],
    "product manager": [
        "roadmap", "agile", "scrum", "user stories", "stakeholder",
        "kpis", "a/b testing", "product lifecycle", "go-to-market",
        "wireframes", "cross-functional",
    ],
    "project manager": [
        "pmp", "agile", "scrum", "risk management", "budget",
        "stakeholder", "milestones", "resource planning", "gantt",
        "communication", "leadership",
    ],
}

COMMON_SKILLS: List[str] = [
    "python", "java", "javascript", "react", "docker", "aws", "sql", "git",
    "fastapi", "node.js", "html", "css", "kubernetes", "tensorflow", "pandas",
    "numpy", "typescript", "postgresql", "mongodb", "redis", "linux", "bash",
    "django", "flask", "spring", "laravel", "vue.js", "angular",
]

COMMON_ACTION_VERBS: List[str] = [
    "achieved", "administered", "analyzed", "architected", "automated",
    "built", "collaborated", "designed", "developed", "delivered",
    "enhanced", "engineered", "established", "executed", "implemented",
    "improved", "integrated", "launched", "led", "managed",
    "migrated", "optimized", "oversaw", "reduced", "refactored",
    "resolved", "scaled", "streamlined", "tested", "transformed",
]

ACTION_VERBS_BY_ROLE: Dict[str, List[str]] = {
    "software engineer": [
        "architected", "engineered", "implemented", "optimized", "refactored",
        "integrated", "automated", "deployed", "designed", "developed",
        "built", "migrated", "scaled", "resolved",
    ],
    "frontend developer": [
        "designed", "built", "implemented", "optimized", "created",
        "developed", "refactored", "integrated", "enhanced", "delivered",
    ],
    "data scientist": [
        "analyzed", "modeled", "predicted", "developed", "trained",
        "evaluated", "visualized", "processed", "automated", "deployed",
    ],
    "ml engineer": [
        "trained", "deployed", "optimized", "architected", "automated",
        "designed", "implemented", "scaled", "built", "evaluated",
    ],
    "devops engineer": [
        "automated", "deployed", "managed", "configured", "orchestrated",
        "monitored", "secured", "optimized", "implemented", "migrated",
    ],
    "product manager": [
        "led", "launched", "defined", "prioritized", "collaborated",
        "drove", "delivered", "managed", "designed", "established",
    ],
    "project manager": [
        "managed", "coordinated", "delivered", "oversaw", "planned",
        "executed", "led", "established", "aligned", "resolved",
    ],
}
