"""Trend analysis — aggregates Adzuna data into chart-ready structures."""
from concurrent.futures import ThreadPoolExecutor, as_completed

from .adzuna_client import fetch_job_demand


def analyze_trends_for_roles(roles: list[str], country: str = "us") -> dict:
    """
    Fetch job demand for multiple roles in parallel and return chart-ready data.
    Includes open positions, salary ranges, and a bar chart payload.
    """
    live_data: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=min(len(roles), 5)) as pool:
        futures = {pool.submit(fetch_job_demand, role, country): role for role in roles}
        for future in as_completed(futures):
            role = futures[future]
            try:
                live_data[role] = future.result()
            except Exception as exc:
                live_data[role] = {
                    "job_title": role,
                    "open_positions": 0,
                    "sample_jobs": [],
                    "error": str(exc),
                }

    results = []
    for role in roles:
        data = live_data.get(role, {})
        open_positions = data.get("open_positions", 0)
        count = open_positions if isinstance(open_positions, int) else 0
        salary = _extract_salary(data.get("sample_jobs", []))
        results.append({
            "role": role,
            "open_positions": count,
            "salary_min": salary["min"],
            "salary_max": salary["max"],
            "salary_avg": salary["avg"],
            "sample_jobs": data.get("sample_jobs", []),
            "error": data.get("error"),
        })

    # Sort by demand descending so the chart shows hottest roles first
    results.sort(key=lambda r: r["open_positions"], reverse=True)

    return {
        "roles": [r["role"] for r in results],
        "open_positions": [r["open_positions"] for r in results],
        "details": results,
        "chart": {
            "type": "bar",
            "labels": [r["role"] for r in results],
            "datasets": [
                {
                    "label": "Open Positions",
                    "data": [r["open_positions"] for r in results],
                    "backgroundColor": "#534AB7",
                    "borderRadius": 6,
                },
                {
                    "label": "Avg Salary (USD)",
                    "data": [r["salary_avg"] or 0 for r in results],
                    "backgroundColor": "#10B981",
                    "borderRadius": 6,
                    "yAxisID": "salary",
                },
            ],
        },
    }


def get_salary_estimates(role: str) -> dict:
    """
    Extract salary range from Adzuna sample jobs for a role.
    Returns min, max, and average salary estimates.
    """
    data = fetch_job_demand(role)
    salary = _extract_salary(data.get("sample_jobs", []))
    return {
        "role": role,
        "open_positions": data.get("open_positions", "N/A"),
        "salary_min": salary["min"],
        "salary_max": salary["max"],
        "salary_avg": salary["avg"],
    }


def extract_trending_skills(roles: list[str]) -> dict:
    """
    Identify trending skills by aggregating job titles from Adzuna listings
    across multiple roles and counting keyword frequency.

    Returns a ranked list of trending skill keywords with counts.
    """
    SKILL_KEYWORDS = [
        "python", "javascript", "typescript", "java", "go", "rust", "c++",
        "react", "node", "django", "fastapi", "spring", "kubernetes", "docker",
        "aws", "azure", "gcp", "terraform", "ci/cd", "devops", "mlops",
        "machine learning", "deep learning", "llm", "nlp", "data science",
        "sql", "nosql", "mongodb", "postgresql", "redis", "kafka",
        "microservices", "rest api", "graphql", "cybersecurity", "blockchain",
        "flutter", "swift", "kotlin", "android", "ios",
    ]

    keyword_counts: dict[str, int] = {}

    for role in roles:
        data = fetch_job_demand(role)
        for job in data.get("sample_jobs", []):
            title_lower = (job.get("title") or "").lower()
            for kw in SKILL_KEYWORDS:
                if kw in title_lower:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    ranked = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return {
        "trending_skills": [{"skill": k, "mentions": v} for k, v in ranked[:20]],
        "chart": {
            "type": "horizontalBar",
            "labels": [k for k, _ in ranked[:10]],
            "datasets": [{
                "label": "Mentions in Job Listings",
                "data": [v for _, v in ranked[:10]],
                "backgroundColor": "#F59E0B",
            }],
        },
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_salary(sample_jobs: list[dict]) -> dict:
    """Compute min/max/avg salary from a list of Adzuna job dicts."""
    mins = [j["salary_min"] for j in sample_jobs if j.get("salary_min")]
    maxs = [j["salary_max"] for j in sample_jobs if j.get("salary_max")]
    all_vals = mins + maxs
    return {
        "min": min(mins) if mins else None,
        "max": max(maxs) if maxs else None,
        "avg": round(sum(all_vals) / len(all_vals), 2) if all_vals else None,
    }
