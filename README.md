# Texnikum admission - reviewed MVP

This package is a security-focused replacement for the Django code in
`inurmuhammad872-pixel/texnikum-admission`. It adds a mobile-first application
form and retains the original database schema via migration `0001_initial.py`.
It intentionally **does not include the publicly committed SQLite database**.

See `AUDIT_UZ.md` for the original source audit and test evidence.

## What's included

- Mobile-friendly, accessible HTML application form, confirmation page and privacy notice
- Public read-only directions API and public create-only application API
- Django-admin-backed review, approve/reject, quota enforcement and document controls
- Staff permissions for all application data and actions
- JSHSHIR/phone input validation, consent timestamp, best-effort rate limiting
- Railway configuration, PostgreSQL support, static files, health check, tests

## Important launch blockers

The public application form and API are CLOSED by default in production. Once the institution has approved the privacy policy, real courses, the security/anti-abuse controls and staff acceptance testing, set ADMISSIONS_OPEN=1 to start collecting applications.


1. Replace the temporary privacy notice with the institution's approved policy,
   including controller, legal basis, contact details, retention and data rights.
2. Verify you have a legal basis for collecting JSHSHIR and applicants' data,
   particularly where applicants may be minors. Avoid collecting unnecessary data.
3. Add the real institute name, logo, contacts, and the list of actual directions.
4. Set up shared Redis rate limits and CAPTCHA or equivalent anti-abuse controls.
5. Set up a private persistent file store / Railway volume, test restore and backups
   **before** accepting document attachments. The public form does not accept files.
6. If the original `db.sqlite3` has real data, treat that as potential public exposure:
   assess impact, secure affected records, remove from current repo **and git history**,
   and follow the relevant incident/privacy process. `.gitignore` alone is not enough.
7. Rotate any secrets ever committed to Git history. The original hardcoded
   Django SECRET_KEY is compromised; do not reuse it.
8. Run dependency vulnerability scanning and a manual acceptance test with real
   school staff before official launch.

## Local development

Use Python 3.12 or 3.13:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DEBUG=1
export DJANGO_SECRET_KEY='development-only'
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

Admin: `/admin/`. Add real Directions in Django admin before accepting applications.
Public form: `/`. Health check: `/healthz/`.

## Deploy to Railway (after pushing patched source to an authorized repo)

1. Create a separate Railway project `texnikum-admission` and add **PostgreSQL**.
2. Create an app service connected to the GitHub repository containing this
   patched package on branch `main`.
3. Set app variables:
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (Railway service reference)
   - `DJANGO_SECRET_KEY=<new random long secret>`
   - `DEBUG=0`
   - `ALLOWED_HOSTS=<exact generated railway domain>`
   - `CSRF_TRUSTED_ORIGINS=https://<exact generated railway domain>`
4. `railway.json` configures `collectstatic`, `migrate`, Gunicorn, and health checks.
   Confirm the Railway builder uses the repository root (where `requirements.txt` is).
5. Generate a public domain only when the app's security and privacy prerequisites
   are accepted. Confirm HTTPS, `/healthz/`, `/`, `/admin/` and mobile layout.
6. Create the first superuser using Railway's secure shell/one-time command,
   then add real Directions. Do not commit admin passwords or seed fake applicants.
7. To store document uploads persistently, mount a Railway volume at `/app/media`,
   set `MEDIA_ROOT=/app/media`, enable tested backups, and plan for persistent
   object storage if the app later needs multiple instances.

## API routes

- `GET /api/v1/directions/`: available to public (active directions only)
- `POST /api/v1/students/`: public application submission (requires `consent: true`)
- `GET /api/v1/students/`: admissions staff with `students.view_student` only
- `GET /api/v1/students/statistics/`: admissions staff with view permission only
- `POST /api/v1/students/<uuid>/approve/`: staff with change permission
- `POST /api/v1/students/<uuid>/reject/`: staff with change permission
- `GET|POST /api/v1/students/<uuid>/documents/`: staff with document permission

For the API create call, POST JSON keys: `fio`, `jshshir` (14 digits),
`phone`, `email`, `birth_date` (YYYY-MM-DD), `address`, `direction` (UUID), `consent`.

## Notes

- The original repository had no front end, no requirements, no deploy settings,
  missing apps in `INSTALLED_APPS`, undefined MEDIA settings, hard-coded DEBUG and
  SECRET_KEY, public student read/write actions, and committed SQLite data.
- The student status API is intentionally limited to dedicated actions. Admin
  can edit records in Django admin with appropriate permissions.
- Local memory rate limiting is a minimal defense, not strong production protection.
- There is no automatic import of the original repository's SQLite data.
