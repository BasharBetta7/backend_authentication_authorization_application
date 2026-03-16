from fastapi.testclient import TestClient
from datetime import datetime
from fastapi import status



from app.main import app

client = TestClient(app)




def test_create_event():
    response = client.post(url="/events/",
                           json={
                               "name":"Festival",
                               "date":datetime.now().isoformat(),
                               "description":"This is a festival event!, Duh"
                           },
                           )
    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["name"] == "Festival"

def test_update_event():
    response = client.patch(url="events/1",
                            json={
                                "name":"FestivalUpdated"
                            },)
    payload = response.json()
    assert payload["name"] == "FestivalUpdated"
    assert payload["description"] == "This is a festival event!, Duh"

def test_delete_event():
    response = client.delete(url="events/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    

