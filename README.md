# CampusCircle - Hyperlocal Student Opportunity Network

A full-stack web application where students post and find internships, projects,
hackathons and freelance gigs within their own college/city — matched by skill,
filtered smartly, and applied to directly, with no middleman. Alumni can post
referrals too.

Built for a Product Development Lab review, following the architecture proposed
in the project's own presentation: **React/Next.js-style frontend experience,
Python FastAPI backend, PostgreSQL database.**

> **Note on the frontend implementation:** the UI is built as a dependency-free
> vanilla HTML/CSS/JS single-page app rather than a React/Next.js build pipeline.
> It delivers the same pages, UX and desktop-first layout the PPT describes, but
> needs zero build step (npm install, bundlers, etc.) - just open it in a
> browser. It can be migrated into React later without changing the API at all,
> since the backend is a clean, independent REST API.

---

## 1. Tech Stack

| Layer          | Technology                                             |
|----------------|---------------------------------------------------------|
| Frontend       | Vanilla HTML, CSS, JavaScript (desktop/laptop-first SPA) |
| Backend        | Python, FastAPI                                          |
| Database       | PostgreSQL (via SQLAlchemy ORM)                          |
| Auth           | JWT (python-jose) + bcrypt password hashing              |
| Matching Logic | Rule-based, explainable scoring algorithm ("AI-ready")   |
| Maps/Location  | Haversine distance calculation (lat/lon), city fallback  |

The matching engine is **explicitly rule-based and transparent** for this
prototype (skill overlap + distance + type + eligibility + urgency) - it is
*not* a trained AI/ML model, but is structured so a real ranking model could be
swapped in later without changing the API shape.

---

## 2. Project Structure

```
campuscircle-app/
├── server/                     FastAPI backend
│   ├── app/
│   │   ├── main.py             App entry point, route wiring, static file serving
│   │   ├── config.py           Settings loaded from .env
│   │   ├── database.py         SQLAlchemy engine/session
│   │   ├── models.py           ORM models: User, Opportunity, Application, Bookmark
│   │   ├── schemas.py          Pydantic request/response schemas
│   │   ├── auth.py             Password hashing + JWT helpers
│   │   ├── deps.py             FastAPI dependencies (get_current_user, require_admin)
│   │   ├── seed.py             Demo data seed script
│   │   ├── routers/            auth, users, opportunities, applications, bookmarks, admin
│   │   └── services/
│   │       ├── matching.py     Rule-based opportunity scoring engine
│   │       └── geo.py          Haversine distance + proximity scoring
│   ├── tests/
│   │   ├── test_logic.py       Unit tests for matching/geo (no DB needed)
│   │   └── test_wiring.py      API wiring tests (FastAPI TestClient)
│   ├── requirements.txt
│   └── .env.example
└── client/                      Vanilla JS frontend
    ├── index.html                Landing page
    ├── login.html
    ├── register.html
    ├── app.html                  Authenticated app shell (sidebar + router)
    ├── css/styles.css
    └── js/
        ├── api.js                Fetch wrapper + auth/session helpers
        ├── ui.js                 Shared UI-building helpers (cards, badges, etc.)
        ├── router.js             Hash-based router + sidebar state
        ├── app.js                Bootstraps the app shell
        └── views/                One file per page (dashboard, feed, profile, etc.)
```

---

## 3. Setup & Run Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (running locally, or a free instance on a host like Supabase/Railway/Neon)

### Step 1 - Install PostgreSQL and create the database
```bash
# Ubuntu/Debian example
sudo apt install postgresql
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER campuscircle WITH PASSWORD 'campuscircle_dev_pw';"
sudo -u postgres psql -c "CREATE DATABASE campuscircle OWNER campuscircle;"
```
(On Windows/Mac, install PostgreSQL normally and create the same user/database
through pgAdmin or psql.)

### Step 2 - Backend setup
```bash
cd server
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit DATABASE_URL/JWT_SECRET if needed
```

### Step 3 - Seed demo data (creates tables automatically)
```bash
python -m app.seed
```
This creates 3 demo students, 2 demo alumni, 1 admin, and 6 sample opportunities.

### Step 4 - Run the server
```bash
uvicorn app.main:app --reload --port 8000
```
Open **http://localhost:8000** - the backend also serves the frontend directly,
so this one URL is all you need.

### Demo accounts (all use password Password@123)
| Email                          | Role    | Notes                                      |
|---------------------------------|---------|---------------------------------------------|
| arjun@campuscircle.edu          | Student | Python/Cloud skills, Chennai                |
| divya@campuscircle.edu          | Student | React/JS skills, Chennai                    |
| karthik@campuscircle.edu        | Student | C++/Embedded, wants hackathons              |
| priya.alumni@campuscircle.edu   | Alumni  | Posts referrals at Zoho                     |
| rahul.alumni@campuscircle.edu   | Alumni  | Posts referrals at Freshworks (Bengaluru)   |
| admin@campuscircle.edu          | Admin   | Password: Admin@12345                       |

