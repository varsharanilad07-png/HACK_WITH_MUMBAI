"""Tests for the resume generator output format."""
import os
import sys
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from docx import Document
from services.resume.generator import generate_resume
from routes.resume_routes import _build_resume_docx_buffer


def test_generate_resume_uses_expected_sections():
    profile = {
        "name": "Varsharani Lad",
        "phone": "9284073325",
        "email": "varsharanilad7@gmail.com",
        "linkedin": "linkedin.com/in/varsharani-lad-105592306/",
        "github": "github.com/Varsha7781",
        "summary": "AI and full-stack developer focused on career guidance and automation.",
        "education_details": [
            {
                "institution": "MIT Academy Of Engineering",
                "degree": "B.Tech",
                "score": "CGPA - 8.46",
            },
            {
                "institution": "Sanjay Ghodawat Junior College",
                "degree": "HSC",
                "score": "75.00",
            },
        ],
        "experience": [
            {
                "title": "Networking Intern",
                "company": "Cisco",
                "date_range": "June 2025 - August 2025",
                "bullets": ["Built an automated network topology generator."],
            }
        ],
        "projects": [
            {
                "name": "EDUSYNC – AI-powered career path recommender system",
                "tech_stack": "Python, LLM, ML, ReactJS, MongoDB, AWS, Agile",
                "bullets": ["Built a resume parser, skill gap analyzer, and automated course recommender."],
            }
        ],
        "skills": ["Java", "Python", "C++", "SQL", "MongoDB"],
        "industries": ["AWS"],
        "interests": ["FastAPI", "React"],
        "achievements": ["Solved 150+ LeetCode challenges."],
    }

    resume = generate_resume(profile)

    assert "Varsharani Lad" in resume
    assert "PROFESSIONAL SUMMARY" in resume
    assert "EDUCATION" in resume
    assert "MIT Academy Of Engineering" in resume
    assert "EXPERIENCE" in resume
    assert "Networking Intern — Cisco" in resume
    assert "PROJECTS" in resume
    assert "EDUSYNC – AI-powered career path recommender system" in resume
    assert "TECHNICAL SKILLS" in resume
    assert "Java, Python, C++, SQL, MongoDB, AWS, FastAPI, React" in resume
    assert "ACHIEVEMENTS" in resume
    assert "Solved 150+ LeetCode challenges." in resume


def test_generate_resume_accepts_string_education():
    profile = {
        "name": "Varsharani Lad",
        "education": "MIT Academy Of Engineering, CGPA - 8.46; Sanjay Ghodawat Junior College, HSC - 75.00",
        "skills": ["Python"],
        "experience": [],
        "projects": [],
        "achievements": [],
    }

    resume = generate_resume(profile)

    assert "MIT Academy Of Engineering, CGPA - 8.46; Sanjay Ghodawat Junior College, HSC - 75.00" in resume


def test_build_resume_docx_buffer_creates_valid_word_file():
    buffer = _build_resume_docx_buffer("Varsharani Lad\n\nPROFESSIONAL SUMMARY\nExample summary")

    document = Document(buffer)
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]

    assert paragraphs[0] == "Varsharani Lad"
    assert "PROFESSIONAL SUMMARY" in paragraphs