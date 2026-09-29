from collections import Counter
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.deps import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def get_stats(current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    total_students = db.query(models.User).filter(models.User.role == models.RoleEnum.student).count()
    total_alumni = db.query(models.User).filter(models.User.role == models.RoleEnum.alumni).count()
    total_opportunities = db.query(models.Opportunity).count()
    open_opportunities = db.query(models.Opportunity).filter(models.Opportunity.status == "open").count()
    total_applications = db.query(models.Application).count()
    total_referrals = db.query(models.Opportunity).filter(models.Opportunity.is_referral.is_(True)).count()

    skill_counter = Counter()
    for opp in db.query(models.Opportunity).all():
        for s in opp.skills_required:
            skill_counter[s.strip()] += 1
    popular_skills = [{"skill": s, "count": c} for s, c in skill_counter.most_common(10)]

    type_counter = Counter(o.type.value for o in db.query(models.Opportunity).all())
    by_type = [{"type": t, "count": c} for t, c in type_counter.items()]

    return {
        "totalStudents": total_students,
        "totalAlumni": total_alumni,
        "totalOpportunities": total_opportunities,
        "openOpportunities": open_opportunities,
        "totalApplications": total_applications,
        "totalReferrals": total_referrals,
        "popularSkills": popular_skills,
        "byType": by_type,
    }


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role != models.RoleEnum.admin).order_by(models.User.created_at.desc()).all()
    return users


@router.get("/opportunities", response_model=List[schemas.OpportunityOut])
def list_all_opportunities(current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    opps = db.query(models.Opportunity).options(joinedload(models.Opportunity.poster)).order_by(
        models.Opportunity.created_at.desc()
    ).limit(200).all()
    results = []
    for o in opps:
        out = schemas.OpportunityOut.model_validate(o)
        out.is_closing_soon = o.is_closing_soon
        out.is_expired = o.is_expired
        out.application_count = len(o.applications)
        results.append(out)
    return results


@router.get("/reported", response_model=List[schemas.UserOut])
def list_reported(current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.is_reported.is_(True)).all()
    return users
