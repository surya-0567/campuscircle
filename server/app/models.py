import enum
from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey,
    UniqueConstraint, Float, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    student = "student"
    alumni = "alumni"
    admin = "admin"


class OpportunityType(str, enum.Enum):
    internship = "internship"
    project = "project"
    hackathon = "hackathon"
    freelance = "freelance"


class ModeEnum(str, enum.Enum):
    online = "online"
    offline = "offline"
    hybrid = "hybrid"


class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    rejected = "rejected"
    selected = "selected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.student)

    college = Column(String(160), default="")
    city = Column(String(100), default="")
    branch = Column(String(100), default="")  # e.g. CSE, ECE - mainly students
    year = Column(Integer, nullable=True)  # 1-5, mainly students
    current_company = Column(String(160), default="")  # mainly alumni

    bio = Column(Text, default="")
    skills = Column(ARRAY(String), default=list)
    interests = Column(ARRAY(String), default=list)
    preferred_types = Column(ARRAY(String), default=list)  # subset of OpportunityType values
    preferred_mode = Column(String(20), default="any")  # online/offline/hybrid/any

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    is_reported = Column(Boolean, default=False)
    report_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    opportunities = relationship("Opportunity", back_populates="poster", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    type = Column(SAEnum(OpportunityType, name="opportunity_type_enum"), nullable=False)
    skills_required = Column(ARRAY(String), default=list)
    description = Column(Text, default="")

    organization = Column(String(160), default="")  # college / startup / company name
    city = Column(String(100), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    mode = Column(SAEnum(ModeEnum, name="mode_enum"), default=ModeEnum.online)
    paid = Column(Boolean, default=False)
    stipend = Column(String(80), default="")  # free-text, e.g. "₹10,000/month" or "Unpaid"
    duration = Column(String(80), default="")
    eligibility = Column(String(200), default="")  # free-text, e.g. "2nd/3rd year, CSE/IT"

    deadline = Column(Date, nullable=False)
    is_referral = Column(Boolean, default=False)  # true when posted by alumni as a referral
    external_link = Column(String(400), default="")

    status = Column(String(20), default="open")  # open / closed
    created_at = Column(DateTime, default=datetime.utcnow)

    poster = relationship("User", back_populates="opportunities")
    applications = relationship("Application", back_populates="opportunity", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="opportunity", cascade="all, delete-orphan")

    @property
    def is_closing_soon(self) -> bool:
        return (self.deadline - date.today()).days <= 3 and self.status == "open"

    @property
    def is_expired(self) -> bool:
        return self.deadline < date.today()


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("opportunity_id", "student_id", name="uq_application_once"),)

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(ApplicationStatus, name="application_status_enum"), default=ApplicationStatus.applied)
    cover_note = Column(Text, default="")
    applied_at = Column(DateTime, default=datetime.utcnow)

    opportunity = relationship("Opportunity", back_populates="applications")
    student = relationship("User", back_populates="applications")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "opportunity_id", name="uq_bookmark_once"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    opportunity = relationship("Opportunity", back_populates="bookmarks")
