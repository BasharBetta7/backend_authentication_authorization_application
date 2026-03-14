from sqlalchemy.orm import Session

from app.db.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

def create_role(db: Session, payload:RoleCreate) -> Role:
    obj = Role(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_roles(db:Session) -> list[Role]:
    return db.query(Role).all()

def get_role(db:Session, role_id:int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()

def update_role(db:Session, role:Role, payload:RoleUpdate) -> Role:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(role,k,v)
    db.commit()
    db.refresh(role)
    return role

def delete_role(db:Session, role:Role) -> None:
    db.delete(role)
    db.commit()




