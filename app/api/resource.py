from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.resource import create_resource, delete_resource, get_resource, list_resources, update_resource
from app.db.session import get_db
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.core.auth import get_current_user, require_permission

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission('resources','add','any'))])
def create(payload: ResourceCreate, db: Session = Depends(get_db)):
    return create_resource(db, payload)


@router.get("/", response_model=list[ResourceRead],
            dependencies=[Depends(require_permission('resources','read','any'))])
def get_all(db: Session = Depends(get_db)):
    return list_resources(db)


@router.get("/{resource_id}", response_model=ResourceRead,
            dependencies=[Depends(require_permission('resources','read','any'))])
def get_one(resource_id: int, db: Session = Depends(get_db)):
    resource = get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource


@router.patch("/{resource_id}", response_model=ResourceRead,
              dependencies=[Depends(require_permission('resources','udpate','any'))])
def update_one(resource_id: int, payload: ResourceUpdate, db: Session = Depends(get_db)):
    resource = get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return update_resource(db, resource, payload)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_permission('resources','delete','any'))])
def delete_one(resource_id: int, db: Session = Depends(get_db)):
    resource = get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    delete_resource(db, resource)
