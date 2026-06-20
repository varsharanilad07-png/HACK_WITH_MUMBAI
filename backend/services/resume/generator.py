"""Resume generator that formats structured profile data into a ready-to-use CV."""


def generate_resume(profile: dict) -> str:
    """Generate a professional resume text from a structured profile."""
    name = _first_non_empty(profile.get("name"), "Unknown")
    contact_line = _format_contact_line(profile)
    summary = _build_summary(profile)
    education_block = _format_education(profile.get("education"), profile)
    experience_block = _format_experience(profile.get("experience", []))
    projects_block = _format_projects(profile.get("projects", []))
    skills_block = _format_skills(profile)
    achievements_block = _format_bullets(profile.get("achievements", []))

    sections = [
        name,
        contact_line,
        "",
        "---",
        "",
        "PROFESSIONAL SUMMARY",
        summary,
        "",
        "---",
        "",
        "EDUCATION",
        education_block,
        "",
        "---",
        "",
        "EXPERIENCE",
        experience_block,
        "",
        "---",
        "",
        "PROJECTS",
        projects_block,
        "",
        "---",
        "",
        "TECHNICAL SKILLS",
        skills_block,
        "",
        "---",
        "",
        "ACHIEVEMENTS",
        achievements_block,
    ]

    return "\n".join(sections).strip()


def _format_contact_line(profile: dict) -> str:
    parts = [
        _first_non_empty(profile.get("phone"), ""),
        _first_non_empty(profile.get("email"), ""),
        _first_non_empty(profile.get("linkedin"), ""),
        _first_non_empty(profile.get("github"), ""),
    ]
    parts = [part for part in parts if part]
    return " | ".join(parts) if parts else ""


def _build_summary(profile: dict) -> str:
    summary = _first_non_empty(profile.get("summary"), "")
    if summary:
        return summary

    name = _first_non_empty(profile.get("name"), "the candidate")
    current_role = _first_non_empty(profile.get("current_role"), "aspiring IT professional")
    skills = _as_list(profile.get("skills"))
    interests = _as_list(profile.get("interests"))
    focus_items = skills[:3] or interests[:3]
    focus_text = ", ".join(focus_items) if focus_items else "software and career development"
    return (
        f"{name} is a {current_role} with a strong interest in {focus_text}. "
        f"The profile reflects hands-on experience in technology, problem solving, and continuous learning."
    )


def _format_education(education, profile: dict) -> str:
    entries = _normalize_section_entries(education)
    if not entries:
        entries = _normalize_section_entries(profile.get("education_details"))

    if not entries and isinstance(education, str) and education.strip():
        entries = [{"institution": education.strip()}]

    if not entries:
        return "- Not specified"

    blocks = []
    for entry in entries:
        if isinstance(entry, str):
            text = entry.strip()
            if text:
                blocks.append(text)
            continue

        institution = _first_non_empty(entry.get("institution"), entry.get("school"), entry.get("college"), entry.get("name"), "Not specified")
        program = _first_non_empty(entry.get("degree"), entry.get("qualification"), entry.get("program"), entry.get("course"), entry.get("title"))
        score = _first_non_empty(entry.get("score"), entry.get("cgpa"), entry.get("grade"), entry.get("percentage"), entry.get("result"))

        lines = [institution]
        if program:
            lines.append(f"- {program}")
        if score:
            lines.append(f"- {score}")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def _format_experience(experience) -> str:
    entries = _normalize_section_entries(experience)
    if not entries:
        return "- Not specified"

    blocks = []
    for entry in entries:
        if isinstance(entry, str):
            blocks.append(entry.strip())
            continue

        title = _first_non_empty(entry.get("title"), entry.get("role"), entry.get("position"), entry.get("name"), "")
        company = _first_non_empty(entry.get("company"), entry.get("organization"), entry.get("employer"), "")
        date_range = _first_non_empty(entry.get("date_range"), entry.get("duration"), entry.get("dates"), entry.get("period"), "")
        bullets = _as_list(entry.get("bullets") or entry.get("achievements") or entry.get("responsibilities") or entry.get("details"))

        lines = []
        header = f"{title} — {company}" if company else title or "Experience"
        lines.append(header)
        if date_range:
            lines.append(date_range)
        if bullets:
            lines.extend(f"- {bullet}" for bullet in bullets)
        else:
            lines.append("- Not specified")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def _format_projects(projects) -> str:
    entries = _normalize_section_entries(projects)
    if not entries:
        return "- Not specified"

    blocks = []
    for entry in entries:
        if isinstance(entry, str):
            blocks.append(entry.strip())
            continue

        name = _first_non_empty(entry.get("name"), entry.get("title"), entry.get("project"), "")
        tech_stack = _first_non_empty(entry.get("tech_stack"), entry.get("stack"), entry.get("technologies"), entry.get("tools"), "")
        bullets = _as_list(entry.get("bullets") or entry.get("achievements") or entry.get("details") or entry.get("points"))

        lines = []
        header = f"{name} — {tech_stack}" if tech_stack else name or "Project"
        lines.append(header)
        if bullets:
            lines.extend(f"- {bullet}" for bullet in bullets)
        else:
            lines.append("- Not specified")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def _format_skills(profile: dict) -> str:
    grouped_skills = _as_list(profile.get("skills"))
    industries = _as_list(profile.get("industries"))
    interests = _as_list(profile.get("interests"))
    extras = [skill for skill in industries + interests if skill not in grouped_skills]
    all_skills = grouped_skills + extras
    if not all_skills:
        return "Not specified"
    return ", ".join(all_skills)


def _format_bullets(value) -> str:
    bullets = _as_list(value)
    if not bullets:
        return "- Not specified"
    return "\n".join(f"- {bullet}" for bullet in bullets)


def _normalize_section_entries(value) -> list:
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split("\n") if part.strip()]
    return []


def _first_non_empty(*values) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""
