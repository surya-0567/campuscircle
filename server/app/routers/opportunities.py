from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.services.matching import score_opportunity
from app.services.geo import haversine_km

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


def _enrich(opp: models.Opportunity, current_user: models.User, db: Session) -> schemas.OpportunityOut:
    out = schemas.OpportunityOut.model_validate(opp)
    out.is_closing_soon = opp.is_closing_soon
    out.is_expired = opp.is_expired
    out.application_count = len(opp.applications)
    out.is_bookmarked = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id, models.Bookmark.opportunity_id == opp.id
    ).first() is not None
    out.has_applied = db.query(models.Application).filter(
        models.Application.student_id == current_user.id, models.Application.opportunity_id == opp.id
    ).first() is not None
    out.distance_km = haversine_km(current_user.latitude, current_user.longitude, opp.latitude, opp.longitude)
    score, reasons = score_opportunity(current_user, opp)
    out.match_score = score
    out.match_reasons = reasons
    return out


@router.post("", response_model=schemas.OpportunityOut, status_code=201)
def create_opportunity(
    payload: schemas.OpportunityCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.is_referral and current_user.role not in (models.RoleEnum.alumni, models.RoleEnum.admin):
        raise HTTPException(status_code=403, detail="Only alumni can mark a posting as a referral.")
    if payload.deadline < date.today():
        raise HTTPException(status_code=400, detail="Deadline can't be in the past.")

    opp = models.Opportunity(
        posted_by=current_user.id,
        title=payload.title.strip(),
        type=models.OpportunityType(payload.type),
        skills_required=list(dict.fromkeys([s.strip() for s in payload.skills_required if s.strip()]))[:25],
        description=payload.description.strip(),
        organization=payload.organization.strip() or current_user.college or current_user.current_company,
        city=payload.city.strip() or current_user.city,
        latitude=payload.latitude if payload.latitude is not None else current_user.latitude,
        longitude=payload.longitude if payload.longitude is not None else current_user.longitude,
        mode=models.ModeEnum(payload.mode),
        paid=payload.paid,
        stipend=payload.stipend.strip(),
        duration=payload.duration.strip(),
        eligibility=payload.eligibility.strip(),
        deadline=payload.deadline,
        is_referral=payload.is_referral,
        external_link=payload.external_link.strip(),
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return _enrich(opp, current_user, db)


@router.get("/feed", response_model=List[schemas.OpportunityOut])
def get_feed(
    type: Optional[str] = None,
    skill: Optional[str] = None,
    city: Optional[str] = None,
    mode: Optional[str] = None,
    paid: Optional[bool] = None,
    closing_soon: Optional[bool] = None,
    referrals_only: Optional[bool] = None,
    q: Optional[str] = Query(None, description="free-text search in title/description"),
    sort: str = Query("match", pattern="^(match|deadline|newest)$"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Opportunity).options(joinedload(models.Opportunity.poster)).filter(
        models.Opportunity.status == "open",
        models.Opportunity.deadline >= date.today(),
        models.Opportunity.posted_by != current_user.id,
    )
    if type:
        query = query.filter(models.Opportunity.type == type)
    if city:
        query = query.filter(models.Opportunity.city.ilike(f"%{city}%"))
    if mode:
        query = query.filter(models.Opportunity.mode == mode)
    if paid is not None:
        query = query.filter(models.Opportunity.paid == paid)
    if referrals_only:
        query = query.filter(models.Opportunity.is_referral.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter((models.Opportunity.title.ilike(like)) | (models.Opportunity.description.ilike(like)))

    opportunities = query.all()

    if skill:
        skill_lower = skill.strip().lower()
        opportunities = [o for o in opportunities if skill_lower in [s.lower() for s in o.skills_required]]

    enriched = [_enrich(o, current_user, db) for o in opportunities]

    if closing_soon:
        enriched = [o for o in enriched if o.is_closing_soon]

    if sort == "match":
        enriched.sort(key=lambda o: o.match_score or 0, reverse=True)
    elif sort == "deadline":
        enriched.sort(key=lambda o: o.deadline)
    else:  # newest
        enriched.sort(key=lambda o: o.created_at, reverse=True)

    return enriched


@router.get("/mine", response_model=List[schemas.OpportunityOut])
def my_postings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opportunities = (
        db.query(models.Opportunity)
        .options(joinedload(models.Opportunity.poster))
        .filter(models.Opportunity.posted_by == current_user.id)
        .order_by(models.Opportunity.created_at.desc())
        .all()
    )
    return [_enrich(o, current_user, db) for o in opportunities]


@router.get("/{opportunity_id}", response_model=schemas.OpportunityOut)
def get_opportunity(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).options(joinedload(models.Opportunity.poster)).filter(
        models.Opportunity.id == opportunity_id
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return _enrich(opp, current_user, db)


@router.patch("/{opportunity_id}", response_model=schemas.OpportunityOut)
def update_opportunity(
    opportunity_id: int,
    payload: schemas.OpportunityUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    if opp.posted_by != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only the poster can edit this opportunity.")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in ("open", "closed"):
        raise HTTPException(status_code=400, detail="status must be 'open' or 'closed'.")
    for field, value in data.items():
        setattr(opp, field, value)

    db.commit()
    db.refresh(opp)
    return _enrich(opp, current_user, db)


@router.delete("/{opportunity_id}", status_code=204)
def delete_opportunity(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    if opp.posted_by != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only the poster can delete this opportunity.")
    db.delete(opp)
    db.commit()
    return None


@router.get("/{opportunity_id}/applicants", response_model=List[schemas.ApplicationOut])
def get_applicants(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    if opp.posted_by != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only the poster can view applicants.")

    apps = (
        db.query(models.Application)
        .options(joinedload(models.Application.student))
        .filter(models.Application.opportunity_id == opportunity_id)
        .order_by(models.Application.applied_at.desc())
        .all()
    )
    return apps
