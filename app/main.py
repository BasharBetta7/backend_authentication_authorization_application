from fastapi import FastAPI

from app.api.role import router as role_router


app = FastAPI(title='Custom Authentication system')
app.include_router(role_router)

@app.get("/health")
def health_check():
    return {"status":"ok"}