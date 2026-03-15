#!/usr/bin/env python3
"""
Database Population Script for Authentication Backend

This script populates the database with initial test data including:
- 3 users (bashar, ahmad, ali) with random emails and passwords matching their names
- 2 roles (user, admin)
- 3 actions (read, add, delete)
- 1 resource (users)
- 2 permissions (users:read:own, users:read:any)
- User-role assignments (bashar -> admin, ahmad -> user)

Usage:
    python populate_db.py

Requirements:
    - All dependencies from requirements.txt must be installed
    - Database must be created and migrated (run alembic upgrade head)
    - Virtual environment should be activated

Author: Database Population Script
Date: March 15, 2026
"""

import random
import string
from app.db.session import SessionLocal
from app.db.models import (
    User, Role, Action, Resource, Permission,
    UserRole, RolePermission
)
from app.core.security import hash_password


def generate_random_email(name: str) -> str:
    """
    Generate a random email address for a user.

    Args:
        name: The user's name to base the email on

    Returns:
        A random email address in format: name{random}@example.com
    """
    random_suffix = ''.join(random.choices(string.digits, k=3))
    return f"{name}{random_suffix}@example.com"


def create_users(db_session):
    """
    Create three users: bashar, ahmad, and ali.

    Each user gets:
    - First name and last name set to their username
    - Random email address
    - Password hashed from their name
    - Active status

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary mapping usernames to User objects
    """
    print("Creating users...")

    users_data = [
        {"name": "bashar", "first_name": "Bashar", "last_name": "User"},
        {"name": "ahmad", "first_name": "Ahmad", "last_name": "User"},
        {"name": "ali", "first_name": "Ali", "last_name": "User"}
    ]

    users = {}
    for user_data in users_data:
        # Check if user already exists
        existing_user = db_session.query(User).filter(User.first_name == user_data["first_name"]).first()
        if existing_user:
            users[user_data["name"]] = existing_user
            print(f"  ✓ User already exists: {user_data['name']} ({existing_user.email})")
            continue

        # Generate random email and hash password
        email = generate_random_email(user_data["name"])
        hashed_password = hash_password(user_data["name"])

        # Create user object
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=email,
            password=hashed_password,
            is_active=True
        )

        # Add to database
        db_session.add(user)
        db_session.flush()  # Get the ID without committing

        users[user_data["name"]] = user
        print(f"  ✓ Created user: {user_data['name']} ({email})")

    return users


def create_roles(db_session):
    """
    Create two roles: 'user' and 'admin'.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary mapping role names to Role objects
    """
    print("Creating roles...")

    roles_data = [
        {"name": "user", "description": "Regular user with basic permissions"},
        {"name": "admin", "description": "Administrator with full permissions"}
    ]

    roles = {}
    for role_data in roles_data:
        # Check if role already exists
        existing_role = db_session.query(Role).filter(Role.name == role_data["name"]).first()
        if existing_role:
            roles[role_data["name"]] = existing_role
            print(f"  ✓ Role already exists: {role_data['name']}")
            continue

        role = Role(
            name=role_data["name"],
            description=role_data["description"]
        )

        db_session.add(role)
        db_session.flush()

        roles[role_data["name"]] = role
        print(f"  ✓ Created role: {role_data['name']}")

    return roles


def create_actions(db_session):
    """
    Create three actions: 'read', 'add', and 'delete'.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary mapping action names to Action objects
    """
    print("Creating actions...")

    actions_data = [
        {"name": "read", "description": "Read/view permission"},
        {"name": "add", "description": "Create/add permission"},
        {"name": "delete", "description": "Delete/remove permission"}
    ]

    actions = {}
    for action_data in actions_data:
        # Check if action already exists
        existing_action = db_session.query(Action).filter(Action.name == action_data["name"]).first()
        if existing_action:
            actions[action_data["name"]] = existing_action
            print(f"  ✓ Action already exists: {action_data['name']}")
            continue

        action = Action(
            name=action_data["name"],
            description=action_data["description"]
        )

        db_session.add(action)
        db_session.flush()

        actions[action_data["name"]] = action
        print(f"  ✓ Created action: {action_data['name']}")

    return actions


def create_resources(db_session):
    """
    Create one resource: 'users'.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        Dictionary mapping resource names to Resource objects
    """
    print("Creating resources...")

    resource_name = "users"
    # Check if resource already exists
    existing_resource = db_session.query(Resource).filter(Resource.name == resource_name).first()
    if existing_resource:
        resources = {resource_name: existing_resource}
        print(f"  ✓ Resource already exists: {resource_name}")
        return resources

    resource = Resource(
        name=resource_name,
        description="User management resource"
    )

    db_session.add(resource)
    db_session.flush()

    resources = {resource_name: resource}
    print(f"  ✓ Created resource: {resource_name}")

    return resources


