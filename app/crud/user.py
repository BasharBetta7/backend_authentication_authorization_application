from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserUpdate
from app.db.models.user import User

def create_user(db:Session, payload:UserCreate) -> User:
    obj = User(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_users(db:Session) -> list[User]:
    return db.query(User).all()

def get_user(db: Session, user_id:int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db:Session, user:User, payload:UserUpdate) -> User:
    for k,v in payload.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db:Session, user:User) -> None:
    db.delete(user)
    db.commit()


