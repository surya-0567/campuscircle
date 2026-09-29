"""
Pure-logic unit tests for the matching engine and geo-distance helper.
These do NOT require a database - run with:
    ./venv/bin/python -m tests.test_logic
"""
import sys
from datetime import date, timedelta

from app.services.geo import haversine_km, proximity_score
from app.services.matching import score_opportunity
from app import models

passed = 0


def check(label, fn):
    global passed
    try:
        fn()
        print(f"  PASS - {label}")
        passed += 1
    except Exception as e:
        print(f"  FAIL - {label}\n    {e}")
        sys.exit(1)


def make_user(**kwargs):
    defaults = dict(
        id=1, name="Test User", email="t@t.com", password_hash="x", role=models.RoleEnum.student,
        college="", city="", branch="", year=None, current_company="", bio="",
        skills=[], interests=[], preferred_types=[], preferred_mode="any",
        latitude=None, longitude=None,
    )
    defaults.update(kwargs)
    return models.User(**defaults)


def make_opp(**kwargs):
    defaults = dict(
        id=1, posted_by=2, title="Test Opp", type=models.OpportunityType.internship,
        skills_required=[], description="", organization="", city="",
        latitude=None, longitude=None, mode=models.ModeEnum.online, paid=False,
        stipend="", duration="", eligibility="", deadline=date.today() + timedelta(days=10),
        is_referral=False, external_link="", status="open",
    )
    defaults.update(kwargs)
    return models.Opportunity(**defaults)


print("Geo distance:")


def test_haversine_small_distance():
    d = haversine_km(13.0827, 80.2707, 13.0604, 80.2496)
    assert 0 < d < 10, f"expected a small positive distance, got {d}"


def test_haversine_missing_coords():
    d = haversine_km(None, None, 13.06, 80.25)
    assert d is None, f"expected None, got {d}"


def test_proximity_close():
    s = proximity_score(2.0, False)
    assert s == 20, f"expected 20, got {s}"


def test_proximity_city_fallback():
    s = proximity_score(None, True)
    assert s == 15, f"expected 15, got {s}"


check("Haversine distance between two nearby Chennai points is small & positive", test_haversine_small_distance)
check("Haversine returns None when coordinates are missing", test_haversine_missing_coords)
check("proximity_score gives max score for very close distance", test_proximity_close)
check("proximity_score falls back to city match when no coordinates", test_proximity_city_fallback)

print("\nMatching algorithm:")


def test_strong_match():
    student = make_user(skills=["Python", "Cloud Basics"], city="Chennai", preferred_types=["internship"], branch="CSE")
    opp = make_opp(skills_required=["Python", "Cloud Basics"], city="Chennai", eligibility="CSE students only")
    score, reasons = score_opportunity(student, opp)
    assert score >= 90, f"expected a near-perfect match >=90, got {score}"
    assert any("skill" in r.lower() for r in reasons)


def test_weak_match():
    student = make_user(skills=["Guitar"], city="Mumbai")
    opp = make_opp(skills_required=["Python", "React"], city="Chennai")
    score, _ = score_opportunity(student, opp)
    assert score < 50, f"expected a low score for no skill overlap, got {score}"


def test_urgency_bonus():
    student = make_user(skills=["Python"])
    near = make_opp(skills_required=["Python"], deadline=date.today() + timedelta(days=1))
    far = make_opp(skills_required=["Python"], deadline=date.today() + timedelta(days=60))
    near_score, _ = score_opportunity(student, near)
    far_score, _ = score_opportunity(student, far)
    assert near_score > far_score, f"closing-soon ({near_score}) should outscore a far-off deadline ({far_score})"


def test_score_capped_at_100():
    student = make_user(
        skills=["Python", "React", "AI/ML"], city="Chennai", preferred_types=["internship"], branch="CSE",
        latitude=13.08, longitude=80.27,
    )
    opp = make_opp(
        skills_required=["Python"], city="Chennai", eligibility="CSE", latitude=13.08, longitude=80.27,
        deadline=date.today() + timedelta(days=1),
    )
    score, _ = score_opportunity(student, opp)
    assert score <= 100, f"score should never exceed 100, got {score}"


def test_no_required_skills_gets_neutral_credit():
    student = make_user(skills=["Anything"])
    opp = make_opp(skills_required=[])
    score, reasons = score_opportunity(student, opp)
    assert score > 0
    assert any("no specific skills" in r.lower() for r in reasons)


check("Strong overlap + same city + branch eligible scores >= 90", test_strong_match)
check("No skill overlap scores well below a strong match", test_weak_match)
check("A closing-soon opportunity outscores an identical far-off one", test_urgency_bonus)
check("Score is always capped at 100", test_score_capped_at_100)
check("An opportunity with no listed required skills still gets a fair score", test_no_required_skills_gets_neutral_credit)

print(f"\n{passed} test(s) passed.")
