from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.schemas.event import EventRead, EventCreate, EventUpdate
from app.crud.event import (
    create_event,
    delete_event,
    get_event,
    list_events,
    update_event,
)

from app.db.session import get_db

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_one(event: EventCreate, db:Session = Depends(get_db)):
    return create_event(db, event)


@router.get("/", response_model=list[EventRead])
def get_all(db: Session = Depends(get_db)):
    return list_events(db)

@router.get("/{event_id:int}", response_model=EventRead)
def get_all(event_id:int, db: Session = Depends(get_db)):
    event = get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.patch("/{event_id:int}", response_model=EventRead)
def update_one(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    event = get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return update_event(db, event, payload)


@router.delete("/{event_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(event_id: int, db: Session = Depends(get_db)):
    event = get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    delete_event(db, event)
