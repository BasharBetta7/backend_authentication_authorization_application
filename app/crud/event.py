from sqlalchemy.orm import Session

from app.schemas.event import EventCreate, EventUpdate, EventDelete
from app.db.models.event import Event


def create_event(db:Session, payload: EventCreate) -> Event:
    obj = Event(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return obj


def update_event(db: Session, event: Event, payload:EventUpdate) -> Event:
    for k,v in payload.model_dump(exclude_unset=True).items():
        setattr(event, k, v)

    db.commit()
    db.refresh(event)
    return event

def get_event(db:Session, event_id:int) -> Event  | None:
    return db.query(Event).filter(Event.id == event_id).first()

def list_events(db:Session) -> list[Event] | None:
    return db.query(Event).all()

def get_event_by_name(db:Session, event_name:str) -> Event | None:
    return db.query(Event).filter(Event.name == event_name).first()


def delete_event(db:Session, event:Event) -> None:
    db.delete(event)
    db.commit()

