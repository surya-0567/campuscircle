from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.post("/{opportunity_id}", status_code=201)
def add_bookmark(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id, models.Bookmark.opportunity_id == opportunity_id
    ).first()
    if existing:
        return {"message": "Already bookmarked.", "bookmarked": True}

    db.add(models.Bookmark(user_id=current_user.id, opportunity_id=opportunity_id))
    db.commit()
    return {"message": "Saved to your bookmarks.", "bookmarked": True}


@router.delete("/{opportunity_id}", status_code=200)
def remove_bookmark(
    opportunity_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id, models.Bookmark.opportunity_id == opportunity_id
    ).first()
    if bookmark:
        db.delete(bookmark)
        db.commit()
    return {"message": "Removed from bookmarks.", "bookmarked": False}


@router.get("", response_model=List[schemas.BookmarkOut])
def my_bookmarks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmarks = (
        db.query(models.Bookmark)
        .options(joinedload(models.Bookmark.opportunity).joinedload(models.Opportunity.poster))
        .filter(models.Bookmark.user_id == current_user.id)
        .order_by(models.Bookmark.created_at.desc())
        .all()
    )
    results = []
    for b in bookmarks:
        out = schemas.BookmarkOut.model_validate(b)
        opp_out = schemas.OpportunityOut.model_validate(b.opportunity)
        opp_out.is_closing_soon = b.opportunity.is_closing_soon
        opp_out.is_expired = b.opportunity.is_expired
        opp_out.application_count = len(b.opportunity.applications)
        opp_out.is_bookmarked = True
        out.opportunity = opp_out
        results.append(out)
    return results