Try logging in as Arjun and opening the Feed - the "Cloud Support Intern"
referral should show a ~90%+ match score (matching skills, same city, closing soon).

---

## 4. Running the Tests

```bash
cd server
python -m tests.test_logic     # matching algorithm + geo distance (no DB needed)
python -m tests.test_wiring    # API wiring, auth enforcement, error handling
```
Both suites were run against a live PostgreSQL instance during development -
every endpoint listed below has been exercised with real HTTP requests, not
just code review. One real bug (a duplicate-application check that returned a
raw 500 instead of a clean error) was caught and fixed this way before delivery.

---

## 5. API Reference

All routes are prefixed with /api. Protected routes require
Authorization: Bearer <token>.

### Auth
| Method | Route              | Description                    |
|--------|--------------------|---------------------------------|
| POST   | /auth/register     | Create a student or alumni account |
| POST   | /auth/login        | Log in, returns a JWT           |
| GET    | /auth/me           | Get the current user's profile  |

### Users
| Method | Route            | Description                  |
|--------|------------------|-------------------------------|
| GET    | /users/{id}      | View another user's public profile |
| PUT    | /users/me        | Update your own profile       |

### Opportunities
| Method | Route                              | Description                                 |
|--------|-------------------------------------|----------------------------------------------|
| POST   | /opportunities                      | Post a new opportunity                      |
| GET    | /opportunities/feed                 | Personalized, filterable, match-ranked feed |
| GET    | /opportunities/mine                 | Opportunities you've posted                 |
| GET    | /opportunities/{id}                 | Single opportunity detail (with match score)|
| PATCH  | /opportunities/{id}                 | Edit/close your own posting                 |
| DELETE | /opportunities/{id}                 | Delete your own posting                     |
| GET    | /opportunities/{id}/applicants      | View applicants (poster only)               |

Feed query params: type, skill, city, mode, paid, closing_soon,
referrals_only, q (free-text search), sort (match / deadline / newest).

### Applications
| Method | Route                             | Description                       |
|--------|------------------------------------|-------------------------------------|
| POST   | /applications/{opportunity_id}     | Apply to an opportunity             |
| GET    | /applications/mine                 | Your application history/status     |
| PATCH  | /applications/{id}/status          | Update applicant status (poster only)|
| DELETE | /applications/{id}                 | Withdraw your own application       |

### Bookmarks
| Method | Route                          | Description             |
|--------|----------------------------------|--------------------------|
| POST   | /bookmarks/{opportunity_id}      | Save an opportunity      |
| DELETE | /bookmarks/{opportunity_id}      | Remove a bookmark        |
| GET    | /bookmarks                       | List saved opportunities |

### Admin (admin role only)
| Method | Route                  | Description                         |
|--------|-------------------------|---------------------------------------|
| GET    | /admin/stats            | Platform-wide stats & popular skills  |
| GET    | /admin/users            | List all registered users             |
| GET    | /admin/opportunities    | List all opportunities                |

---

## 6. The Matching Algorithm (Explained)

For every opportunity in the feed, a **0-100 match score** is computed against
the viewing student's profile:

| Factor                        | Points | Logic                                                      |
|---------------------------------|--------|--------------------------------------------------------------|
| Skill fit                     | 0-50   | (matched skills) / (required skills) x 50                   |
| Hyperlocal proximity          | 0-20   | Haversine distance in km if coordinates are set, else city-name match |
| Preferred opportunity type    | 0-10   | Does it match the student's stated interests?               |
| Branch/domain eligibility     | 0-15   | Does the eligibility text mention the student's branch?      |
| Deadline urgency              | 0-5    | Small bonus if it's closing within 3 days                   |

Every match includes a human-readable list of reasons (e.g. "Matches 2/3
required skills: python, cloud basics", "3.4 km away", "Closing soon") so the
scoring is fully explainable - never a black box.

---

## 7. Security Notes

- Passwords are hashed with bcrypt, never stored in plaintext.
- All mutating routes require a valid JWT; ownership is checked server-side
  (you can't edit someone else's profile, close someone else's posting, view
  applicants for a posting that isn't yours, or apply on someone's behalf).
- A student cannot apply to their own posting, and cannot apply twice to the
  same opportunity (enforced with a DB-level unique constraint + app-level check).
- Admin-only routes are protected by a role check, not just authentication.
- Secrets (JWT secret, DB credentials) are loaded from environment variables,
  never hardcoded - see .env.example.
- A student's own postings are automatically excluded from their own discovery feed.

---

## 8. Known Limitations (by design, for prototype scope)

- No email verification or password-reset flow yet.
- No file upload for profile photos (avatars are auto-generated initials).
- No push/email notifications for deadline alerts - they're surfaced in-app
  on the Dashboard and a dedicated "Deadline Alerts" page instead.
- The frontend is vanilla JS rather than a React/Next.js build, for zero-setup
  simplicity (see the note at the top of this file).
