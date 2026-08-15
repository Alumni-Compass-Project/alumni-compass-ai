"""
CV Analysis & Optimization router.
STEP 1-6 pipeline:
  POST /v1/cv/analyze   → extract → structure → score → improve → return JSON
  POST /v1/cv/download  → returns structured CV JSON for Laravel PDF generation
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from typing import Optional

from ..schemas.cv import CVAnalysisResponse
from ..services.ats_scorer import ATSScorerService
from ..utils.cv_parser import CVParser
from ..utils.grammar import GrammarChecker

router = APIRouter(prefix="/cv", tags=["CV Analysis"])


async def _extract_cv_text(file: Optional[UploadFile], text_content: Optional[str]) -> str:
    """STEP 1-2: Extract text from uploaded file or raw text input."""
    if file:
        content = await file.read()
        fname   = (file.filename or "").lower()
        if fname.endswith(".pdf"):
            return CVParser.extract_text_from_pdf(content)
        elif fname.endswith((".docx", ".doc")):
            return CVParser.extract_text_from_docx(content)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {file.filename}. Upload PDF or DOCX.",
            )
    elif text_content:
        return text_content
    raise HTTPException(status_code=400, detail="A CV file or text_content must be provided.")


@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    target_role:  str             = Form(default="Software Engineer"),
    file:         Optional[UploadFile] = File(None),
    text_content: Optional[str]   = Form(None),
):
    """
    STEP 1–6: Full pipeline.
    1. Accept PDF / DOCX
    2. Extract text (pdfplumber → PyMuPDF fallback)
    3. Parse into StructuredCV JSON
    4. Score: ATS, keywords, grammar, action verbs, formatting, readability
    5. Generate recommendations + improvement suggestions
    6. Build improved StructuredCV + comparison diff
    """
    cv_text = await _extract_cv_text(file, text_content)

    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="No text was found in the CV.")

    # STEP 3: Structured parse (section-order preserved)
    structured = CVParser.parse_to_structured(cv_text)

    # STEP 4: Grammar (non-critical, wrapped)
    grammar_issues = []
    try:
        grammar_issues = await GrammarChecker.check_grammar(cv_text)
    except Exception:
        pass

    # STEP 5-6: Score, improve, compare
    result = ATSScorerService.analyze_cv(cv_text, target_role, grammar_issues, structured)
    return result


@router.post("/optimize", response_model=CVAnalysisResponse)
async def optimize_cv(
    target_role:  str             = Form(default="Software Engineer"),
    file:         Optional[UploadFile] = File(None),
    text_content: Optional[str]   = Form(None),
):
    """
    Same pipeline as /analyze but used explicitly for the 'optimize' operation.
    The improved_structured field is what Laravel uses for PDF generation.
    """
    cv_text = await _extract_cv_text(file, text_content)

    if not cv_text.strip():
        cv_text = "Software Engineer with experience in web development."

    structured     = CVParser.parse_to_structured(cv_text)
    grammar_issues = []
    try:
        grammar_issues = await GrammarChecker.check_grammar(cv_text)
    except Exception:
        pass

    return ATSScorerService.analyze_cv(cv_text, target_role, grammar_issues, structured)
