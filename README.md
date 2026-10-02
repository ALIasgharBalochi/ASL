# ASL — Ask, Share, Listen

ASL is a Django/DRF backend for building and submitting forms, with authentication, OTP-based registration and password recovery, Google OAuth, reporting, caching, Celery background jobs, and real-time reporting over WebSocket.

## Features

- Custom Django user with unique email
- JWT authentication with access/refresh tokens
- JWT logout through token blacklisting
- Google OAuth with django-allauth and PKCE
- Email verification during registration
- OTP regeneration and brute-force protection for OTP verification
- Password reset through email OTP
- Form/process/category management through DRF ViewSets
- Public/private forms and password-protected forms
- Free and linear form flows
- Anonymous submissions through a session UUID
- Question types: `text`, `number`, `select`, `checkbox`
- Transactional answer submission with `bulk_create`
- Per-form and per-process reporting
- Weekly/monthly reporting
- Cached reporting endpoints
- Periodic report emails with Celery Beat
- Real-time form statistics with Django Channels + Redis
- Swagger/OpenAPI and ReDoc
- Docker Compose setup with Redis, PostgreSQL, Celery, Daphne, and Nginx

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Framework | Django 6.1.1 |
| API | Django REST Framework 3.18.1 |
| Authentication | Simple JWT + Basic Authentication |
| OAuth | django-allauth + Google |
| Async / WebSocket | Django Channels 4.3.2 |
| ASGI server | Daphne |
| Cache / Channel Layer | Redis + django-redis + channels-redis |
| Background jobs | Celery + Celery Beat |
| Database | SQLite in current `dev` settings; PostgreSQL service is provided by Compose |
| API schema | drf-spectacular |
| Reverse proxy | Nginx |
| Containers | Docker / Docker Compose |

## Architecture

```text
                         ┌───────────────┐
                         │    Client     │
                         └───────┬───────┘
                                 │
                    HTTP / HTTPS │ WebSocket
                                 │
                         ┌───────▼───────┐
                         │     Nginx     │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │    Daphne     │
                         │  Django ASGI  │
                         └───┬─────┬─────┘
                             │     │
              ┌──────────────┘     └────────────────┐
              │                                      │
       ┌──────▼──────┐                        ┌──────▼──────┐
       │ PostgreSQL  │                        │    Redis    │
       └─────────────┘                        └──┬────┬─────┘
                                                 │    │
                                          ┌──────▼┐  ┌▼────────────┐
                                          │Celery │  │Channels     │
                                          │Worker │  │WebSocket    │
                                          └───────┘  └─────────────┘
```

> Current repository behavior: `core.settings.dev` uses SQLite, while `compose.yaml` also provisions a PostgreSQL container. PostgreSQL is therefore infrastructure provided by Compose, but it is not the database used by the current development settings.

## Project Structure

```text
ASL/
├── apps/
│   ├── accounts/
│   │   ├── api/
│   │   │   ├── serializers/
│   │   │   ├── views/
│   │   │   └── urls.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   └── services.py
│   │
│   ├── forms/
│   │   ├── api/
│   │   │   ├── serializers/
│   │   │   ├── views/
│   │   │   └── urls.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   └── services.py
│   │
│   └── reports/
│       ├── api/
│       │   ├── views/
│       │   └── urls.py
│       ├── consumers.py
│       ├── routing.py
│       ├── services.py
│       └── tasks.py
│
├── common/
│   └── utils/
│       ├── generate_otp.py
│       └── notification.py
│
├── core/
│   ├── settings/
│   │   ├── settings.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
│
├── nginx/
│   ├── nginx.conf
│   └── ssl/
│
├── documents/
├── staticfiles/
├── .github/
│   └── workflows/
├── Dockerfile
├── compose.yaml
├── compose.debug.yaml
├── requirements.txt
├── manage.py
└── .env.example
```

## Core Domain

### Accounts

`apps.accounts` owns authentication and account lifecycle.

The registration flow does not immediately create a database user. Registration data and the OTP are temporarily stored in Redis. The user is created only after successful OTP verification.

Registration data lifetime:

- Registration data: 10 minutes
- OTP: 2 minutes
- OTP verification attempts: maximum 5 attempts within 5 minutes

The password is hashed before being stored in Redis.

Password reset uses a separate temporary `finder_id` flow:

```text
Request reset
    ↓
Generate finder_id + OTP
    ↓
Store reset data in Redis
    ↓
Send OTP by email
    ↓
Verify OTP
    ↓
Create short-lived "verified" state
    ↓
Change password
    ↓
Delete temporary Redis state
```

### Forms

The form domain contains:

