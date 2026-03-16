# Implementing Backend application with authorization and authentication logic.
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




## Authentication :
when performing request to endpoint, we will include Authorization: Bearer <token> header. Token will be extracted from Authorization header of the request, which fetches the token of the current user. Request then are processed based on the token passed to determine permissions and respond.

## Authorization:
each end point will be assigned a permission, to determine authorization rights of the user. 
roles are : guest, user, admin, superuser 
1. Guest: can only signup. This role is the default which will be assigned to all users
2. User: this is a user with valid access token.

### Role Permissions:
Permissions are organized as triplets of <Resource>:<Action>:<Scope>. 
For example, the permission to read the user profile requires the permission: users:read:own.
Below we explain the permission of each role:

1. Guest: 
    - events:read:any
    
2. User:
    - users:read:own
    - users:update:own
    - users:delete:own
    - events:read:any
    - events:update:own
    - events:add:own
    - events:delete:own
3. Admin:
    - everything in User
    - users:read:any
    - events:update:any
    - events:add:own
    - events:delete:any
    - admins:add:any
    - admins:delete:own
4. Superuser:
    - everything in Admin
    - admins:delete:any
    - roles:read|add|update|delete:any


## Flow of request:
1. request to endpoint 
2. validation of access token if needed to access : grant access or 401 
3. validation of the permission to access the endpoint
4. response based on role permission: grant access or 403 


