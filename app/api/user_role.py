from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_role import create_user_role, delete_user_role, get_user_role, list_user_roles, update_user_role
from app.db.session import get_db
from app.schemas.user_role import UserRoleCreate, UserRoleRead, UserRoleUpdate
from app.core.auth import require_permission, get_current_user

router = APIRouter(prefix="/user-roles", tags=["user_roles"])


@router.post("/", response_model=UserRoleRead, status_code=status.HTTP_201_CREATED,)
def create(payload: UserRoleCreate, db: Session = Depends(get_db), current_user = Depends(require_permission('user-roles','add','any'))):
    return create_user_role(db, payload)


@router.get("/", response_model=list[UserRoleRead])
def get_all(db: Session = Depends(get_db)):
    return list_user_roles(db)


@router.get("/{user_id}/{role_id}", response_model=UserRoleRead)
def get_one(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user_role = get_user_role(db, user_id, role_id)
    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    return user_role


@router.patch("/{user_id}/{role_id}", response_model=UserRoleRead)
def update_one(user_id: int, role_id: int, payload: UserRoleUpdate, db: Session = Depends(get_db)):
    user_role = get_user_role(db, user_id, role_id)
    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    return update_user_role(db, user_role, payload)


@router.delete("/{user_id}/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user_role = get_user_role(db, user_id, role_id)
    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    delete_user_role(db, user_role)
