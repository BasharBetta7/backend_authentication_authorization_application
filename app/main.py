from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.api.role import router as role_router
from app.api.user import router as user_router
from app.api.permission import router as permission_router
from app.api.resource import router as resource_router
from app.api.action import router as action_router
from app.api.user_role import router as user_role_router
from app.api.permission_role import router as permission_role_router
from app.api.auth import router as auth_router
from app.api.event import router as event_router 


from app.db.session import get_db
from app.crud.permission import get_or_create_permission


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db: Session = next(get_db())
    try:
        # Create default permission for users to read their own profile
        get_or_create_permission(db, "users", "read", "own")
        for resource in ("products", "items", "documents"):
            get_or_create_permission(db, resource, "read", "any")
    finally:
        db.close()
    yield
    # Shutdown
    pass


app = FastAPI(title='Custom Authentication system', lifespan=lifespan)
app.include_router(role_router)
app.include_router(user_router)
app.include_router(permission_router)
app.include_router(resource_router)
app.include_router(action_router)
app.include_router(user_role_router)
app.include_router(permission_role_router)
app.include_router(auth_router)
app.include_router(event_router)

@app.get("/health")
def health_check():
    return {"status":"ok"}
