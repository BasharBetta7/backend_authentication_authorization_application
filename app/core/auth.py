from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import verify_access_token
from app.crud.user import get_user
from app.db.session import get_db
from app.db.models.user import User
from app.db.models import RolePermission, Permission, Resource, Action, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate the current user from JWT token"""
    # Verify and decode the token
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )
    
    # Get user from database
    print(user_id)
    user = get_user(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


def check_user_permission(
    user: User,
    resource_name: str,
    action_name: str,
    scope: str = "own",
    db: Session = Depends(get_db)
) -> bool:
    

    from app.db.models import UserRole

    # Query: User -> UserRole -> Role -> RolePermission -> Permission -> Resource/Action
    permissions = db.query(Permission).\
        select_from(UserRole).\
        join(UserRole.role).\
        join(RolePermission, RolePermission.role_id == UserRole.role_id).\
        join(Permission, Permission.id == RolePermission.permission_id).\
        join(Resource, Resource.id == Permission.resource_id).\
        join(Action, Action.id == Permission.action_id).\
        filter(
            UserRole.user_id == user.id,
            Resource.name == resource_name,
            Action.name == action_name,
            Permission.scope == scope
        ).all()


    return len(permissions) > 0


def require_permission(
    resource_name: str,
    action_name: str,
    scope: str = "own"
):
    """
    Dependency function to require specific permission for an endpoint.

    Args:
        resource_name: Name of the resource (e.g., "users")
        action_name: Name of the action (e.g., "read")
        scope: Permission scope ("own" or "any")

    Returns:
        Dependency function that checks permission and returns current user
    """
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not check_user_permission(current_user, resource_name, action_name, scope, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {resource_name}:{action_name}:{scope}"
            )
        return current_user

    return permission_dependency
    

