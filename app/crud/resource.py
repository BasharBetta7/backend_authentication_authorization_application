from sqlalchemy.orm import Session

from app.db.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate


def create_resource(db: Session, payload: ResourceCreate) -> Resource:
    obj = Resource(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_resources(db: Session) -> list[Resource]:
    return db.query(Resource).all()


def get_resource(db: Session, resource_id: int) -> Resource | None:
    return db.query(Resource).filter(Resource.id == resource_id).first()


def get_resource_by_name(db: Session, name: str) -> Resource | None:
    return db.query(Resource).filter(Resource.name == name).first()


def update_resource(db: Session, resource: Resource, payload: ResourceUpdate) -> Resource:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(resource, k, v)
    db.commit()
    db.refresh(resource)
    return resource


def delete_resource(db: Session, resource: Resource) -> None:
    db.delete(resource)
    db.commit()
