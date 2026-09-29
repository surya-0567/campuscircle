from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token
from app.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

VALID_PREFERRED_TYPES = {"internship", "project", "hackathon", "freelance"}
VALID_MODES = {"online", "offline", "hybrid", "any"}


def _clean_list(items, cap=25):
    return list(dict.fromkeys([str(i).strip() for i in (items or []) if str(i).strip()]))[:cap]


@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    preferred_types = [t for t in _clean_list(payload.preferred_types) if t.lower() in VALID_PREFERRED_TYPES]
    preferred_mode = payload.preferred_mode if payload.preferred_mode in VALID_MODES else "any"

    user = models.User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=models.RoleEnum(payload.role),
        college=payload.college.strip(),
        city=payload.city.strip(),
        branch=payload.branch.strip(),
        year=payload.year,
        current_company=payload.current_company.strip(),
        bio=payload.bio.strip(),
        skills=_clean_list(payload.skills),
        interests=_clean_list(payload.interests),
        preferred_types=preferred_types,
        preferred_mode=preferred_mode,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token(user.id)
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserOut.model_validate(current_user)
