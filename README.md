# Nexus Student Hub (In Progress)

An actively developing, distributed full-stack student management platform. This project represents a modern rewrite and architectural migration from a previous Java implementation into a streamlined Python ecosystem, introducing a centralized TCP socket server, a persistent SQLite database layer, and a desktop graphical user interface.

---

## Current Project Status & Roadmap

The project is currently transitioning through its foundational phases. The core architecture is being decoupled into separate, specialized modules to guarantee a clean separation of concerns:

- [ ] **Core Models (Phase 1):** Implementing abstract user definitions, student profiles, and administrative privilege roles.
- [ ] **Database Engine (Phase 2):** Developing a persistent storage layer utilizing SQLite with dynamic structural relational tables, safe data concurrency, and automated unique student ID assignment.
- [ ] **Server Backend (Phase 3):** Building a robust, custom TCP socket server that listens for incoming client connections and routes incoming data packets based on a custom string-delimited protocol.
- [ ] **Desktop Client Portal (Phase 4):** Designing a custom graphical user interface (GUI) to completely abstract network and database execution from users, providing role-based security access controls for admins and students.

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
│   ├── models/        # [In Progress] Abstract user definitions, student profiles, and administrative roles
│   ├── database/      # [Planned] SQLite engine setups, connection handles, and core schemas
│   ├── server/        # [Planned] Custom socket processing hooks and client command routers
│   └── client/        # [Planned] Network communication abstraction layers and the desktop UI
│
├── requirements.txt   # Third-party application requirements (e.g., PyQt6)
└── README.md          # Technical overview documentation