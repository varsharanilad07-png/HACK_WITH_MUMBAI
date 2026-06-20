"""Format parsed resume data for API responses."""


def format_parsed_profile(raw: dict) -> dict:
    """
    Normalise and clean a raw parsed profile dict from the LLM.
    Ensures all expected keys exist with sensible defaults.
    """
    return {
        "name": str(raw.get("name", "Unknown")).strip(),
        "skills": _clean_list(raw.get("skills", [])),
        "experience_years": _safe_int(raw.get("experience_years", 0)),
        "education": str(raw.get("education", "Not specified")).strip(),
        "current_role": str(raw.get("current_role", "Not specified")).strip(),
        "industries": _clean_list(raw.get("industries", [])),
        "interests": _clean_list(raw.get("interests", [])),
        "phone": str(raw.get("phone", "")).strip(),  # Preserving phone field
        "email": str(raw.get("email", "")).strip(),  # Preserving email field
        "linkedin": str(raw.get("linkedin", "")).strip(),  # Preserving linkedin field
        "github": str(raw.get("github", "")).strip(),  # Preserving github field
        "summary": str(raw.get("summary", "")).strip(),
        "education_details": raw.get("education_details", []),
        "experience": raw.get("experience", []),
        "projects": raw.get("projects", []),
        "achievements": _clean_list(raw.get("achievements", [])),
        "experience": _clean_list(raw.get("experience", [])),  # Preserving experience field
        "projects": _clean_list(raw.get("projects", [])),  # Preserving projects field
        "achievements": _clean_list(raw.get("achievements", [])),  # Preserving achievements field
    }


def _clean_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _safe_int(value) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0
