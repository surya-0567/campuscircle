from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------- Auth / User ----------------

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = "student"  # "student" or "alumni"
    college: str = ""
    city: str = ""
    branch: str = ""
    year: Optional[int] = None
    current_company: str = ""
    bio: str = ""
    skills: List[str] = []
    interests: List[str] = []
    preferred_types: List[str] = []
    preferred_mode: str = "any"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v):
        if v not in ("student", "alumni"):
            raise ValueError("role must be 'student' or 'alumni'")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    city: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    current_company: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    preferred_types: Optional[List[str]] = None
    preferred_mode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    college: str
    city: str
    branch: str
    year: Optional[int]
    current_company: str
    bio: str
    skills: List[str]
    interests: List[str]
    preferred_types: List[str]
    preferred_mode: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------- Opportunity ----------------

class OpportunityCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    type: str  # internship / project / hackathon / freelance
    skills_required: List[str] = []
    description: str = ""
    organization: str = ""
    city: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mode: str = "online"  # online / offline / hybrid
    paid: bool = False
    stipend: str = ""
    duration: str = ""
    eligibility: str = ""
    deadline: date
    is_referral: bool = False
    external_link: str = ""

    @field_validator("type")
    @classmethod
    def type_valid(cls, v):
        if v not in ("internship", "project", "hackathon", "freelance"):
            raise ValueError("type must be one of internship, project, hackathon, freelance")
        return v

    @field_validator("mode")
    @classmethod
    def mode_valid(cls, v):
        if v not in ("online", "offline", "hybrid"):
            raise ValueError("mode must be one of online, offline, hybrid")
        return v


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[List[str]] = None
    status: Optional[str] = None  # open / closed
    deadline: Optional[date] = None
    stipend: Optional[str] = None


class PosterOut(BaseModel):
    id: int
    name: str
    role: str
    college: str
    current_company: str

    class Config:
        from_attributes = True


class OpportunityOut(BaseModel):
    id: int
    title: str
    type: str
    skills_required: List[str]
    description: str
    organization: str
    city: str
    latitude: Optional[float]
    longitude: Optional[float]
    mode: str
    paid: bool
    stipend: str
    duration: str
    eligibility: str
    deadline: date
    is_referral: bool
    external_link: str
    status: str
    created_at: datetime
    poster: PosterOut
    is_closing_soon: bool
    is_expired: bool
    application_count: int = 0
    is_bookmarked: bool = False
    has_applied: bool = False
    distance_km: Optional[float] = None
    match_score: Optional[int] = None
    match_reasons: Optional[List[str]] = None

    class Config:
        from_attributes = True


# ---------------- Applications ----------------

class ApplicationCreate(BaseModel):
    cover_note: str = ""


class ApplicationStatusUpdate(BaseModel):
    status: str  # applied / shortlisted / rejected / selected

    @field_validator("status")
    @classmethod
    def status_valid(cls, v):
        if v not in ("applied", "shortlisted", "rejected", "selected"):
            raise ValueError("Invalid status")
        return v


class ApplicantOut(BaseModel):
    id: int
    name: str
    college: str
    branch: str
    year: Optional[int]
    skills: List[str]

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: int
    opportunity_id: int
    status: str
    cover_note: str
    applied_at: datetime
    student: Optional[ApplicantOut] = None
    opportunity: Optional[OpportunityOut] = None

    class Config:
        from_attributes = True


# ---------------- Bookmarks ----------------

class BookmarkOut(BaseModel):
    id: int
    opportunity: OpportunityOut
    created_at: datetime

    class Config:
        from_attributes = True
