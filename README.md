# NoteNest Users Service

FastAPI + MongoDB microservice that handles user registration, email verification, JWT login with refresh tokens, and profile management for NoteNest.

> **Status:** Archived learning project, not maintained.

## Features

- User registration with bcrypt password hashing and duplicate email/username checks
- Email verification via a UUID link sent over SMTP
- Login that requires a verified account and a `User-Agent` header; issues an access token and a refresh token (JWT)
- Per-device refresh token tracking (device type, OS and browser parsed from the `User-Agent`)
- Refresh token rotation: each refresh invalidates the previous refresh token
- Authenticated profile read, profile edit (username / full name) and email change (re-verification required)

API messages are in Spanish.

## Architecture

| Layer | Path | Responsibility |
| --- | --- | --- |
| Entry point | `app/main.py` | Creates the FastAPI app and mounts the routers under `/auth`, `/verification` and `/user` |
| Routers | `app/routers/` | HTTP endpoints, request validation and error-to-status mapping |
| Services | `app/services/` | Business logic: users, tokens/devices, verification email |
| Schemas | `app/schemas/` | Pydantic request/response models |
| Models | `app/models/` | Pydantic `User` model used for registration |
| Core | `app/core/` | Settings (`config.py`), password hashing and JWT helpers (`security.py`), custom exceptions |
| Database | `app/db/mongo.py` | Async MongoDB client (Motor) and the `users` collection |
| Tests | `app/tests/` | pytest + httpx async tests |

## Endpoints

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register` | - | Register a user (`username`, `full_name`, `email`, `password`) and send a verification email |
| POST | `/auth/login` | - | Log in with `email` and `password`; returns `access_token` and `refresh_token` |
| POST | `/auth/refresh-token` | Bearer refresh token | Rotate the refresh token and issue a new token pair |
| GET | `/verification/email/{verification_uuid}` | - | Mark the user's email as verified |
| GET | `/user/profile` | Bearer access token | Return `email`, `username` and `full_name` |
| PATCH | `/user/edit-profile` | Bearer access token | Update `username` and/or `full_name` |
| PATCH | `/user/change-email` | Bearer access token | Change the email, mark the account unverified and send a new verification email |

Interactive docs are available at `/docs` (FastAPI default) when the server is running.

Planned but not implemented endpoints are listed in [Roadmap.md](Roadmap.md) (in Spanish).

## Configuration

Settings are read from environment variables, loaded from `app/core/.env` via `python-dotenv` (see `app/core/config.py`).

| Variable | Notes |
| --- | --- |
| `ENVIRONMENT` | `des` (default), `pro` or `test` (`pytest.ini` sets `test`) |
| `MONGO_LOCAL` | MongoDB URI used when `ENVIRONMENT=des` |
| `DATABASE_PRO` | MongoDB URI used for any other environment, including `test` |
| `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_HOST`, `SMTP_PORT`, `EMAIL_FROM`, `EMAIL_FROM_NAME`, `FRONTEND_URL` | Used when `ENVIRONMENT=pro` |
| `SMTP_USERNAME_DES`, `SMTP_PASSWORD_DES`, `SMTP_HOST_DES`, `SMTP_PORT_DES`, `EMAIL_FROM_DES`, `EMAIL_FROM_NAME_DES`, `FRONTEND_URL_DES` | Used for any non-`pro` environment |
| `SECRET_KEY` | JWT signing key |
| `ALGORITHM` | JWT algorithm (for example `HS256`) |
| `ACCESS_TOKEN_EXPIRE_TIMES` | Token lifetime in hours |

The database name is `notenest`, or `test` when `ENVIRONMENT=test`. `SMTP_PORT*` and `ACCESS_TOKEN_EXPIRE_TIMES` must be set, since they are parsed as integers at startup.

## Running locally

Requires Python 3.10+ and a reachable MongoDB instance.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# create app/core/.env with the variables above
uvicorn app.main:app --reload
```

Run commands from the repository root, since the `.env` path is relative to it.

## Running tests

```bash
pytest
```

The tests are not fully isolated: they connect to the MongoDB at `DATABASE_PRO` (database `test`), and an autouse fixture deletes every document in its `users` collection before each test. Email sending is mocked.

## Known limitations

- `REFRESH_TOKEN_EXPIRE_TIMES` is read from `ACCESS_TOKEN_EXPIRE_TIMES`, so both tokens share the same lifetime.
- `/user/change-email` sends the verification email to the previous address, not the new one.
- SMTP connects with `use_tls=False`, and email send errors are only printed.
