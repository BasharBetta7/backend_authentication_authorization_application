from fastapi.testclient import TestClient
from datetime import datetime
from fastapi import status


from app.main import app

client = TestClient(app)

def test_admin_can_add_user():
    # get the token 
    response = client.post("/auth/login",
                            json= {
                               "email":"bashar459@example.com",
                               "password":"bashar"
                           })
    data = response.json()
    acc_token, refresh_token = data["access_token"],data["refresh_token"]

    response = client.post("/users/",
                           headers={"Authorization": f"Bearer {acc_token}"},
                           json={
                                "first_name": "string",
                                "last_name": "string",
                                "email": "user@example.com",
                                "password": "stringst"
                                },)
    assert response.status_code == 201



def test_user_cant_add_user():
    # get the token 
    response = client.post("/auth/login",
                            json= {
                               "email":"ahmad646@example.com",
                               "password":"ahmad"
                           })
    data = response.json()
    acc_token, refresh_token = data["access_token"],data["refresh_token"]

    response = client.post("/users/",
                           headers={"Authorization": f"Bearer {acc_token}"},
                           json={
                                "first_name": "string",
                                "last_name": "string",
                                "email": "user@example.com",
                                "password": "stringst"
                                },)
    assert response.status_code == 403

def test_guest_cant_read_user():
    response = client.get(url="/users/me")
    assert response.status_code == 401


    

def test_user_can_read_user():
    # get the token 
    response = client.post("/auth/login",
                            json= {
                               "email":"ahmad646@example.com",
                               "password":"ahmad"
                           })
    data = response.json()
    acc_token, refresh_token = data["access_token"],data["refresh_token"]

    # send get with auth header
    response = client.get("users/me",headers={"Authorization":f"Bearer {acc_token}"})
    assert response.status_code == 200

def test_user_cant_read_another():
    # get the token 
    response = client.post("/auth/login",
                           json= {
                               "email":"ahmad646@example.com",
                               "password":"ahmad"
                           })
    data = response.json()
    acc_token, refresh_token = data["access_token"],data["refresh_token"]

    # send get with auth header
    response = client.get("users/1",headers={"Authorization":f"Bearer {acc_token}"})
    assert response.status_code == 403



