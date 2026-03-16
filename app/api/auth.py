from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.security import create_access_token, verify_password, create_refresh_token
from app.core.auth import get_current_user
from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.auth import SignupRequest, TokenResponse
from app.schemas.user import UserLogin, UserRead
from app.db.models.refresh_token import RefreshToken


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    return create_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token, jti, expire = create_refresh_token(user.id)
    db.add(
        RefreshToken(user_id = user.id, token=refresh_token, expires_at = expire, created_at = datetime.now())
    )
    db.commit()
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