def create_permissions(db_session, resources, actions):
    """
    Create two permissions:
    - users:read:own (users resource + read action + own scope)
    - users:read:any (users resource + read action + any scope)

    Args:
        db_session: SQLAlchemy database session
        resources: Dictionary of resource objects
        actions: Dictionary of action objects

    Returns:
        Dictionary mapping permission descriptions to Permission objects
    """
    print("Creating permissions...")

    permissions_data = [
        {
            "resource": "users",
            "action": "read",
            "scope": "own",
            "description": "users:read:own"
        },
        {
            "resource": "users",
            "action": "read",
            "scope": "any",
            "description": "users:read:any"
        }
    ]

    permissions = {}
    for perm_data in permissions_data:
        # Check if permission already exists
        existing_permission = db_session.query(Permission).filter(
            Permission.resource_id == resources[perm_data["resource"]].id,
            Permission.action_id == actions[perm_data["action"]].id,
            Permission.scope == perm_data["scope"]
        ).first()

        if existing_permission:
            permissions[perm_data["description"]] = existing_permission
            print(f"  ✓ Permission already exists: {perm_data['description']}")
            continue

        permission = Permission(
            resource_id=resources[perm_data["resource"]].id,
            action_id=actions[perm_data["action"]].id,
            scope=perm_data["scope"]
        )

        db_session.add(permission)
        db_session.flush()

        permissions[perm_data["description"]] = permission
        print(f"  ✓ Created permission: {perm_data['description']}")

    return permissions


def assign_user_roles(db_session, users, roles):
    """
    Assign roles to users:
    - bashar -> admin
    - ahmad -> user

    Args:
        db_session: SQLAlchemy database session
        users: Dictionary of user objects
        roles: Dictionary of role objects
    """
    print("Assigning user roles...")

    user_role_assignments = [
        {"user": "bashar", "role": "admin"},
        {"user": "ahmad", "role": "user"}
    ]

    for assignment in user_role_assignments:
        # Check if assignment already exists
        existing_assignment = db_session.query(UserRole).filter(
            UserRole.user_id == users[assignment["user"]].id,
            UserRole.role_id == roles[assignment["role"]].id
        ).first()

        if existing_assignment:
            print(f"  ✓ User role assignment already exists: {assignment['user']} -> {assignment['role']}")
            continue

        user_role = UserRole(
            user_id=users[assignment["user"]].id,
            role_id=roles[assignment["role"]].id
        )

        db_session.add(user_role)
        print(f"  ✓ Assigned {assignment['user']} -> {assignment['role']}")


def assign_role_permissions(db_session, roles, permissions):
    """
    Assign permissions to roles:
    - admin role gets both permissions (users:read:own and users:read:any)
    - user role gets only users:read:own

    Args:
        db_session: SQLAlchemy database session
        roles: Dictionary of role objects
        permissions: Dictionary of permission objects
    """
    print("Assigning role permissions...")

    role_permission_assignments = [
        {"role": "admin", "permissions": ["users:read:own", "users:read:any"]},
        {"role": "user", "permissions": ["users:read:own"]}
    ]

    for assignment in role_permission_assignments:
        for perm_name in assignment["permissions"]:
            # Check if assignment already exists
            existing_assignment = db_session.query(RolePermission).filter(
                RolePermission.role_id == roles[assignment["role"]].id,
                RolePermission.permission_id == permissions[perm_name].id
            ).first()

            if existing_assignment:
                print(f"  ✓ Role permission assignment already exists: {assignment['role']} -> {perm_name}")
                continue

            role_permission = RolePermission(
                role_id=roles[assignment["role"]].id,
                permission_id=permissions[perm_name].id
            )

            db_session.add(role_permission)
            print(f"  ✓ Assigned {assignment['role']} -> {perm_name}")


def main():
    """
    Main function to populate the database with all initial data.

    This function orchestrates the creation of all database entities
    in the correct order to maintain referential integrity.
    """
    print("🚀 Starting database population...")
    print("=" * 50)

    # Create database session
    db = SessionLocal()

    try:
        # Create base entities first (no dependencies)
        users = create_users(db)
        roles = create_roles(db)
        actions = create_actions(db)
        resources = create_resources(db)

        print()

        # Create permissions (depends on resources and actions)
        permissions = create_permissions(db, resources, actions)

        print()

        # Create relationships
        assign_user_roles(db, users, roles)
        assign_role_permissions(db, roles, permissions)

        print()
        print("=" * 50)
        print("✅ Database population completed successfully!")

        # Display summary
        print("\n📊 Summary:")
        print(f"   Users created: {len(users)}")
        print(f"   Roles created: {len(roles)}")
        print(f"   Actions created: {len(actions)}")
        print(f"   Resources created: {len(resources)}")
        print(f"   Permissions created: {len(permissions)}")

        print("\n👥 User Details:")
        for name, user in users.items():
            print(f"   {name}: {user.email} (password: {name})")

        print("\n🔐 Role Assignments:")
        print("   bashar -> admin")
        print("   ahmad -> user")
        print("   ali -> (no role assigned)")

        # Commit all changes
        db.commit()
        print("\n💾 All changes committed to database.")

    except Exception as e:
        print(f"\n❌ Error during database population: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()