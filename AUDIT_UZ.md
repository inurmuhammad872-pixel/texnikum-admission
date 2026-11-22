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

Verified:
- All generated Python files compile via Python's AST parser
- railway.json parses as JSON
- Chrome mobile/desktop prototype checked at widths 320, 375, 390, 768, 1024, 1366 px;
  no horizontal overflow in prototype at any of these widths
- Form button at least 50 px tall in tested layouts

Not verified:
- Full Django `manage.py check`, migrations, API and web flow integration tests
  (required Django packages unavailable in this execution environment)
- Actual production Railway deployment: upstream GitHub connection is read-only
- Real phone hardware/browser behavior and actual database persistence
- Private uploads, backup/restore, penetration testing and legal compliance

## Release gate

DO NOT open public admissions while the privacy notice is still a placeholder,
or without a properly configured Postgres database, admin account, actual study
directions, tested backups, anti-bot controls and a complete live-flow test.

GitHub access: connected account can read, but not push to source repository.
For next step, authorize write access to the current connected GitHub account,
or commit this package to a writable repository and connect that repo to Railway.