```text
Category
   │
   ├── Process
   │      │
   │      └── Form
   │             │
   │             └── Question
   │                    │
   │                    └── QuestionOption
   │
   └── Form
```

Submission data is represented as:

```text
Submission
   │
   └── Answer
          │
          └── AnswerOption
```

Supported question types:

- `text`
- `number`
- `select`
- `checkbox`

The submission serializer validates the relationship between question type, value, and selected options before data is persisted.

### Linear Forms

A process can be:

- `free`
- `liner` (the current model choice name)

For a linear process, a user/session must submit the previous form before accessing the next form.

Anonymous users receive a UUID stored in the Django session. This UUID is used to associate anonymous submissions with the linear flow.

## Reporting

The reporting service provides:

### Form report

For numeric questions:

- count
- sum
- average
- minimum
- maximum

For select/checkbox questions:

- option value
- option ID
- answer count

### Process report

Aggregates:

- total views
- total submissions
- individual form reports

### Period report

Supported periods:

- `weekly`
- `monthly`

The period boundaries are normalized to five-minute intervals.

### Real-time report

A WebSocket consumer subscribes clients to a form-specific channel group:

```text
ws/reporting/forms/<form_uuid>/
```

When a submission is committed, the application sends an update to the form's WebSocket group.

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000
```

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/accounts/api/login/` | Obtain JWT access/refresh tokens |
| POST | `/accounts/api/refresh/token/` | Refresh access token |
| POST | `/accounts/api/logout/` | Blacklist refresh token |
| POST | `/accounts/api/registration/` | Start registration |
| POST | `/accounts/api/verify_otp/` | Verify registration OTP |
| POST | `/accounts/api/regenerate_otp/` | Regenerate expired OTP |
| GET | `/accounts/api/google/jwt/` | Return JWT after Google authentication |
| POST | `/accounts/api/reset-password/` | Start password reset |
| POST | `/accounts/api/reset-password/verify/` | Verify reset OTP |
| POST | `/accounts/api/reset-password/change/` | Change password |

### Forms

The forms API uses DRF routers.

| Method(s) | Endpoint | Purpose |
|---|---|---|
| CRUD | `/forms/api/categories/` | Manage categories |
| CRUD | `/forms/api/processes/` | Manage processes |
| CRUD | `/forms/api/forms/` | Manage forms |
| CRUD | `/forms/api/questions/` | Manage questions |
| CRUD | `/forms/api/question-options/` | Manage question options |
| POST | `/forms/api/submit_answer/` | Submit answers |

Additional actions:

```text
POST /forms/api/processes/<id>/unlock/
POST /forms/api/forms/<uuid>/unlock/
```

### Reports

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/reports/api/<form_uuid>/reports` | Form report |
| GET | `/reports/api/processes/<process_id>/report/` | Process report |
| GET | `/reports/api/period/report/?period=weekly` | Weekly admin report |
| GET | `/reports/api/period/report/?period=monthly` | Monthly admin report |

The period report requires an admin user.

### Documentation

```text
GET /api/schema/
GET /api/docs/
GET /api/redoc/
```

## WebSocket API

Connect to:

```text
ws://127.0.0.1:8000/ws/reporting/forms/<form_uuid>/
```

When reporting data changes, the server sends JSON similar to:

```json
{
  "type": "report.update",
  "data": {
    "total_submissions": 10,
    "total_views": 42
  }
}
```

For production behind Nginx/HTTPS, use:

```text
wss://your-domain/ws/reporting/forms/<form_uuid>/
```

## Environment Variables

Start from `.env.example`.

Required core variables:

```env
GOOGLE_CLIENT_ID=google_client_id
GOOGLE_CLIENT_SECRET=google_client_secret
DJANGO_SECRET_KEY=django_secret_key

DB_NAME=name
DB_USER=user
DB_PASSWORD=password
```

For SMTP email delivery, the current development settings also read:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_APP_PASSWORD=your-app-password
```

For periodic report delivery:

```env
REPORT_EMAIL_TO=recipient@example.com
```

Never commit real secrets, passwords, OAuth credentials, or email app passwords.

## Installation — Local Development

### 1. Clone the repository

```bash
git clone https://github.com/ALIasgharBalochi/ASL.git
cd ASL
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and provide your actual secret, database, Google OAuth, and SMTP values.

### 5. Start Redis

If Redis is installed locally:

```bash
redis-server
```

The development settings expect Redis at:

```text
redis://redis:6379/0
```

When running Django directly on the host, change the Redis hostname to `127.0.0.1` in your local configuration, or run the application inside the Compose network.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create an admin user

```bash
python manage.py createsuperuser
```

### 8. Run the ASGI application

For HTTP + WebSocket support:

```bash
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

