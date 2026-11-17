# Queensway Early Years — Flask School Website

A complete, responsive school marketing website with a private school-office dashboard. Built with Flask, SQLAlchemy, Jinja HTML templates, compiled Tailwind CSS, inline custom CSS and inline JavaScript.

The colour scheme is mustard yellow, deep green and near-black, with warm cream for readable content. The supplied Queensway banner is included unchanged, and its vision, mission, core values and tagline are used in the website.

## Included

- Home, Our School, Learning, three learning-stage pages, School Life, Gallery, Admissions, Book a Visit, Contact, Journal, article pages and Privacy.
- Database-backed admission enquiries, visit requests and contact messages, with unique confirmation references.
- Staff sign-in, enquiry search and filters, pagination, status updates, private notes and record deletion.
- Journal creation, drafts, publishing, editing and deletion.
- Mobile navigation, accessible gallery filters and photo lightbox, FAQ accordions and server-side form validation.
- Hashed staff passwords, CSRF protection, rate limits, honeypot, secure production cookies and security headers.
- SQLite for local use; PostgreSQL support and Alembic migrations for deployment.
- Locally stored photographs, fonts and CSS. No CDN is needed at runtime.
- Render configuration, tests and a static design-preview exporter.

## Run locally

Use Python 3.12 or later. Extract the ZIP, open a terminal inside `queensway-school`, then:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

macOS / Linux:

```bash
source .venv/bin/activate
cp .env.example .env
```

Install and initialise:

```bash
python -m pip install -r requirements.txt
flask --app app db upgrade
flask --app app seed-content
flask --app app create-admin
flask --app app run --debug
```

Open `http://127.0.0.1:5000`. Staff sign-in is at `/admin/login/`.

`create-admin` prompts for an email and a password privately. Use at least 12 characters. No default administrator or default password is included. Use `flask --app app reset-admin-password` to reset an existing administrator’s password.

`seed-content` adds three evergreen starter journal articles. It is safe to repeat and does not overwrite edited articles. The six supplied school photographs are included unchanged. No student, staff or parent records are preloaded.

`flask --app app init-db` is also available for simple local table creation. Prefer `db upgrade` for a new project so migration history stays tracked. If `init-db` was already used on this exact initial schema, use `flask --app app db stamp head` before future migrations; do not stamp an unknown or different schema.

## Configure school information

Edit `.env` locally, or set environment variables on your host:

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | `development` locally; `production` on the public server |
| `SECRET_KEY` | Unique random value, at least 32 characters in production |
| `DATABASE_URL` | SQLite locally or the PostgreSQL connection URL on your host |
| `REDIS_URL` | Redis URL for shared rate limits across production workers; `memory://` locally |
| `TRUSTED_PROXY_HOPS` | Verified number of trusted reverse proxies; default `0` |
| `SCHOOL_EMAIL` | Official school email |
| `SCHOOL_PHONE` | Official school telephone |
| `SCHOOL_ADDRESS` | School location / postal address |
| `SCHOOL_HOURS` | Confirmed office hours |

Generate a production secret locally:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Keep `.env`, database credentials and secrets out of Git. The development key is automatically generated into the ignored `instance` folder only when no key is configured. Production refuses to start without a suitable `SECRET_KEY`.

Blank contact settings are hidden, so the application never displays invented telephone numbers or addresses. There is no map until the actual school location is supplied.

The enquiry system saves submissions in the database for staff review. It does **not** send email or SMS automatically. Staff must review `/admin/` and respond using the submitted contact details. A visit request is not an appointment confirmation, and an admissions enquiry is not an offer of a place.

## Update content and images

| File | What to edit |
| --- | --- |
| `app.py` | Flask routes, configuration, security and CLI commands |
| `models.py` | Admin, enquiry and journal database models |
| `forms.py` | Form fields, choices and validation |
| `content.py` | Mission, vision, values, learning-stage descriptions and starter articles |
| `templates/base.html` | Header, footer, colours, inline CSS and shared inline JavaScript |
| `templates/index.html` | Homepage content and layout |
| `templates/about.html` | School information |
| `templates/admissions.html` | Admissions information and FAQ |
| `templates/admin/` | Private office dashboard and editing screens |
| `static/images/` | School banner, favicon and photographs |
| `static/fonts/` | Locally stored font files |

The three learning-stage names and descriptions are proposed editable content, not verified school programme information. Confirm them with the school before public launch. Age eligibility, fees, calendar dates, opening hours, staff identities, accreditations, testimonials and enrolment statistics have deliberately not been invented.

The six supplied school photographs are used throughout the website and gallery. Edit the `PHOTOS` mapping in `content.py` to change filenames, descriptions or crop positions. Existing journal image keys are preserved, so stored articles continue to work without a database migration. The crown wordmark is an editable site interpretation of the supplied branding; the original banner remains available on the About page.

