from fastapi import FastAPI

from app.api.role import router as role_router
from app.api.user import router as user_router



app = FastAPI(title='Custom Authentication system')
app.include_router(role_router)
app.include_router(user_router)

@app.get("/health")
def health_check():
    return {"status":"ok"}