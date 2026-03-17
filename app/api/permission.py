from  fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session 

from app.crud.permission import create_permission, create_permission_by_name, update_permission, list_permissions, delete_permission, get_permission
from app.schemas.permission import PermissionCreate, PermissionCreateByName ,PermissionUpdate, PermissionRead, PermissionDelete
from app.db.session import get_db
from app.core.auth import require_permission, get_current_user

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("/", response_model=PermissionRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission('permission','add','any'))])
def create(payload:PermissionCreateByName, db:Session = Depends(get_db)):
    return create_permission_by_name(db, payload)

@router.get("/", response_model=list[PermissionRead],
            dependencies=[Depends(require_permission('permission','read','any'))])
def get_all(db:Session = Depends(get_db)):
    return list_permissions(db)

@router.get("/{permission_id}", response_model=PermissionRead,
            dependencies=[Depends(require_permission('permission','read','any'))])
def get_one(permission_id:int, db:Session = Depends(get_db)):
    permission = get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission

@router.patch("/{permission_id}", response_model=PermissionRead,
              dependencies=[Depends(require_permission('permission','update','any'))])
def update_one(permission_id:int, payload:PermissionUpdate, db:Session = Depends(get_db)):
    permission = get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return update_permission(db, permission, payload)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission('permission','delete','any'))])
def delete_one(permission_id: int, db:Session = Depends(get_db)):
    permission = get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    delete_permission(db, permission)
