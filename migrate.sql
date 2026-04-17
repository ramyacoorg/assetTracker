-- ============================================================
-- OptiAsset Database Migration Script
-- Run this in Supabase SQL Editor (or any Postgres client)
-- Safe to run multiple times — uses IF NOT EXISTS guards
-- ============================================================

-- 1. Add photo_url to users table
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500);

-- 2. Add photo_url to asset_issues table
ALTER TABLE asset_issues
  ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500);

-- 3. Verify roles exist (role_id 1 = admin, role_id 2 = employee)
--    Run this SELECT to check — if empty, insert the rows below
SELECT id, role_name FROM roles;

-- If roles table is empty, uncomment and run:
-- INSERT INTO roles (id, role_name) VALUES (1, 'admin'), (2, 'employee')
-- ON CONFLICT (id) DO NOTHING;

-- 4. Verify permissions exist for RBAC (add:asset, edit:asset, delete:asset)
SELECT id, permission_name FROM permissions;

-- If permissions are missing, uncomment:
-- INSERT INTO permissions (permission_name) VALUES
--   ('add:asset'), ('edit:asset'), ('delete:asset'),
--   ('view:reports'), ('manage:users')
-- ON CONFLICT (permission_name) DO NOTHING;

-- 5. Verify role_permissions (admin gets all permissions)
SELECT rp.id, r.role_name, p.permission_name
FROM role_permissions rp
JOIN roles r ON r.id = rp.role_id
JOIN permissions p ON p.id = rp.permission_id;

-- If role_permissions is empty for admin (role_id=1), uncomment:
-- INSERT INTO role_permissions (role_id, permission_id)
-- SELECT 1, id FROM permissions
-- ON CONFLICT DO NOTHING;

-- ============================================================
-- Done! All schema changes applied.
-- ============================================================
