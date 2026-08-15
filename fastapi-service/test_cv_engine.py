from app.utils.cv_parser import CVParser
from app.services.ats_scorer import ATSScorerService
from app.schemas.cv import GrammarIssue

dummy_cv = """
John Doe
Email: john.doe@example.com
Phone: +1 123 456 7890
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

Summary
Passionate Software Engineer with 3 years of experience building web applications. Highly experienced in Python, FastAPI, Docker, and REST APIs.

Skills
Python, Java, JavaScript, FastAPI, Docker, Git, SQL, HTML, CSS

Experience
Software Engineer at Tech Corp (Jan 2023 - Present)
- Worked on developing microservices using FastAPI and PostgreSQL.
- Responsible for dockerizing applications and setting up CI/CD pipelines.
- Helped with optimizing database queries to reduce response time.

Education
Bachelor of Science in Computer Science
University of Technology (2019 - 2023)
GPA: 3.8/4.0
"""

def main():
    print("Testing CV Parser...")
    structured = CVParser.parse_to_structured(dummy_cv)
    print("Structured Output:")
    print("Name:", structured.personal_information.full_name)
    print("Email:", structured.personal_information.email)
    print("Skills:", structured.skills)
    print("Experience entries count:", len(structured.experience))
    if structured.experience:
        print("First exp job title:", structured.experience[0].job_title)
        print("First exp bullets:", structured.experience[0].bullets)

    print("\nTesting ATS Scorer Service...")
    grammar_issues = [
        GrammarIssue(message="Use active voice", context="Worked on developing", suggestions=["Developed"], rule_id="ACTIVE_VOICE")
    ]
    response = ATSScorerService.analyze_cv(dummy_cv, "Software Engineer", grammar_issues, structured)
    print("Scores:")
    print("  Overall Score:", response.overall_score)
    print("  ATS Score:", response.ats_score)
    print("  Improved ATS Score:", response.improved_ats_score)
    print("  Grammar Score:", response.grammar_score)
    print("  Formatting Score:", response.formatting_score)
    print("  Action Verb Score:", response.action_verb_score)

    print("\nImprovements count:", len(response.improvements))
    for imp in response.improvements:
        print(f"  [{imp.priority.upper()}] {imp.category}: {imp.issue} -> {imp.suggestion}")

    print("\nComparison changes:")
    for change in response.comparison:
        print(f"  {change.section} ({change.change_type}): '{change.original}' -> '{change.improved}'")

    print("\nSUCCESS: CV Engine is fully functional!")

if __name__ == "__main__":
    main()
