from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.crud.user import create_user, delete_user, list_users, get_user, update_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserDelete

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create(payload:UserCreate, db:Session = Depends(get_db)):
    return create_user(db, payload)

@router.get("/", response_model= list[UserRead])
def get_all(db:Session = Depends(get_db)):
    return list_users(db)

@router.get("/{user_id}", response_model=UserRead)
def get_one(user_id:int , db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user Found")
    return user 

@router.patch("/{user_id}", response_model=UserRead)
def upate(user_id:int, payload:UserUpdate, db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return update_user(db, user, payload)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(user_id: int, db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, user)

    