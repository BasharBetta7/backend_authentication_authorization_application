from sqlalchemy.orm import Session

from app.db.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate


def create_action(db: Session, payload: ActionCreate) -> Action:
    obj = Action(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_actions(db: Session) -> list[Action]:
    return db.query(Action).all()


def get_action(db: Session, action_id: int) -> Action | None:
    return db.query(Action).filter(Action.id == action_id).first()


def update_action(db: Session, action: Action, payload: ActionUpdate) -> Action:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(action, k, v)
    db.commit()
    db.refresh(action)
    return action


def delete_action(db: Session, action: Action) -> None:
    db.delete(action)
    db.commit()
