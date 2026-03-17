from sqlalchemy import and_
from sqlalchemy.orm import Session


from app.db.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate


def create_user_role(db: Session, payload: UserRoleCreate) -> UserRole:
    obj = UserRole(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj




def list_user_roles(db: Session) -> list[UserRole]:
    return db.query(UserRole).all()


def get_user_role(db: Session, user_id: int, role_id: int) -> UserRole | None:
    return db.query(UserRole).filter(and_(UserRole.user_id == user_id, UserRole.role_id == role_id)).first()

def get_user_role_by_user(db:Session, user_id:int ) -> list[UserRole] | None:
    return db.query(UserRole).filter(UserRole.user_id == user_id).all()

def update_user_role(db: Session, user_role: UserRole, payload: UserRoleUpdate) -> UserRole:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(user_role, k, v)
    db.commit()
    db.refresh(user_role)
    return user_role


def delete_user_role(db: Session, user_role: UserRole) -> None:
    db.delete(user_role)
    db.commit()
