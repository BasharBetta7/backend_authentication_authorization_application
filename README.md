# Authentication & Authorization Backend

## Description
Этот проект представляет собой backend на FastAPI, который реализует:
- Authentication на основе JWT (`access token` + `refresh token`)
- Authorization по модели RBAC с использованием `roles`, `permissions`, `user_roles` и `role_permissions`
- CRUD API для пользователей и объектов Authorization (roles, resources, actions, permissions)
- Mock API для демонстрации проверок permissions

Permissions задаются в формате:
`resource:action:scope`

Пример:
`users:read:own`


## Tables
- `users`
  - Хранит учетные данные пользователя и статус.
  - Основные поля: `id`, `first_name`, `last_name`, `email` (unique), `password`, `is_active`.

- `roles`
  - Хранит определения ролей.
  - Основные поля: `id`, `name` (unique), `description`.

- `user_roles`
  - Связь many-to-many между users и roles.
  - Основные поля: `user_id` (FK -> `users.id`), `role_id` (FK -> `roles.id`).
  - Composite uniqueness по `(user_id, role_id)`.

- `resources`
  - Хранит названия защищаемых resources для permission triplets.
  - Основные поля: `id`, `name` (unique), `description`.

- `actions`
  - Хранит допустимые actions для permission triplets.
  - Основные поля: `id`, `name` (unique), `description`.

- `permissions`
  - Хранит комбинации `resource + action + scope`.
  - Основные поля: `id`, `resource_id` (FK -> `resources.id`), `action_id` (FK -> `actions.id`), `scope` (`own`/`any`).
  - Unique constraint на `(resource_id, action_id, scope)`.

- `role_permissions`
  - Связь many-to-many между roles и permissions.
  - Основные поля: `id`, `role_id` (FK -> `roles.id`), `permission_id` (FK -> `permissions.id`).
  - Unique constraint на `(role_id, permission_id)`.

- `refresh_tokens`
  - Хранит refresh token sessions для rotation/revocation.
  - Основные поля: `id`, `user_id`, `token`, `expires_at`, `is_revoked`, `created_at`, `revoked_at`.

### `is_active` и Soft Delete
- `is_active` — это статусный флаг в таблице `users`.
- `is_active=true`: пользователь может проходить Authentication и Authorization checks.
- `is_active=false`: пользователь считается неактивным и блокируется при доступе к protected endpoints.

`Soft delete` реализован через установку `users.is_active = false`, без физического удаления строки.

Endpoints для soft delete:
- `DELETE /users/me`
- `DELETE /users/{user_id}` (требуются соответствующие permissions)

Endpoint для hard delete:
- `DELETE /users/hard/{user_id}` (физически удаляет строку из БД)


## Authentication
Authentication flow:
1. Пользователь регистрируется через `POST /auth/signup`
2. Пользователь выполняет login через `POST /auth/login` и получает:
   - `access_token` (используется в `Authorization: Bearer <token>`)
   - `refresh_token`
3. Пользователь может выполнить logout через `POST /auth/logout` (требуется access token). Это revokes одну сохраненную refresh token запись пользователя.
4. Когда `access token` истекает, клиент вызывает `POST /auth/refresh`, чтобы получить новую пару токенов.

Для protected endpoints необходимо передавать:
`Authorization: Bearer <access_token>`

### Login Request Format (`OAuth2PasswordRequestForm`)
`/auth/login` ожидает `application/x-www-form-urlencoded` поля:
- `username` (email)
- `password`

Пример:
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

### Как работает Login
1. Сервер находит пользователя по email (из поля `username`)
2. Проверяет `password hash`
3. Пользователь должен быть активным (`is_active=true`)
4. Выдаются `access token` и `refresh token`
5. `refresh token` сохраняется в таблице `refresh_tokens`

### Как работает Logout
1. Клиент вызывает `POST /auth/logout` с bearer access token
2. Сервер находит запись refresh token для пользователя
3. Сервер помечает эту запись как `is_revoked=true`
4. Revoked refresh token больше нельзя использовать в `POST /auth/refresh`

Примечание: `access token` является stateless JWT, поэтому уже выданный access token остается валидным до истечения срока действия.


## Authorization
Authorization применяется на уровне endpoint через `require_permission(resource, action, scope)`.

Во время выполнения:
1. Валидируется token
2. Загружается current user
3. Permissions пользователя вычисляются по цепочке:
   - `users -> user_roles -> roles -> role_permissions -> permissions`
4. Если нужная permission найдена — доступ разрешается
5. Если нет:
   - `401` для missing/invalid token
   - `403` для insufficient permissions

Текущие seeded roles:
- `user`
- `admin`
- `superuser`

Role-permission mappings заполняются скриптом `populate_db.py`.

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
  - Все permissions из `user`, плюс:
  - `users:read:any`
  - `events:update:any`
  - `events:delete:any`
  - `admins:add:any`
  - `admins:delete:own`

- `superuser`
  - Все permissions из `admin`, плюс:
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
1. Клонируйте репозиторий и перейдите в проект
```bash
git clone <your-repo-url>
cd backend_authentication_authorization_application
```

2. Создайте и активируйте virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Установите зависимости
```bash
.venv/bin/pip install -r requirements.txt
```

4. Примените migrations
```bash
alembic upgrade head
```

5. Заполните БД seed-данными (roles, permissions, role-permissions, test users)
```bash
python populate_db.py
```
Скрипт заполнит БД тестовыми пользователями и их учетными данными (email, password).

6. Запустите сервер
```bash
uvicorn app.main:app --reload
```

7. Запустите тесты
```bash
pytest -q tests/
```

8. Откройте Swagger UI
`http://127.0.0.1:8000/docs`
Там можно интерактивно тестировать endpoints и выполнять authorize.
