#!/usr/bin/env python3
"""
Populate database with RBAC roles, permissions, and role-permission mappings.

This script follows the README role matrix with one requested change:
- do NOT create `guest`
- create only: `user`, `admin`, `superuser`
"""

from __future__ import annotations

import random
import string
from collections.abc import Iterable

from app.core.security import hash_password
from app.db.models import Action, Permission, Resource, Role, RolePermission, User, UserRole
from app.db.session import SessionLocal


# Core RBAC constants
ROLE_DEFINITIONS = [
    ("user", "Regular authenticated user"),
    ("admin", "Administrative user"),
    ("superuser", "System superuser"),
]

ACTIONS = ["read", "add", "update", "delete"]

USER_PERMISSIONS = {
    ("users", "read", "own"),
    ("users", "update", "own"),
    ("users", "delete", "own"),
    ("events", "read", "any"),
    ("events", "update", "own"),
    ("events", "add", "own"),
    ("events", "delete", "own"),
    ("user-roles", "read", "own"),
}

ADMIN_EXTRA_PERMISSIONS = {
    ("users", "read", "any"),
    ("events", "update", "any"),
    ("events", "delete", "any"),
    ("admins", "add", "any"),
    ("admins", "delete", "own"),
}

SUPERUSER_EXTRA_PERMISSIONS = {
    ("admins", "delete", "any"),
    ("roles", "read", "any"),
    ("roles", "add", "any"),
    ("roles", "update", "any"),
    ("roles", "delete", "any"),
    ("role-permissions", "read", "any"),
    ("role-permissions", "add", "any"),
    ("role-permissions", "update", "any"),
    ("role-permissions", "delete", "any"),
    ("permissions", "add", "any"),
    ("permissions", "read", "any"),
    ("permissions", "update", "any"),
    ("permissions", "delete", "any"),
}

ROLE_PERMISSION_MATRIX = {
    "user": set(USER_PERMISSIONS),
    "admin": set(USER_PERMISSIONS) | set(ADMIN_EXTRA_PERMISSIONS),
    "superuser": set(USER_PERMISSIONS) | set(ADMIN_EXTRA_PERMISSIONS) | set(SUPERUSER_EXTRA_PERMISSIONS),
}


def generate_random_email(name: str) -> str:
    random_suffix = "".join(random.choices(string.digits, k=3))
    return f"{name}@example.com"


def get_or_create_user(db, first_name: str, last_name: str, password_plain: str) -> User:
    existing = db.query(User).filter(User.first_name == first_name, User.last_name == last_name).first()
    if existing:
        return existing

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=generate_random_email(first_name.lower()),
        password=hash_password(password_plain),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_role(db, name: str, description: str) -> Role:
    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        return existing

    role = Role(name=name, description=description)
    db.add(role)
    db.flush()
    return role


def get_or_create_action(db, name: str) -> Action:
    existing = db.query(Action).filter(Action.name == name).first()
    if existing:
        return existing

    action = Action(name=name, description=f"{name} action")
    db.add(action)
    db.flush()
    return action


def get_or_create_resource(db, name: str) -> Resource:
    existing = db.query(Resource).filter(Resource.name == name).first()
    if existing:
        return existing

    resource = Resource(name=name, description=f"{name} resource")
    db.add(resource)
    db.flush()
    return resource


def get_or_create_permission(
    db,
    resource: Resource,
    action: Action,
    scope: str,
) -> Permission:
    existing = (
        db.query(Permission)
        .filter(
            Permission.resource_id == resource.id,
            Permission.action_id == action.id,
            Permission.scope == scope,
        )
        .first()
    )
    if existing:
        return existing

    permission = Permission(resource_id=resource.id, action_id=action.id, scope=scope)
    db.add(permission)
    db.flush()
    return permission


def sync_user_roles(db, desired_pairs: set[tuple[int, int]]) -> None:
    existing = db.query(UserRole).all()
    existing_pairs = {(ur.user_id, ur.role_id) for ur in existing}

    stale_pairs = existing_pairs - desired_pairs
    for user_id, role_id in stale_pairs:
        (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .delete(synchronize_session=False)
        )

    missing_pairs = desired_pairs - existing_pairs
    for user_id, role_id in missing_pairs:
        db.add(UserRole(user_id=user_id, role_id=role_id))


