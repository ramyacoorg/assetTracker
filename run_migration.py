import logging
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env if present

from sqlalchemy import text
from database import engine

logging.basicConfig(level=logging.INFO)

migration_sql = """
ALTER TABLE assets ADD COLUMN IF NOT EXISTS purchase_date TIMESTAMP;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS qr_code VARCHAR(500);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS qr_value VARCHAR(100);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS last_service_date DATE;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS repair_count INTEGER DEFAULT 0;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS last_used_date DATE;
ALTER TABLE assets DROP CONSTRAINT IF EXISTS assets_qr_value_key;
ALTER TABLE assets ADD CONSTRAINT assets_qr_value_key UNIQUE (qr_value);

-- Core tables and seeding
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE
);

-- Seed Roles
INSERT INTO roles (id, role_name) VALUES (1, 'admin'), (2, 'employee') ON CONFLICT (id) DO NOTHING;

-- Seed Permissions
INSERT INTO permissions (permission_name) VALUES 
('add:asset'), ('edit:asset'), ('delete:asset'), ('view:reports'), ('manage:users') 
ON CONFLICT (permission_name) DO NOTHING;

-- Admin gets all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    asset_id INTEGER REFERENCES assets(id),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exit_checklists (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES users(id) NOT NULL,
    asset_id INTEGER REFERENCES assets(id) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending'
);
"""

with engine.connect() as conn:
    conn.execute(text(migration_sql))
    conn.commit()
    logging.info("Successfully ran Assentra schema migrations.")
