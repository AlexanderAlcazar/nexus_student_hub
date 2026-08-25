# Nexus Student Hub

Backend foundation for a future client-server student hub with a GUI.

## Current focus

The project is currently centered on authentication, normalized user data, profile completion, and a lightweight HTTP API layer:

- SQLite-backed user storage
- password hashing and login verification
- shared user profile composition
- profile completion for personal details and contact info
- student major persistence
- separate student and administrator role records
- dependency injection via a simple application container
- FastAPI-based HTTP endpoints for register/login/profile flows

## What is implemented

- `AuthService` for register/login flows and password verification
- `ProfileService` for completing a user profile after account creation
- `UserRepository` for user and profile table access
- `Database` wrapper for SQLite connections and schema loading
- `FastAPI` app in `src/server/app.py` exposing HTTP endpoints
- normalized schema with:
  - `users`
  - `personal_details`
  - `contact_info`
  - `students`
  - `administrators`
- reusable model components:
  - `Credentials`
  - `PersonalDetails`
  - `ContactInfo`
  - `UserBase`
  - `Student`
  - `Administrator`
- repository support for upserting profile data by `user_id`
- API routes for:
  - `GET /health`
  - `POST /register`
  - `POST /login`
  - `POST /profile/complete`
  - `GET /users/{user_id}`

## Architecture

The codebase is organized as a small backend-first application with a thin API layer on top:

- `src/database/` for persistence and schema
- `src/repositories/` for database access
- `src/services/` for business logic and profile workflows
- `src/models/` for domain data objects
- `src/container.py` for dependency wiring
- `src/server/` for HTTP request handling and API routes

The backend is intentionally stateless and service-oriented so it can later support multiple users, request handling, and client integrations safely.

## Project structure

```text
nexus_student_hub/
├── src/
│   ├── container.py
│   ├── database/
│   │   ├── database_manager.py
│   │   └── schema.sql
│   ├── models/
│   │   ├── credentials.py
│   │   ├── personal_details.py
│   │   ├── contact_info.py
│   │   ├── user_base.py
│   │   ├── student.py
│   │   └── administrator.py
│   ├── repositories/
│   │   └── user_repository.py
│   ├── server/
│   │   └── app.py
│   └── services/
│       ├── auth_service.py
│       └── profile_service.py
├── tests/
│   ├── test_api.py
│   ├── test_profile_completion.py
│   ├── test_container.py
│   ├── test_student.py
│   ├── test_administrator.py
│   ├── test_user_base.py
│   ├── test_personal_details.py
│   ├── test_contact_info.py
│   ├── test_credentials.py
│   └── test_database_manager.py
├── data/
├── assets/
├── requirements.txt
├── README.md
└── .gitignore
```

## Running the API

From the project root:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m uvicorn server.app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

## Running tests

The project expects `src` on `PYTHONPATH`:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Roadmap

- add session and JWT-based authentication
- add client UI scaffolding
- expand repositories for student and administrator workflows
- add profile editing APIs and validation rules
- add admin-only and role-based authorization checks
- replace SQLite with a server-grade database if concurrency demands grow