Or during simple development:

```bash
python manage.py runserver
```

When using WebSockets, prefer Daphne/ASGI.

## Installation — Docker Compose

The main Compose file defines:

- `web`
- `db`
- `redis`
- `celery_worker`
- `celery_beat`
- `nginx`

### 1. Prepare environment files

```bash
cp .env.example .env
cp .env.example .env.docker
```

Set the required database and application variables.

### 2. Build the application image

```bash
docker compose build
```

### 3. Run the application

For the Django/Daphne stack without Nginx:

```bash
docker compose up web redis celery_worker celery_beat db
```

The API is then available at:

```text
http://127.0.0.1:8000
```

### 4. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Collect static files

```bash
docker compose exec web python manage.py collectstatic --noinput
```

### 7. Stop services

```bash
docker compose down
```

To remove the PostgreSQL volume as well:

```bash
docker compose down -v
```

> `docker compose down -v` deletes the database volume. Use it only when you intentionally want to reset persisted PostgreSQL data.

## Nginx + HTTPS

The Compose configuration includes Nginx and expects:

```text
nginx/
└── ssl/
    ├── origin.crt
    └── origin.key
```

The current Nginx configuration:

- redirects HTTP to HTTPS
- serves `/static/` from `staticfiles`
- proxies application traffic to `web:8000`

If the SSL files are not present, run the application without the Nginx service during local development.

## Celery

Celery uses Redis as its broker.

Worker:

```bash
celery -A core worker --loglevel=info --pool=solo
```

Beat:

```bash
celery -A core.celery beat --loglevel=info
```

Compose starts both services automatically.

Two periodic tasks are configured:

- Weekly report — Monday at 09:00
- Monthly report — first day of the month at 09:00

The report task sends the generated summary by email.

## Caching

Django's cache backend uses `django-redis`.

Reporting endpoints use Django's `cache_page` decorator for short-lived response caching.

Redis is also used independently for:

- temporary registration data
- OTP storage
- OTP attempt counters
- password-reset state
- Django cache
- Channels channel layer

## Authentication Flow

### JWT

```text
Login
  ↓
Access Token + Refresh Token
  ↓
Authenticated API requests
  ↓
Refresh when access token expires
  ↓
Blacklist refresh token on logout
```

### Registration

```text
POST /registration/
       ↓
Validate user data
       ↓
Generate registration UUID + OTP
       ↓
Store temporary data in Redis
       ↓
Send OTP email
       ↓
POST /verify_otp/
       ↓
Create database user
```

## Security Considerations

The project already applies several security mechanisms:

- Password hashing with Django's password hashing utilities
- Temporary registration data stored in Redis rather than the database
- OTP expiration
- OTP attempt limiting
- JWT authentication
- Refresh-token blacklisting
- Password-protected forms/processes use hashed passwords
- CSRF middleware enabled
- HTTPS termination through Nginx
- Secrets loaded from environment variables
- Docker image runs the application as a non-root user

Before production deployment, review:

- `DEBUG`
- `ALLOWED_HOSTS`
- database configuration
- Redis access
- HTTPS certificates
- OAuth redirect URLs
- SMTP credentials
- CORS/CSRF trusted origins
- secure cookie settings
- proxy/security headers
- production database host configuration

## API Workflow Example

A typical form lifecycle is:

```text
1. Create Category
        ↓
2. Create Process
        ↓
3. Create Form
        ↓
4. Create Questions
        ↓
5. Add Question Options where required
        ↓
6. Share Form
        ↓
7. User submits answers
        ↓
8. Submission + Answers are stored atomically
        ↓
9. Reporting data is updated
        ↓
10. WebSocket clients receive real-time statistics
```

## Database Model Overview

```text
CustomUser
   │
   ├── Category
   │      ├── Process
   │      │      └── Form
   │      │             └── Question
   │      │                    └── QuestionOption
   │      │
   │      └── Form
   │
   └── Submission
            └── Answer
                   └── AnswerOption
```

## Testing

Run Django's test runner with:

```bash
python manage.py test
```

Inside Docker:

```bash
docker compose exec web python manage.py test
```

## Debugging with Docker

The repository includes a dedicated debug Compose file exposing port `5678` for `debugpy`.

```bash
docker compose -f compose.debug.yaml up --build
```

The debug service runs Django with:

```text
0.0.0.0:8000
```

and waits for a debugger connection on:

```text
0.0.0.0:5678
```

## Useful Management Commands

```bash
# Check project configuration
python manage.py check

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

Docker equivalents:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell
```

## License

This project is released under the MIT License. See `LICENSE` for details.
