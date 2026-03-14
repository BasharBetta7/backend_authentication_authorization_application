from fastapi import FastAPI

app = FastAPI(title='Custom Authentication system')

@app.get("/health")
def health_check():
    return {"status":"ok"}