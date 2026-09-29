"""
Rule-Based Opportunity Matching Engine (explicitly a transparent, explainable
scoring model for this prototype - NOT a trained AI/ML model). It is written
so a machine-learning ranker could be swapped in later without changing the
API shape ("AI-ready"), per the project's tech stack slide.

Score breakdown (0-100):
  - Skill fit          : up to 50 points  (overlap between student skills and required skills)
  - Hyperlocal proximity: up to 20 points (distance in km, or city match fallback)
  - Preferred type match: up to 10 points (internship/project/hackathon/freelance)
  - Domain/eligibility  : up to 15 points (branch appears in the eligibility text)
  - Freshness/urgency   : up to 5 points  (closing soon nudges it up the feed)
"""
from typing import List, Tuple

from app import models
from app.services.geo import haversine_km, proximity_score


def _normalize(items: List[str]) -> List[str]:
    return [i.strip().lower() for i in (items or []) if i and i.strip()]


def score_opportunity(student: models.User, opp: models.Opportunity) -> Tuple[int, List[str]]:
    reasons: List[str] = []
    total = 0

    # ---- Skill fit (0-50) ----
    student_skills = set(_normalize(student.skills))
    required_skills = set(_normalize(opp.skills_required))
    if required_skills:
        overlap = student_skills & required_skills
        fit_ratio = len(overlap) / len(required_skills)
        skill_points = round(fit_ratio * 50)
        total += skill_points
        if overlap:
            reasons.append(f"Matches {len(overlap)}/{len(required_skills)} required skill(s): {', '.join(sorted(overlap))}")
    else:
        total += 10  # no specific skills required - small neutral credit
        reasons.append("No specific skills required")

    # ---- Hyperlocal proximity (0-20) ----
    distance = haversine_km(student.latitude, student.longitude, opp.latitude, opp.longitude)
    same_city = bool(student.city) and bool(opp.city) and student.city.strip().lower() == opp.city.strip().lower()
    prox_points = proximity_score(distance, same_city)
    total += prox_points
    if distance is not None:
        reasons.append(f"{distance} km away")
    elif same_city:
        reasons.append(f"Same city ({opp.city})")

    # ---- Preferred opportunity type (0-10) ----
    preferred_types = set(_normalize(student.preferred_types))
    if not preferred_types or opp.type.value in preferred_types:
        total += 10
        if preferred_types:
            reasons.append(f"Matches your preferred type ({opp.type.value})")
    

    # ---- Domain / eligibility text match (0-15) ----
    if student.branch and opp.eligibility:
        if student.branch.strip().lower() in opp.eligibility.strip().lower():
            total += 15
            reasons.append(f"Open to your branch ({student.branch})")
        else:
            total += 5  # eligibility stated but doesn't explicitly exclude/include - small credit
    else:
        total += 8  # no eligibility restriction stated

    # ---- Freshness / urgency (0-5) ----
    if opp.is_closing_soon:
        total += 5
        reasons.append("Closing soon")

    return min(total, 100), reasons


def rank_opportunities(student: models.User, opportunities: List[models.Opportunity]):
    """Returns a list of (opportunity, score, reasons) sorted by score desc."""
    scored = []
    for opp in opportunities:
        score, reasons = score_opportunity(student, opp)
        scored.append((opp, score, reasons))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
