from sqlalchemy.orm import Session

from app.db.models.role_permission import RolePermission
from app.schemas.role_permission import RolePermissionCreate, RolePermissionUpdate


def create_permission_role(db: Session, payload: RolePermissionCreate) -> RolePermission:
    obj = RolePermission(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_permission_roles(db: Session) -> list[RolePermission]:
    return db.query(RolePermission).all()


def get_permission_role(db: Session, permission_role_id: int) -> RolePermission | None:
    return db.query(RolePermission).filter(RolePermission.id == permission_role_id).first()


def update_permission_role(db: Session, permission_role: RolePermission, payload: RolePermissionUpdate) -> RolePermission:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(permission_role, k, v)
    db.commit()
    db.refresh(permission_role)
    return permission_role


def delete_permission_role(db: Session, permission_role: RolePermission) -> None:
    db.delete(permission_role)
    db.commit()
