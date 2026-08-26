-- ============================================================================
-- Project: Nexus Student Hub
-- Scope: Lean MVP Production Schema
-- Focus: Clean Object Composition & Dual-UI Interface Mapping
-- ============================================================================

-- Force SQLite to actively enforce relational constraints and cascading wipes
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. CENTRAL IDENTITY LAYER
-- ----------------------------------------------------------------------------
-- This table handles network identity and acts as the TCP server's traffic router.
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL, -- Stored securely as binary bytes
    user_type TEXT NOT NULL CHECK(user_type IN ('student', 'administrator')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. COMPOSITION DATA COMPONENTS (Strict 1:1 Relationships)
-- ----------------------------------------------------------------------------
-- Shared modular blocks that map directly to your Python component classes.
CREATE TABLE IF NOT EXISTS personal_details (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact_info (
    user_id INTEGER PRIMARY KEY,
    phone_number TEXT,
    street_address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 3. DOMAIN ROLE CORES (1:N Relationships)
-- ----------------------------------------------------------------------------
-- Isolated profile buckets used to determine dashboard privileges and layouts.
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    major TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS administrators (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4. AUTH SESSION LAYER
-- ----------------------------------------------------------------------------
-- Refresh-token sessions are stored hashed to support secure rotation/revocation.
CREATE TABLE IF NOT EXISTS auth_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    refresh_token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    replaced_by_session_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (replaced_by_session_id) REFERENCES auth_sessions(session_id) ON DELETE SET NULL
);