def ensure_role_permission(db, role: Role, permission: Permission) -> None:
    existing = (
        db.query(RolePermission)
        .filter(RolePermission.role_id == role.id, RolePermission.permission_id == permission.id)
        .first()
    )
    if existing:
        return
    db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def delete_guest_role_if_exists(db) -> None:
    guest = db.query(Role).filter(Role.name == "guest").first()
    if not guest:
        return
    db.query(UserRole).filter(UserRole.role_id == guest.id).delete(synchronize_session=False)
    db.query(RolePermission).filter(RolePermission.role_id == guest.id).delete(synchronize_session=False)
    db.delete(guest)


def sync_role_permissions(db, role: Role, desired_permission_ids: set[int]) -> None:
    existing = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
    existing_ids = {rp.permission_id for rp in existing}

    # Remove stale permissions that are no longer in the matrix.
    stale_ids = existing_ids - desired_permission_ids
    if stale_ids:
        (
            db.query(RolePermission)
            .filter(RolePermission.role_id == role.id, RolePermission.permission_id.in_(stale_ids))
            .delete(synchronize_session=False)
        )

    # Add missing permissions from the matrix.
    missing_ids = desired_permission_ids - existing_ids
    for permission_id in missing_ids:
        db.add(RolePermission(role_id=role.id, permission_id=permission_id))


def permission_key(permission_triplet: tuple[str, str, str]) -> str:
    resource, action, scope = permission_triplet
    return f"{resource}:{action}:{scope}"


def all_permission_triplets(matrix_values: Iterable[set[tuple[str, str, str]]]) -> set[tuple[str, str, str]]:
    triplets: set[tuple[str, str, str]] = set()
    for role_perms in matrix_values:
        triplets |= role_perms
    return triplets


def main() -> None:
    print("Starting RBAC database population")
    db = SessionLocal()
    try:
        delete_guest_role_if_exists(db)

        # 1) Users for quick local testing
        users = {
            "user_1": get_or_create_user(db, "User1", "User", "user1"),
            "user_2": get_or_create_user(db, "User2", "User", "user2"),
            "user_3": get_or_create_user(db, "User3", "User", "user3"),
        }

        # 2) Roles (no guest)
        roles = {name: get_or_create_role(db, name, description) for name, description in ROLE_DEFINITIONS}

        # 3) Actions
        actions = {name: get_or_create_action(db, name) for name in ACTIONS}

        # 4) Resources from permission matrix
        all_triplets = all_permission_triplets(ROLE_PERMISSION_MATRIX.values())
        resource_names = sorted({resource for resource, _, _ in all_triplets})
        resources = {name: get_or_create_resource(db, name) for name in resource_names}

        # 5) Permissions
        permissions: dict[str, Permission] = {}
        for resource_name, action_name, scope in sorted(all_triplets):
            permission = get_or_create_permission(
                db,
                resource=resources[resource_name],
                action=actions[action_name],
                scope=scope,
            )
            permissions[f"{resource_name}:{action_name}:{scope}"] = permission

        # 6) Sync user-role assignments to exactly three mappings
        desired_user_role_pairs = {
            (users["user_1"].id, roles["user"].id),
            (users["user_2"].id, roles["admin"].id),
            (users["user_3"].id, roles["superuser"].id),
        }
        sync_user_roles(db, desired_user_role_pairs)

        # 7) Role-permission assignments from README matrix
        for role_name, triplets in ROLE_PERMISSION_MATRIX.items():
            role = roles[role_name]
            desired_permission_ids = {permissions[permission_key(triplet)].id for triplet in triplets}
            sync_role_permissions(db, role, desired_permission_ids)

        db.commit()
        print("USERS CREDENTIALS: ")
        for k,v in users.items():
            print(f"{k} : email:{v.email}, password: {(v.first_name.lower())}")
        print("*"*100)


        print("RBAC population complete")
        print(f"Roles: {', '.join(sorted(roles.keys()))}")
        print(f"Resources: {', '.join(resource_names)}")
        print(f"Permissions created/ensured: {len(all_triplets)}")
        print("Role permission counts:")
        for role_name in ["user", "admin", "superuser"]:
            print(f"  {role_name}: {len(ROLE_PERMISSION_MATRIX[role_name])}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
