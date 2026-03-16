from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_permission
from app.crud.user import create_user, delete_user, list_users, get_user, update_user,soft_delete_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserDelete
from app.db.models.user import User


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission('users','add','any'))])
def create(payload:UserCreate, db:Session = Depends(get_db)):
    return create_user(db, payload)

@router.get("/", response_model= list[UserRead], dependencies=[Depends(require_permission('users','read','any'))])
def get_all( db:Session = Depends(get_db)):
    return list_users(db)

@router.get("/me", response_model=UserRead, dependencies=[Depends(require_permission('users','read','own'))])
def get_current_one(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's profile - requires users:read:own permission"""
    return current_user

@router.get("/{user_id:int}", response_model=UserRead)
def get_one(user_id:int, current_user: User = Depends(require_permission('users','read','any')), db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user Found")
    return user 


@router.patch("/me", response_model=UserRead, dependencies=[Depends(require_permission('users','update','own'))])
def upate(user_id:int, payload:UserUpdate, current_user = Depends(get_current_user), db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return update_user(db, user, payload)


@router.patch("/{user_id:int}", response_model=UserRead, dependencies=[Depends(require_permission('users','update','any'))])
def upate(user_id:int, payload:UserUpdate, current_user = Depends(get_current_user), db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return update_user(db, user, payload)


@router.delete("/hard/{user_id:int}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission('users','delete','any'))])
def delete_one(user_id: int, db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(require_permission('users','delete','own'))] )
def delete_me(current_user: User = Depends(get_current_user),
              db:Session = Depends(get_db),
              _:None = Depends(require_permission("users","delete","own"))):
    print(current_user)
    soft_delete_user(db, current_user)


@router.delete("/{user_id:int}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission('users','delete','any'))])
def soft_delete_one(user_id: int, db:Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    soft_delete_user(db, user)

