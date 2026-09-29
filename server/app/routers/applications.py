from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/{opportunity_id}", response_model=schemas.ApplicationOut, status_code=201)
def apply_to_opportunity(
    opportunity_id: int,
    payload: schemas.ApplicationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    if opp.posted_by == current_user.id:
        raise HTTPException(status_code=400, detail="You can't apply to your own posting.")
    if opp.status != "open" or opp.deadline < date.today():
        raise HTTPException(status_code=400, detail="This opportunity is no longer accepting applications.")

    existing = db.query(models.Application).filter(
        models.Application.opportunity_id == opportunity_id,
        models.Application.student_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You've already applied to this opportunity.")

    application = models.Application(
        opportunity_id=opportunity_id,
        student_id=current_user.id,
        cover_note=payload.cover_note.strip(),
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/mine", response_model=List[schemas.ApplicationOut])
def my_applications(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apps = (
        db.query(models.Application)
        .options(joinedload(models.Application.opportunity).joinedload(models.Opportunity.poster))
        .filter(models.Application.student_id == current_user.id)
        .order_by(models.Application.applied_at.desc())
        .all()
    )
    results = []
    for a in apps:
        out = schemas.ApplicationOut.model_validate(a)
        opp_out = schemas.OpportunityOut.model_validate(a.opportunity)
        opp_out.is_closing_soon = a.opportunity.is_closing_soon
        opp_out.is_expired = a.opportunity.is_expired
        opp_out.application_count = len(a.opportunity.applications)
        out.opportunity = opp_out
        results.append(out)
    return results


@router.patch("/{application_id}/status", response_model=schemas.ApplicationOut)
def update_application_status(
    application_id: int,
    payload: schemas.ApplicationStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = db.query(models.Application).options(joinedload(models.Application.opportunity)).filter(
        models.Application.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    if application.opportunity.posted_by != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Only the opportunity's poster can update application status.")

    application.status = models.ApplicationStatus(payload.status)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def withdraw_application(
    application_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    if application.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only withdraw your own application.")
    db.delete(application)
    db.commit()
    return None
