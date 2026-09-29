"""
Development seed script - populates demo users and opportunities so the
feed/matching/apply flow can be demonstrated immediately.

Run with:  ./venv/bin/python -m app.seed   (from the server/ folder)
"""
from datetime import date, timedelta

from app.database import SessionLocal, Base, engine
from app import models
from app.auth import hash_password
from app.config import settings

Base.metadata.create_all(bind=engine)


def run():
    db = SessionLocal()
    try:
        print("[seed] Clearing existing demo data...")
        db.query(models.Bookmark).delete()
        db.query(models.Application).delete()
        db.query(models.Opportunity).delete()
        db.query(models.User).delete()
        db.commit()

        print("[seed] Creating admin account...")
        admin = models.User(
            name="CampusCircle Admin",
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            role=models.RoleEnum.admin,
        )
        db.add(admin)

        print("[seed] Creating demo students & alumni...")
        # Chennai-area coordinates so hyperlocal distance scoring has something real to compute.
        arjun = models.User(
            name="Arjun Kumar", email="arjun@campuscircle.edu", password_hash=hash_password("Password@123"),
            role=models.RoleEnum.student, college="RMD Engineering College", city="Chennai",
            branch="CSE", year=3, bio="Backend-leaning CSE student, into Python and cloud.",
            skills=["Python", "Cloud Basics", "Communication"], interests=["AI/ML", "Backend Development"],
            preferred_types=["internship", "hackathon"], preferred_mode="hybrid",
            latitude=13.0827, longitude=80.2707,
        )
        divya = models.User(
            name="Divya Rajan", email="divya@campuscircle.edu", password_hash=hash_password("Password@123"),
            role=models.RoleEnum.student, college="Anna University", city="Chennai",
            branch="IT", year=2, bio="Frontend enthusiast, looking for my first internship.",
            skills=["JavaScript", "React", "UI/UX Design"], interests=["Web Development"],
            preferred_types=["internship", "project"], preferred_mode="online",
            latitude=13.0108, longitude=80.2337,
        )
        karthik = models.User(
            name="Karthik Iyer", email="karthik@campuscircle.edu", password_hash=hash_password("Password@123"),
            role=models.RoleEnum.student, college="SRM Institute", city="Chennai",
            branch="ECE", year=4, bio="Looking to build a hackathon team.",
            skills=["C++", "Embedded Systems", "Python"], interests=["Hackathons", "IoT"],
            preferred_types=["hackathon", "project"], preferred_mode="offline",
            latitude=12.8230, longitude=80.0444,
        )
        priya_alumni = models.User(
            name="Priya Sharma", email="priya.alumni@campuscircle.edu", password_hash=hash_password("Password@123"),
            role=models.RoleEnum.alumni, college="RMD Engineering College", city="Chennai",
            current_company="Zoho Corporation", bio="RMDEC alum, now SDE at Zoho. Happy to refer juniors.",
            skills=["Python", "System Design"], interests=["Mentoring"],
            latitude=13.0604, longitude=80.2496,
        )
        rahul_alumni = models.User(
            name="Rahul Verma", email="rahul.alumni@campuscircle.edu", password_hash=hash_password("Password@123"),
            role=models.RoleEnum.alumni, college="Anna University", city="Bengaluru",
            current_company="Freshworks", bio="Product manager, occasionally posts PM internship referrals.",
            skills=["Product Management", "Communication"], interests=["Mentoring"],
            latitude=12.9716, longitude=77.5946,
        )

        db.add_all([arjun, divya, karthik, priya_alumni, rahul_alumni])
        db.commit()
        for u in [arjun, divya, karthik, priya_alumni, rahul_alumni]:
            db.refresh(u)

        print("[seed] Creating demo opportunities...")
        today = date.today()
        opportunities = [
            models.Opportunity(
                posted_by=priya_alumni.id, title="Cloud Support Intern", type=models.OpportunityType.internship,
                skills_required=["Cloud Basics", "Python", "Communication"],
                description="Support the cloud infra team, learn AWS/GCP fundamentals on the job.",
                organization="Zoho Corporation", city="Chennai", latitude=13.0604, longitude=80.2496,
                mode=models.ModeEnum.hybrid, paid=True, stipend="₹15,000/month", duration="3 months",
                eligibility="3rd/4th year CSE/IT", deadline=today + timedelta(days=2), is_referral=True,
            ),
            models.Opportunity(
                posted_by=arjun.id, title="AI/ML Internship - Startup", type=models.OpportunityType.internship,
                skills_required=["Python", "AI/ML", "Communication"],
                description="Early-stage startup looking for an ML intern to help with a recommendation engine.",
                organization="NeuraTech Labs", city="Chennai", latitude=13.05, longitude=80.21,
                mode=models.ModeEnum.hybrid, paid=True, stipend="₹10,000/month", duration="2 months",
                eligibility="2nd/3rd year, any branch", deadline=today + timedelta(days=8), is_referral=False,
            ),
            models.Opportunity(
                posted_by=karthik.id, title="College Hackathon - Team Needed", type=models.OpportunityType.hackathon,
                skills_required=["C++", "Python", "Embedded Systems"],
                description="Need 2 more teammates for the upcoming 24-hour IoT hackathon.",
                organization="SRM Institute", city="Chennai", latitude=12.8230, longitude=80.0444,
                mode=models.ModeEnum.offline, paid=False, stipend="", duration="24 hours",
                eligibility="Any year, ECE/CSE/IT", deadline=today + timedelta(days=5), is_referral=False,
            ),
            models.Opportunity(
                posted_by=divya.id, title="React Project Collaborator", type=models.OpportunityType.project,
                skills_required=["React", "JavaScript"],
                description="Building a student marketplace app, need one more frontend collaborator.",
                organization="Anna University", city="Chennai", latitude=13.0108, longitude=80.2337,
                mode=models.ModeEnum.online, paid=False, stipend="", duration="1 month",
                eligibility="Any year", deadline=today + timedelta(days=20), is_referral=False,
            ),
            models.Opportunity(
                posted_by=rahul_alumni.id, title="Associate PM Referral", type=models.OpportunityType.internship,
                skills_required=["Product Management", "Communication"],
                description="Referral for an Associate PM internship at Freshworks - reach out if interested!",
                organization="Freshworks", city="Bengaluru", latitude=12.9716, longitude=77.5946,
                mode=models.ModeEnum.hybrid, paid=True, stipend="₹20,000/month", duration="6 months",
                eligibility="Final year, any branch", deadline=today + timedelta(days=15), is_referral=True,
            ),
            models.Opportunity(
                posted_by=priya_alumni.id, title="Freelance Logo Design Gig", type=models.OpportunityType.freelance,
                skills_required=["UI/UX Design"],
                description="Small startup needs a logo + brand colors, quick freelance gig.",
                organization="NeuraTech Labs", city="Chennai", latitude=13.06, longitude=80.25,
                mode=models.ModeEnum.online, paid=True, stipend="₹3,000 flat", duration="1 week",
                eligibility="Any year", deadline=today + timedelta(days=30), is_referral=False,
            ),
        ]
        db.add_all(opportunities)
        db.commit()

        print(f"\n[seed] Done! Demo accounts (all use password: Password@123):")
        print("  Student: arjun@campuscircle.edu  (Chennai, Python/Cloud, wants AI/ML internships)")
        print("  Student: divya@campuscircle.edu  (Chennai, React/JS, wants web dev internships)")
        print("  Student: karthik@campuscircle.edu (Chennai, C++/Embedded, wants hackathons)")
        print("  Alumni:  priya.alumni@campuscircle.edu (Zoho, posts referrals)")
        print("  Alumni:  rahul.alumni@campuscircle.edu (Freshworks, posts referrals)")
        print(f"  Admin:   {settings.admin_email} / {settings.admin_password}")
        print("\n[seed] Try logging in as Arjun - the Cloud Support Intern referral should show a high match score.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
