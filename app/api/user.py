from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.user import create_user, delete_user, list_users, get_user, update_user,soft_delete_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserDelete
from app.db.models.user import User


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create(payload:UserCreate, db:Session = Depends(get_db)):
    return create_user(db, payload)

@router.get("/", response_model= list[UserRead])
def get_all( db:Session = Depends(get_db)):
    return list_users(db)

@router.get("/me", response_model=UserRead)
def get_current_one(current_user: User= Depends(get_current_user), db:Session = Depends(get_db)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def get_one(user_id:int, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    print(current_user.first_name)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user Found")
    return user 

@router.patch("/{user_id}", response_model=UserRead)
def upate(user_id:int, payload:UserUpdate, current_user = Depends(get_current_user), db:Session = Depends(get_db)):
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

@router.delete("/soft/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_one(user_id: int, db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    soft_delete_user(db, user)



