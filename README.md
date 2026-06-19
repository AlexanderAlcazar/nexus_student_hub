# Nexus Student Hub (In Progress)

An actively developing, distributed full-stack student management platform. This project represents a modern rewrite and architectural migration from a previous Java implementation into a streamlined Python ecosystem, introducing a decoupled Model-View-Controller (MVC) architecture, a centralized TCP socket server, and a persistent SQLite database layer.

---

## Current Project Status & Roadmap

The project is currently transitioning through its foundational phases. The core architecture has been organized into modular layers to strictly separate data, user interfaces, and business logic:

- [ ] **Phase 1: Core Models & Shared Data Layer:** Implementing abstract user schemas, student profiles, and administrative privilege roles.
- [ ] **Phase 2: Database Infrastructure:** Structuring a persistent storage layer utilizing SQLite with dynamic relational tables and auto-incrementing system IDs.
- [ ] **Phase 3: Server-Side Controllers & Sockets:** Building a custom TCP socket listener paired with server controllers to route incoming network packets and safely execute database queries.
- [ ] **Phase 4: Client-Side Views & Controllers:** Designing a desktop graphical user interface (GUI) via PyQt6/CustomTkinter that leverages view-controllers to cleanly abstract all network requests away from the user.

---

## Technical Architecture (MVC Design Pattern)

To guarantee a professional separation of concerns, the repository follows a strict architectural pipeline:
- **Model (M):** Pure data frameworks that govern entity definitions (`User`, `Student`, `Admin`) without any knowledge of network sockets or user interfaces.
- **View (V):** Desktop layout view scripts responsible solely for rendering UI elements (buttons, windows, tables) and reporting client-side click events.
- **Controller (C):** The operational brain divided across the network stream. Client controllers intercept UI interactions to communicate with the server, while server controllers process backend business logic and query the SQLite layer.

---

## Technical Overview

Once fully implemented, the platform will support:
- **User Authentication:** Isolated validation pathways distinguishing between administrative privilege configurations and read-only student system states.
- **Academic Record Tracking:** Complete CRUD capabilities (Create, Read, Update, Delete) allowing administrators to inject new records, remove students by system IDs, or pull structural student rosters.
- **Data Serialization:** Automatic, corruption-free binary serialization directly onto disk storage via SQLite.
- **Relational Domain Integrity:** Integrated structural boundaries to prevent desynchronized data states across multi-user environments.

---

## Project Structure

```text
nexus_student_hub/
│
├── src/
│   ├── models/              # [In Progress] Pure data frameworks (User, Student, Admin blueprints)
│   ├── database/            # [Planned] SQLite engine setups, connection handles, and schemas
│   │
│   ├── server/              # Server-Side Backend Ecosystem
│   │   ├── controllers/     # Backend business logic routers (Auth, CRUD processing)
│   │   └── main.py          # TCP server socket listener entry point
│   │
│   └── client/              # Client-Side Frontend Ecosystem
│       ├── controllers/     # View-controllers bridging GUI clicks to network channels
│       ├── views/           # Graphical user interface layouts and widgets
│       └── main.py          # Desktop application bootstrap entry point
│
├── requirements.txt         # Third-party application requirements (e.g., PyQt6)
└── README.md                # Technical overview documentation