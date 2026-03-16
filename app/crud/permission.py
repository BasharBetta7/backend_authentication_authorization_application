from sqlalchemy.orm import Session, joinedload

from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionDelete, PermissionCreateByName
from app.db.models.permission import Permission
from app.crud.resource import get_resource_by_name
from app.crud.action import get_action_by_name

def create_permission(db:Session, payload:PermissionCreate) -> Permission:
    obj = Permission(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def create_permission_by_name(db:Session, payload:PermissionCreateByName) -> Permission:
    resource = get_resource_by_name(db, payload.resource_name)
    action = get_action_by_name(db, payload.action_name)
    scope = payload.scope

    obj = Permission(resource_id=resource.id, action_id=action.id, scope=scope)
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


def get_or_create_permission(db: Session, resource_name: str, action_name: str, scope: str = "own") -> Permission:
    resource = get_resource_by_name(db, resource_name)
    if not resource:
        from app.schemas.resource import ResourceCreate
        from app.crud.resource import create_resource
        resource = create_resource(db, ResourceCreate(name=resource_name))
    
    action = get_action_by_name(db, action_name)
    if not action:
        from app.schemas.action import ActionCreate
        from app.crud.action import create_action
        action = create_action(db, ActionCreate(name=action_name))
    
    permission = db.query(Permission).filter(
        Permission.resource_id == resource.id,
        Permission.action_id == action.id,
        Permission.scope == scope
    ).first()
    
    if not permission:
        permission = create_permission(db, PermissionCreate(
            resource_id=resource.id,
            action_id=action.id,
            scope=scope
        ))
    
    return permission
    


