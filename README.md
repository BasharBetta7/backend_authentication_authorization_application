# Authentication & Authorization Backend

## Description
This project is a FastAPI+SQLalchemy backend that implements:
- JWT-based authentication (`access token` + `refresh token`)
- RBAC authorization using `roles`, `permissions`, `user_roles`, and `role_permissions`
- CRUD APIs for users and authorization objects (roles, resources, actions, permissions)
- Mock APIs (`roles`,`permissions`, `events`) to demonstrate permission checks

Permissions are represented as:
`resource:action:scope`

Example:
`users:read:own`


## Tables
- `users`
  - Stores account identity and status.
  - Key fields: `id`, `first_name`, `last_name`, `email` (unique), `password`, `is_active`.

- `roles`
  - Stores role definitions.
  - Key fields: `id`, `name` (unique), `description`.

- `user_roles`
  - Many-to-many mapping between users and roles.
  - Key fields: `user_id` (FK -> `users.id`), `role_id` (FK -> `roles.id`).
  - Composite uniqueness by `(user_id, role_id)`.

- `resources`
  - Stores protected resource names used in permission triplets.
  - Key fields: `id`, `name` (unique), `description`.

- `actions`
  - Stores allowed operations used in permission triplets.
  - Key fields: `id`, `name` (unique), `description`.

- `permissions`
  - Stores `resource + action + scope` combinations.
  - Key fields: `id`, `resource_id` (FK -> `resources.id`), `action_id` (FK -> `actions.id`), `scope` (`own`/`any`).
  - Unique constraint on `(resource_id, action_id, scope)`.

- `role_permissions`
  - Many-to-many mapping between roles and permissions.
  - Key fields: `id`, `role_id` (FK -> `roles.id`), `permission_id` (FK -> `permissions.id`).
  - Unique constraint on `(role_id, permission_id)`.

- `refresh_tokens`
  - Stores refresh token sessions for rotation/revocation.
  - Key fields: `id`, `user_id`, `token`, `expires_at`, `is_revoked`, `created_at`, `revoked_at`.

### `is_active` and Soft Delete
- `is_active` is a status flag on `users`.
- `is_active=true`: user can authenticate and pass authorization checks.
- `is_active=false`: user is treated as inactive and blocked from protected access.

Soft delete is implemented by setting `users.is_active = false` instead of removing the row.

Soft-delete endpoints:
- `DELETE /users/me`
- `DELETE /users/{user_id}` (permission required)

Hard delete endpoint:
- `DELETE /users/hard/{user_id}` (physically removes row)


## Authentication
Authentication flow:
1. User signs up using `POST /auth/signup`
2. User logs in using `POST /auth/login` and receives:
   - `access_token` (used in `Authorization: Bearer <token>`)
   - `refresh_token`
3. User can log out using `POST /auth/logout` (requires access token). This revokes a stored refresh token for the user.
4. When access token expires, client calls `POST /auth/refresh` to get a new token pair.

Requests to protected endpoints must include:
`Authorization: Bearer <access_token>`

### Login Request Format (`OAuth2PasswordRequestForm`)
`/auth/login` expects `application/x-www-form-urlencoded` fields:
- `username` (email)
- `password`

Example:
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

### How Login Works
1. Server finds user by email (`username` field)
2. Password hash is verified
3. User must be active (`is_active=true`)
4. Access token and refresh token are issued
5. Refresh token is stored in `refresh_tokens`

### How Logout Works
1. Client calls `POST /auth/logout` with bearer access token
2. Server finds a refresh token row for that user
3. Server marks that row as `is_revoked=true`
4. Revoked refresh token cannot be used in `POST /auth/refresh`

Note: Access tokens are stateless JWTs, so an already-issued access token remains valid until it expires.


## Authorization
Authorization is enforced per endpoint using `require_permission(resource, action, scope)`.

At runtime:
1. Token is validated
2. Current user is loaded
3. User permissions are resolved through:
   - `users -> user_roles -> roles -> role_permissions -> permissions`
4. If permission exists, request is allowed
5. If not:
   - `401` for missing/invalid token
   - `403` for insufficient permissions

Current seeded roles:
- `user`
- `admin`
- `superuser`

Role-permission mappings are populated by `populate_db.py`.

### Current Roles and Permissions
- `user`
  - `users:read:own`
  - `users:update:own`
  - `users:delete:own`
  - `events:read:any`
  - `events:update:own`
  - `events:add:own`
  - `events:delete:own`

- `admin`
  - Everything in `user`, plus:
  - `users:read:any`
  - `events:update:any`
  - `events:delete:any`
  - `admins:add:any`
  - `admins:delete:own`

- `superuser`
  - Everything in `admin`, plus:
  - `admins:delete:any`
  - `roles:read:any`
  - `roles:add:any`
  - `roles:update:any`
  - `roles:delete:any`
  - `role-permissions:read:any`
  - `role-permissions:add:any`
  - `role-permissions:update:any`
  - `role-permissions:delete:any`


## How to install
1. Clone and enter the project
```bash
git clone <your-repo-url>
cd AuthBackEnd
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run database migrations
```bash
alembic upgrade head
```
 

5. Populate seed data (roles, permissions, role-permissions, test users)
```bash
python populate_db.py
```
this will populate the database with three users, and provide their credentials (email, password).

6. Start the server
```bash
uvicorn app.main:app --reload
```

7. Run tests to ensure the application works fine
```bash
pytest -q tests/
```

8. Open Swagger UI
`http://127.0.0.1:8000/docs`
to get interactive web page to test the endpoints, you can authorize 