The CSS is already compiled. **Node is not required to run Flask.** To regenerate Tailwind after adding or changing utility classes:

```bash
npm ci
npm run build:css
```

Custom styling stays inline in `base.html`, as requested. Page-specific and shared JavaScript also stay inline. The content security policy allows these inline scripts/styles; external assets and arbitrary object embeds are blocked.

## Deploy to Render

The included `render.yaml` defines the Flask web service. It requires your PostgreSQL connection, Redis connection and actual school contact details. Review Render’s selected compute plan before creating the service; the file does not provision a database or Redis automatically.

1. Upload the project to your own Git repository, excluding `.env`, `instance`, `.venv` and `node_modules`.
2. Create a PostgreSQL database and a Redis-compatible service, and use their connection URLs in the web-service environment.
3. Create a Python web service from the repository or import the Blueprint.
4. Use these commands:

| Setting | Value |
| --- | --- |
| Build | `pip install -r requirements.txt` |
| Pre-deploy | `flask --app app db upgrade` |
| Start | `gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
| Health check | `/health` |

5. Set `APP_ENV=production` and a strong `SECRET_KEY`. Configure `TRUSTED_PROXY_HOPS` only after verifying the proxy topology; trusting arbitrary forwarding headers can let clients spoof their address.
6. Run `flask --app app seed-content` and `flask --app app create-admin` in the service shell.
7. Open the deployed site, submit a test enquiry and verify it in the school office before directing families to the forms.

If your hosting plan does not support a pre-deploy command, initialise the production database with `flask --app app db upgrade` using your host’s shell or a controlled migration job before serving traffic. Use managed PostgreSQL for persistent data; do not rely on a transient local SQLite file on Render. Keep database backups and restrict administrator access.

The supplied Render configuration has been prepared, but no Render account has been connected and no Flask backend has been deployed to Render in this delivery.

Official deployment references: [Flask + Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/), [Render Flask guide](https://render.com/docs/deploy-flask), [Render Blueprint reference](https://render.com/docs/blueprint-spec).

## Database changes

After changing models in development:

```bash
flask --app app db migrate -m "Describe the schema change"
flask --app app db upgrade
```

Review generated migrations before deploying. Back up the production database before migrations. Do not run `db.create_all()` as a schema-update strategy for an existing database.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The included tests cover public routes, invalid inputs, persistence, confirmation references, hidden drafts, staff authentication and access control, enquiry review/deletion, article lifecycle, CSRF, security headers and production-secret requirements. SQLite is used in automated tests. PostgreSQL/Redis infrastructure and live email delivery are not included in those checks.

Desktop and a 390-pixel responsive layout were reviewed in a browser. Gallery filtering, the photo lightbox and mobile navigation were exercised. WTForms 3.3 emits a deprecation warning about tuple choices; the tested version is pinned. Update the choice declarations when upgrading to WTForms 3.4 or newer.

## Static visual preview

The separately hosted design preview is a static export, not a Python server. The top design-preview banner has been removed. Its forms retain a local availability note and a submission message, and send/store no enquiries; staff sign-in is demonstrative. The downloadable Flask application implements the actual backend.

To export the preview again:

```bash
python -m pip install -r requirements-dev.txt
python scripts/export_preview.py ./preview
```

Serve the generated folder with a static web server from its root. Do not double-click an HTML file: the pages use root-relative URLs. Run Flask for real form submissions and staff administration.

## Before the school launches

Confirm official contact information, programme labels, curriculum, admissions requirements and fee information. Have the school approve the site copy, its privacy wording and a retention/deletion policy that reflects the actual hosting and office practices. No payment handling, parent accounts, fee billing, attendance, examinations or learning-management system is included; this project is the public school website plus its enquiry and publishing office.

## Asset sources

The following original school photographs were supplied by the user and are included without pixel edits:

| File | School photograph |
| --- | --- |
| `our-school-community.jpg` | Class group outside school |
| `queensway-learner.jpg` | Learner in green and mustard yellow uniform |
| `playground-friends.jpg` | Pupils beside the playground |
| `outdoor-discovery.jpg` | Children and adults enjoying a wooded outdoor space |
| `learning-through-play.jpg` | Two pupils exploring and balancing outside |
| `queensway-campus.jpg` | School exterior |

The supplied photographs and branding are not relicensed by this project. All six photographs appear in the gallery; the lightbox preserves each complete image. Gallery thumbnails use their full proportions. Display crops elsewhere are controlled by CSS. The older `classroom.jpg`, `discover.jpg`, `create.jpg` and `together.jpg` URLs are retained as identical copies of the corresponding school photographs for compatibility; no stock photographs remain.

DM Sans and Lora are distributed under the SIL Open Font License. Their licence notices are included in `licenses/`. The source banner was supplied by the user and is not relicensed by this project.
