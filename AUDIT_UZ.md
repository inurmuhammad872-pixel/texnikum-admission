# Texnikum ariza sayti - kod auditi (2026-11-22)

Manba: https://github.com/inurmuhammad872-pixel/texnikum-admission
Branch: main; source reviewed through connected GitHub read API.
Scope: repository contents, security boundaries, Django configuration,
application flows, responsive frontend presence, Railway readiness.

## Topilmalar (original code)

| ID | Daraja | Holat | Dalil |
|---|---|---|---|
| 01 | CRITICAL | StudentViewSet AllowAny: public GET list/retrieve, PUT/PATCH/DELETE and approve/reject | apps/students/views.py:20-39,59-89 |
| 02 | CRITICAL | Public student responses include JSHSHIR and phone; search by national ID is allowed | apps/students/views.py:25; serializers.py:28-46 |
| 03 | CRITICAL | DirectionViewSet allows public changes and deletion | apps/students/views.py:12-16 |
| 04 | CRITICAL | Hardcoded Django SECRET_KEY and DEBUG=True | project/settings.py:23-28 |
| 05 | CRITICAL | Public repository tracks db.sqlite3 (may contain private records; contents not inspected) | db.sqlite3 at repo root |
| 06 | BLOCKER | 7 absent apps in INSTALLED_APPS prevent Django setup | project/settings.py:47-53 |
| 07 | BLOCKER | Missing MEDIA_URL/MEDIA_ROOT/STATIC_ROOT referenced in urls.py | project/urls.py:11-13 |
| 08 | BLOCKER | No requirements.txt, pyproject.toml, lockfile, Procfile, railway.json or Dockerfile | GitHub repository tree |
| 09 | HIGH | No student-facing HTML/CSS/JS frontend; mobile compatibility cannot be demonstrated | GitHub repository tree |
| 10 | HIGH | ALLOWED_HOSTS=[] disallows Railway hostname; no public domain config | project/settings.py:28 |
| 11 | HIGH | SQLite used as database; Railway app filesystem is ephemeral without mounted storage | project/settings.py:106-111 |
| 12 | HIGH | Public document API can read/update uploaded files | apps/students/views.py:68-89 |
| 13 | HIGH | Document uploads lack type, size and persistent private-storage policy | apps/students/models.py:52-59 |
| 14 | HIGH | No spam prevention, CAPTCHA or request throttling for applicant intake | project/settings.py, apps/students/views.py |
| 15 | HIGH | Quota count and approval update not transactional or serialized; race possible | apps/students/views.py:46-57 |
| 16 | HIGH | Original form has no consent trail or privacy policy | models.py:20-40; repository tree |
| 17 | MEDIUM | Only duplicate JSHSHIR is validated, not 14-digit format or date | serializers.py:56-59 |
| 18 | MEDIUM | Production HTTPS, secure cookie and proxy settings absent | project/settings.py |
| 19 | MEDIUM | No automated tests, backup/migration plan or CI | repository tree |
| 20 | MEDIUM | No official school logo, actual directions list or student form | repository tree |

## New package changes

- Backend startup settings fixed, missing modules removed, dependencies added
- Django SECRET_KEY and DB credentials sourced from environment, DEBUG disabled by default
- Private application list, statistics, changes and documents guarded by Django permissions
- Public create-only endpoint retains original API path with consent requirement
- Approve action uses transaction + select_for_update to serialize quota checks
- Input validation and upload signature/size checks added
- Consent timestamp stored in new migration 0002
- Mobile-first HTML application form, responsive CSS, protected file downloads
- PostgreSQL, Gunicorn, WhiteNoise, Railway health check, static assets and deployment config
- Local SQLite DB file is intentionally omitted from the fixed archive

## Verified vs not verified

Verified on GitHub Actions (2026-11-22):
- Dependency installation and pip check
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py collectstatic --noinput`
- Nine automated Django API/form/security tests
- Python AST/compileall validation in the development environment
- Static Chrome prototype checked for horizontal overflow at 320, 375, 390, 768, 1024 and 1366 px

Not verified:
- Live Railway deployment (Railway free-plan resource limit blocks project creation)
- Real device and hardware-browser behavior
- Production PostgreSQL and private document backup/restore
- Load tests, independent security testing and institutional/legal approval

The public form and API are CLOSED by default in production (ADMISSIONS_OPEN=0).

## Release gate

Do not open public admissions until the institution approves the privacy policy,
actual school name/directions/contact details, PostgreSQL setup, staff workflow,
backup/restore and anti-abuse controls. The repository originally committed an
SQLite database and a hardcoded Django secret key; removing the SQLite file from
the current branch does NOT remove old Git history. Review potential disclosure
and rotate any production credentials before live use.

GitHub: security changes have been committed to audit/secure-admissions-20261122.
Railway: creation attempted, blocked by free plan resource provisioning limit.
