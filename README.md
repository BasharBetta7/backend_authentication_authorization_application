Implementing Backend application with authorization and authentication logic.

## Tables:
- Users:
    - id PrimaryKEY (PK)
    -  first_name str
    -  last_name str
    -  email unique(str)

- Roles:
    -  id PK
    -  name unique(str)
    -  description str


- UserRoles:
    -  id PK
    -  user_id FK(users.id)
    -  role_id FK(roles.id)
    -  unique(user_id, role_id)

- Resources:
    -  id PK
    -  name unique(str)
    -  description str

- Actions:
    -  id PK
    -  name unique(str)
    -  description

- Permissions:
    -  id PK
    -  resource_id FK(resources.id)
    -  action_id FK(actions.id)
    -  scope str ['own', 'any']
    -  unique (resource_id, action_id, scope)

- RolePermissions:
    -  id PK
    -  role_id FK(roles.id)
    -  permission_id FK(permissions.id)
    -  unique(role_id, permission_id)

- RefreshTokens:
    - id PK
    - user_id FK(users.id)
    - token_jti unique(str)
    - expires_at TIMESTAMP
    - is_revoked boolean == False
    - created_at TIMESTAMP
    - revoked_at TIMESTAMP
    


## Modules:
- User Module:
    -  Register
    -  Login
    -  Logout
    -  get current profile
    -  update profile
    -  soft delete
- Authorization Module:
    -  list roles/actions/permissions/resources
    -  assign roles to users
    -  assign permissions to roles
    -  create new roles or permissions
- Mock business module:
    -  fake dummy resources : products/items/documents/events
    -  endpoints that can check access and return dummy JSON 



