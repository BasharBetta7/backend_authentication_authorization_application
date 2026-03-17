from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.models import Action, Permission, Resource, Role, RolePermission, User, UserRole
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


def _u(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def _ensure_permission(db, resource_name: str, action_name: str, scope: str) -> Permission:
    resource = db.query(Resource).filter(Resource.name == resource_name).first()
    if not resource:
        resource = Resource(name=resource_name, description=f"{resource_name} resource")
        db.add(resource)
        db.flush()

    action = db.query(Action).filter(Action.name == action_name).first()
    if not action:
        action = Action(name=action_name, description=f"{action_name} action")
        db.add(action)
        db.flush()

    permission = (
        db.query(Permission)
        .filter(
            Permission.resource_id == resource.id,
            Permission.action_id == action.id,
            Permission.scope == scope,
        )
        .first()
    )
    if not permission:
        permission = Permission(resource_id=resource.id, action_id=action.id, scope=scope)
        db.add(permission)
        db.flush()
    return permission


def _create_privileged_actor() -> tuple[dict, int]:
    db = SessionLocal()
    role = Role(name=_u("role-all"), description="all endpoint permissions")
    db.add(role)
    db.flush()

    required_permissions = {
        ("users", "add", "any"),
        ("users", "read", "any"),
        ("users", "read", "own"),
        ("users", "update", "any"),
        ("users", "update", "own"),
        ("users", "delete", "any"),
        ("users", "delete", "own"),
        ("roles", "add", "any"),
        ("roles", "read", "any"),
        ("roles", "update", "any"),
        ("roles", "delete", "any"),
        ("permission", "add", "any"),
        ("permission", "read", "any"),
        ("permission", "update", "any"),
        ("permission", "delete", "any"),
        ("resources", "add", "any"),
        ("resources", "read", "any"),
        ("resources", "udpate", "any"),
        ("resources", "delete", "any"),
        ("actions", "add", "any"),
        ("actions", "read", "any"),
        ("actions", "update", "any"),
        ("actions", "delete", "any"),
        ("events", "add", "any"),
        ("events", "read", "any"),
        ("events", "update", "any"),
        ("events", "delete", "any"),
        ("user-roles", "add", "any"),
        ("user-roles", "read", "any"),
        ("user-roles", "update", "any"),
        ("user-roles", "delete", "any"),
        ("permission-roles", "add", "any"),
        ("permission-roles", "read", "any"),
        ("permission-roles", "update", "any"),
        ("permission-roles", "delete", "any"),
    }

    for resource_name, action_name, scope in required_permissions:
        permission = _ensure_permission(db, resource_name, action_name, scope)
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    plain_password = "pass12345"
    actor = User(
        first_name=_u("Actor"),
        last_name="Tester",
        email=f"{_u('actor')}@example.com",
        password=hash_password(plain_password),
        is_active=True,
    )
    db.add(actor)
    db.flush()
    db.add(UserRole(user_id=actor.id, role_id=role.id))
    db.commit()

    actor_email = actor.email
    actor_id = actor.id
    db.close()

    login = client.post("/auth/login", json={"email": actor_email, "password": plain_password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, actor_id


def _create_actor_with_permissions(permission_triplets: set[tuple[str, str, str]]) -> dict:
    db = SessionLocal()
    role = Role(name=_u("role-limited"), description="limited permissions")
    db.add(role)
    db.flush()

    for resource_name, action_name, scope in permission_triplets:
        permission = _ensure_permission(db, resource_name, action_name, scope)
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    plain_password = "pass12345"
    actor = User(
        first_name=_u("Limited"),
        last_name="Tester",
        email=f"{_u('limited')}@example.com",
        password=hash_password(plain_password),
        is_active=True,
    )
    db.add(actor)
    db.flush()
    db.add(UserRole(user_id=actor.id, role_id=role.id))
    db.commit()
    actor_email = actor.email
    db.close()

    login = client.post("/auth/login", json={"email": actor_email, "password": plain_password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_health_and_auth_endpoints():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    signup_email = f"{_u('signup')}@example.com"
    signup_password = "signup123"
    signup = client.post(
        "/auth/signup",
        json={
            "first_name": "Sign",
            "last_name": "Up",
            "email": signup_email,
            "password": signup_password,
            "confirm_password": signup_password,
        },
    )
    assert signup.status_code == 201

    login = client.post("/auth/login", json={"email": signup_email, "password": signup_password})
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()


def test_users_endpoints_smoke():
    headers, actor_id = _create_privileged_actor()
    email_1 = f"{_u('user1')}@example.com"
    email_2 = f"{_u('user2')}@example.com"
    email_3 = f"{_u('user3')}@example.com"

    create_1 = client.post(
        "/users/",
        headers=headers,
        json={"first_name": "U1", "last_name": "A", "email": email_1, "password": "password1"},
    )
    assert create_1.status_code == 201
    created_user_1_id = create_1.json()["id"]

    create_2 = client.post(
        "/users/",
        headers=headers,
        json={"first_name": "U2", "last_name": "B", "email": email_2, "password": "password2"},
    )
    assert create_2.status_code == 201
    created_user_2_id = create_2.json()["id"]

    create_3 = client.post(
        "/users/",
        headers=headers,
        json={"first_name": "U3", "last_name": "C", "email": email_3, "password": "password3"},
    )
    assert create_3.status_code == 201
    created_user_3_id = create_3.json()["id"]

    assert client.get("/users/", headers=headers).status_code == 200
    assert client.get("/users/me", headers=headers).status_code == 200
    assert client.get(f"/users/{created_user_1_id}", headers=headers).status_code == 200

    assert (
        client.patch(
            "/users/me",
            params={"user_id": actor_id},
            headers=headers,
            json={"last_name": "Updated"},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/users/{created_user_1_id}",
            headers=headers,
            json={"first_name": "UserOne"},
        ).status_code
        == 200
    )

    assert client.delete(f"/users/hard/{created_user_2_id}", headers=headers).status_code == 204
    assert client.delete(f"/users/{created_user_3_id}", headers=headers).status_code == 204

    # Call delete me last in users flow since actor becomes inactive.
    assert client.delete("/users/me", headers=headers).status_code == 204


def test_roles_permissions_resources_actions_events_user_roles_permission_roles_endpoints_smoke():
    headers, _ = _create_privileged_actor()

    role_name = _u("role")
    role_create = client.post("/roles/", headers=headers, json={"name": role_name, "description": "d"})
    assert role_create.status_code == 201
    role_id = role_create.json()["id"]
    assert client.get("/roles/", headers=headers).status_code == 200
    assert client.get(f"/roles/{role_id}", headers=headers).status_code == 200
    assert client.patch(f"/roles/{role_id}", headers=headers, json={"description": "updated"}).status_code == 200

    resource_name = _u("resource")
    resource_create = client.post(
        "/resources/",
        headers=headers,
        json={"name": resource_name, "description": "desc"},
    )
    assert resource_create.status_code == 201
    resource_id = resource_create.json()["id"]
    assert client.get("/resources/", headers=headers).status_code == 200
    assert client.get(f"/resources/{resource_id}", headers=headers).status_code == 200
    assert client.patch(f"/resources/{resource_id}", headers=headers, json={"description": "new"}).status_code == 200

    action_name = _u("action")
    action_create = client.post(
        "/actions/",
        headers=headers,
        json={"name": action_name, "description": "desc"},
    )
    assert action_create.status_code == 201
    action_id = action_create.json()["id"]
    assert client.get("/actions/", headers=headers).status_code == 200
    assert client.get(f"/actions/{action_id}", headers=headers).status_code == 200
    assert client.patch(f"/actions/{action_id}", headers=headers, json={"description": "new"}).status_code == 200

    permission_create = client.post(
        "/permissions/",
        headers=headers,
        json={"resource_name": resource_name, "action_name": action_name, "scope": "any"},
    )
    assert permission_create.status_code == 201
    permission_id = permission_create.json()["id"]
    assert client.get("/permissions/", headers=headers).status_code == 200
    assert client.get(f"/permissions/{permission_id}", headers=headers).status_code == 200
    assert client.patch(f"/permissions/{permission_id}", headers=headers, json={"scope": "own"}).status_code == 200

    event_create = client.post(
        "/events/",
        headers=headers,
        json={
            "name": _u("event"),
            "date": datetime.now(timezone.utc).isoformat(),
            "description": "event description",
        },
    )
    assert event_create.status_code == 201
    event_id = event_create.json()["id"]
    assert client.get("/events/", headers=headers).status_code == 200
    assert client.get(f"/events/{event_id}", headers=headers).status_code == 200
    assert client.patch(f"/events/{event_id}", headers=headers, json={"description": "updated event"}).status_code == 200

    user_create = client.post(
        "/users/",
        headers=headers,
        json={"first_name": "UR", "last_name": "User", "email": f"{_u('ur')}@example.com", "password": "password1"},
    )
    assert user_create.status_code == 201
    target_user_id = user_create.json()["id"]

    user_role_create = client.post(
        "/user-roles/",
        headers=headers,
        json={"user_id": target_user_id, "role_id": role_id},
    )
    assert user_role_create.status_code == 201
    assert client.get("/user-roles/", headers=headers).status_code == 200
    assert client.get(f"/user-roles/{target_user_id}/{role_id}", headers=headers).status_code == 200
    assert (
        client.patch(
            f"/user-roles/{target_user_id}/{role_id}",
            headers=headers,
            json={"user_id": target_user_id, "role_id": role_id},
        ).status_code
        == 200
    )

    permission_role_create = client.post(
        "/permission-roles/",
        headers=headers,
        json={"role_id": role_id, "permission_id": permission_id},
    )
    assert permission_role_create.status_code == 201
    permission_role_id = permission_role_create.json()["id"]
    assert client.get("/permission-roles/", headers=headers).status_code == 200
    assert client.get(f"/permission-roles/{permission_role_id}", headers=headers).status_code == 200
    assert (
        client.patch(
            f"/permission-roles/{permission_role_id}",
            headers=headers,
            json={"role_id": role_id, "permission_id": permission_id},
        ).status_code
        == 200
    )

    assert client.delete(f"/permission-roles/{permission_role_id}", headers=headers).status_code == 204
    assert client.delete(f"/user-roles/{target_user_id}/{role_id}", headers=headers).status_code == 204
    assert client.delete(f"/events/{event_id}", headers=headers).status_code == 204
    assert client.delete(f"/permissions/{permission_id}", headers=headers).status_code == 204
    assert client.delete(f"/actions/{action_id}", headers=headers).status_code == 204
    assert client.delete(f"/resources/{resource_id}", headers=headers).status_code == 204
    assert client.delete(f"/roles/{role_id}", headers=headers).status_code == 204


def test_user_forbidden_from_endpoint_outside_permissions():
    headers = _create_actor_with_permissions({("users", "read", "own")})

    own_profile = client.get("/users/me", headers=headers)
    assert own_profile.status_code == 200

    roles_list = client.get("/roles/", headers=headers)
    assert roles_list.status_code == 403
