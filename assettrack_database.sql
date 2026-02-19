1. departments (
   id,
   department_name,
   created_at
)

2. employees (
   id,
   employee_code,
   full_name,
   email,
   phone_number,
   department_id,
   joining_date,
   status,
   created_at
)

3. users (
   id,
   employee_id,
   username,
   password_hash,
   role,
   is_active,
   created_at
)

4. assets (
   id,
   asset_code,
   asset_name,
   asset_category,
   asset_status,
   purchase_date,
   created_at
)

5. asset_assignments (
   id,
   asset_id,
   employee_id,
   assigned_date,
   return_date,
   status,
   created_at
)

6. asset_issues (
   id,
   asset_id,
   employee_id,
   issue_description,
   issue_status,
   reported_at
)

7. asset_requests (
   id,
   employee_id,
   asset_category,
   reason,
   request_status,
   requested_at,
   reviewed_at
)

8. asset_contracts (
   id,
   asset_id,
   contract_type,
   start_date,
   expiry_date,
   created_at
)

9. notifications (
   id,
   user_id,
   notification_type,
   message,
   is_read,
   created_at
)
