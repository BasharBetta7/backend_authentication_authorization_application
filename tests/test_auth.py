# signup
# login
# logout
# login 
# delete

from fastapi.testclient import TestClient
from uuid import uuid4

from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)

def _u(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def test_auth():
    db = SessionLocal()
    # signup
    email = _u("signup")
    
    response = client.post("/auth/signup",
                           json={
                               "first_name":"fn",
                               "last_name":"ln",
                               "email":email,
                               "password":"password",
                               "confirm_password":"password"
                           })
    assert response.status_code == 201
