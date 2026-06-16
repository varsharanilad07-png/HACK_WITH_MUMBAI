import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def generate_resume(profile: dict) -> str:
    """Generate a professional resume text from a structured profile."""
    name = profile.get("name", "Unknown")
    phone = profile.get("phone", "")
    email = profile.get("email", "")
    linkedin = profile.get("linkedin", "")
    github = profile.get("github", "")
    current_role = profile.get("current_role", "")
    education = profile.get("education", "")
    skills = profile.get("skills", [])
    industries = profile.get("industries", [])
    interests = profile.get("interests", [])
    achievements = profile.get("achievements", [])
    projects = profile.get("projects", [])
    experience_entries = profile.get("experience", [])

    contact_line = " | ".join([item for item in [phone, email, linkedin, github] if item])
    if contact_line:
        contact_line = contact_line.strip()

    prompt = f"""
You are a professional resume writer. Create a resume in plain text using the exact format below.
Use the provided profile information. If any section details are missing, omit only the missing lines, but keep the section headings.
Do not include any extra commentary or markdown formatting.

Resume output format:
Name
phone | email | linkedin | github

---

PROFESSIONAL SUMMARY
<2-3 concise sentences summarising the candidate's strengths, experience, and technical focus>

---

EDUCATION
<Institution>  
- <Degree / Program>  
- <Score / CGPA / Grade>

<Institution>  
- <Degree / Program or qualification>  
- <Score / Grade>

---

EXPERIENCE
<Title> — <Company>  
<Date range>  
- <Achievement bullet>
- <Achievement bullet>

<Title> — <Company>  
<Date range>  
- <Achievement bullet>
- <Achievement bullet>

---

PROJECTS
<Project name> — <Tech stack>  
- <Achievement bullet>
- <Achievement bullet>

<Project name> — <Tech stack>  
- <Achievement bullet>
- <Achievement bullet>

---

TECHNICAL SKILLS
<comma separated skills and tools>

---

ACHIEVEMENTS
- <Achievement bullet>
- <Achievement bullet>
"""

    profile_data = {
        "name": name,
        "current_role": current_role,
        "education": education,
        "skills": skills,
        "industries": industries,
        "interests": interests,
        "achievements": achievements,
        "projects": projects,
        "experience": experience_entries,
    }

    supplemental = f"Name: {name}\n"
    if contact_line:
        supplemental += f"Contact: {contact_line}\n"
    if current_role:
        supplemental += f"Current role: {current_role}\n"
    if education:
        supplemental += f"Education: {education}\n"
    if skills:
        supplemental += f"Skills: {', '.join(skills)}\n"
    if industries:
        supplemental += f"Industries: {', '.join(industries)}\n"
    if interests:
        supplemental += f"Interests: {', '.join(interests)}\n"
    if achievements:
        supplemental += f"Achievements: {', '.join(achievements)}\n"
    if projects:
        supplemental += f"Projects: {', '.join(projects)}\n"
    if experience_entries:
        supplemental += f"Experience: {experience_entries}\n"

    response = _client.chat.completions.create(
        messages=[{"role": "user", "content": prompt + "\n\n" + supplemental}],
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
