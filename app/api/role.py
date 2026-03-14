from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.crud.role import create_role, delete_role, update_role, get_role, list_roles
from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleDelete, RoleUpdate, RoleRead

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create(payload: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, payload)

@router.get("/", response_model=list[RoleRead])
def list_all(db:Session = Depends(get_db)):
    return list_roles(db)


@router.get("/{role_id}", response_model=RoleRead)
def get_one(role_id:int, db: Session = Depends(get_db)):
    return get_role(db, role_id)

@router.patch("/{role_id}", response_model=RoleRead)
def update_one(role_id:int, payload:RoleUpdate, db:Session= Depends(get_db)):
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return update_role(db, role, payload)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(role_id: int, db: Session = Depends(get_db)):
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rolw not found")
    delete_role(db, role)