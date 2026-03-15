from sqlalchemy.orm import Session, joinedload

from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionDelete
from app.db.models.permission import Permission
from app.crud.resource import get_resource_by_name
from app.crud.action import get_action_by_name

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


def delete_permission(db:Session, permission:Permission) -> None:
    db.delete(permission)
    db.commit()
    

