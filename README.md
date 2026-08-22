# Nexus Student Hub

Backend foundation for a future client-server student hub with a GUI.

## Current focus

The project is currently centered on authentication and data modeling:

- SQLite-backed user storage
- password hashing and login verification
- shared user profile composition
- separate student and administrator role records
- dependency injection via a simple application container

## What is implemented

- `AuthService` for register/login flows
- `UserRepository` for users table access
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

## Architecture

The codebase is organized as a small backend-first application:

- `src/database/` for persistence and schema
- `src/repositories/` for database access
- `src/services/` for business logic
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
│       └── auth_service.py
├── tests/
└── README.md
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
- replace SQLite with a server-grade database if concurrency demands grow
