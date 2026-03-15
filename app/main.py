from fastapi import FastAPI

from app.api.role import router as role_router
from app.api.user import router as user_router
from app.api.permission import router as permission_router
from app.api.resource import router as resource_router
from app.api.action import router as action_router
from app.api.user_role import router as user_role_router
from app.api.permission_role import router as permission_role_router
from app.api.auth import router as auth_router



app = FastAPI(title='Custom Authentication system')
app.include_router(role_router)
app.include_router(user_router)
app.include_router(permission_router)
app.include_router(resource_router)
app.include_router(action_router)
app.include_router(user_role_router)
app.include_router(permission_role_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status":"ok"}
