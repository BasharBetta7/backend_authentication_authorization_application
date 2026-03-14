from sqlalchemy.orm import Session

from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionDelete
from app.db.models.permission import Permission

def create_permission(db:Session, payload:PermissionCreate) -> Permission:
    obj = Permission(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_permissions(db:Session) -> list[Permission] | None:
    return db.query(Permission).all()

def get_permission(db:Session, permission_id:int) -> Permission | None:
    return db.query(Permission).filter(Permission.id == permission_id).first()


def update_permission(db:Session, permission:Permission, payload:PermissionUpdate) -> Permission:
    for k,v in payload.model_dump(exclude_unset=True).items():
        setattr(permission, k, v)
    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db:Session, permission:Permission) -> None:
    db.delete(permission)
    db.commit()
    

