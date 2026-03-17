from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.permission_role import (
    create_permission_role,
    delete_permission_role,
    get_permission_role,
    list_permission_roles,
    update_permission_role,
)
from app.db.session import get_db
from app.schemas.role_permission import RolePermissionCreate, RolePermissionRead, RolePermissionUpdate
from app.core.auth import require_permission, get_current_user

router = APIRouter(prefix="/permission-roles", tags=["permission_roles"])


@router.post("/", response_model=RolePermissionRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission('permission-roles','add','any'))])
def create(payload: RolePermissionCreate, db: Session = Depends(get_db)):
    return create_permission_role(db, payload)


@router.get("/", response_model=list[RolePermissionRead],
            # dependencies=[Depends(require_permission('permission-roles','read','any'))]
)
def get_all(db: Session = Depends(get_db)):
    return list_permission_roles(db)


@router.get("/{permission_role_id}", response_model=RolePermissionRead,
            dependencies=[Depends(require_permission('permission-roles','read','any'))])
def get_one(permission_role_id: int, db: Session = Depends(get_db)):
    permission_role = get_permission_role(db, permission_role_id)
    if not permission_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission role not found")
    return permission_role


@router.patch("/{permission_role_id}", response_model=RolePermissionRead,
              dependencies=[Depends(require_permission('permission-roles','update','any'))])
def update_one(permission_role_id: int, payload: RolePermissionUpdate, db: Session = Depends(get_db)):
    permission_role = get_permission_role(db, permission_role_id)
    if not permission_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission role not found")
    return update_permission_role(db, permission_role, payload)


@router.delete("/{permission_role_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission('permission-roles','delete','any'))])
def delete_one(permission_role_id: int, db: Session = Depends(get_db)):
    permission_role = get_permission_role(db, permission_role_id)
    if not permission_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission role not found")
    delete_permission_role(db, permission_role)
