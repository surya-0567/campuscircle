from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.routers.auth import _clean_list, VALID_PREFERRED_TYPES, VALID_MODES

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found.")
    return schemas.UserOut.model_validate(user)


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    payload: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)

    if "skills" in data and data["skills"] is not None:
        data["skills"] = _clean_list(data["skills"])
    if "interests" in data and data["interests"] is not None:
        data["interests"] = _clean_list(data["interests"])
    if "preferred_types" in data and data["preferred_types"] is not None:
        data["preferred_types"] = [t for t in _clean_list(data["preferred_types"]) if t.lower() in VALID_PREFERRED_TYPES]
    if "preferred_mode" in data and data["preferred_mode"] not in VALID_MODES:
        data.pop("preferred_mode", None)

    for field, value in data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return schemas.UserOut.model_validate(current_user)
