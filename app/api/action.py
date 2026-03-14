from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.action import create_action, delete_action, get_action, list_actions, update_action
from app.db.session import get_db
from app.schemas.action import ActionCreate, ActionRead, ActionUpdate

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/", response_model=ActionRead, status_code=status.HTTP_201_CREATED)
def create(payload: ActionCreate, db: Session = Depends(get_db)):
    return create_action(db, payload)


@router.get("/", response_model=list[ActionRead])
def get_all(db: Session = Depends(get_db)):
    return list_actions(db)


@router.get("/{action_id}", response_model=ActionRead)
def get_one(action_id: int, db: Session = Depends(get_db)):
    action = get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    return action


@router.patch("/{action_id}", response_model=ActionRead)
def update_one(action_id: int, payload: ActionUpdate, db: Session = Depends(get_db)):
    action = get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    return update_action(db, action, payload)


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one(action_id: int, db: Session = Depends(get_db)):
    action = get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    delete_action(db, action)
