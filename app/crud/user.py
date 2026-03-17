from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate
from app.db.models.user import User

def create_user(db:Session, payload:UserCreate) -> User:
    data = payload.model_dump()
    data.pop("confirm_password", None)
    data["password"] = hash_password(data["password"])
    obj = User(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_users(db:Session) -> list[User]:
    return db.query(User).all()

def get_user(db: Session, user_id:int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_name(db:Session, name:str) -> User | None:
    return db.query(User).filter(User.first_name == name).all()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def update_user(db:Session, user:User, payload:UserUpdate) -> User:
    for k,v in payload.model_dump(exclude_unset=True).items():
        if k == "password":
            v = hash_password(v)
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db:Session, user:User) -> None:
    db.delete(user)
    db.commit()

def soft_delete_user(db:Session, user:User) -> User:
    user.is_active = False
    db.refresh(user)
    return user
