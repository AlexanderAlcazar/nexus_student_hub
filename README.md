# Nexus Student Hub

Backend foundation for a future client-server student hub with a GUI.

## Current focus

The project is currently centered on authentication, normalized user data, and profile completion:

- SQLite-backed user storage
- password hashing and login verification
- shared user profile composition
- profile completion for personal details and contact info
- student major persistence
- separate student and administrator role records
- dependency injection via a simple application container

## What is implemented

- `AuthService` for register/login flows and profile completion
- `ProfileService` for completing a user profile after account creation
- `UserRepository` for user and profile table access
- `Database` wrapper for SQLite connections and schema loading
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

## Architecture

The codebase is organized as a small backend-first application:

- `src/database/` for persistence and schema
- `src/repositories/` for database access
- `src/services/` for business logic and profile workflows
- `src/models/` for domain data objects
- `src/container.py` for dependency wiring

The current backend is designed to stay stateless so it can later support multiple users and request handling safely.

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
│   └── services/
│       ├── auth_service.py
│       └── profile_service.py
├── tests/
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
├── README.md
└── .gitignore
```

## Running tests

The project expects `src` on `PYTHONPATH`:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Roadmap

- add server request handling
- add client UI scaffolding
- add session/token handling
- expand repositories for student and administrator workflows
- add profile editing APIs and validation rules
- replace SQLite with a server-grade database if concurrency demands grow
