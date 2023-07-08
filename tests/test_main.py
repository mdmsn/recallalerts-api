from .fake_user import test_user, test_user_registration_response, test_header, test_user_number_2, test_user_number_2_registration_response, test_header_number_2


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message":"welcome to the recall alerts api developed with FastAPI. Append '/docs' to the url to get started"
        }



def test_create_test_user(client):
    #This will be used throughout testing
    response = client.post(
        "users/register",
         json=test_user
            )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == test_user_registration_response
    test_user['id'] = response.json()['id']


def test_existing_user_auth(client):
    response = client.post(
        "users/auth",
        json={
            "username": test_user["username"],
            "password": test_user["password"]
        }
      )
    data = response.json()
    print(test_user)
    assert response.status_code == 200
    print(response)
    assert data['token_type'] == "Bearer"
    assert len(data['access_token']) != 0
    token = data['access_token']
    test_header["Authorization"] = f"Bearer {token}"





def test_create_test_user_2(client):
    #This will be used for testing unauthorised access
    response = client.post(
        "users/register",
         json=test_user_number_2
            )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == test_user_number_2_registration_response
    test_user_number_2['id'] = response.json()['id']


def test_user_number_2_auth(client):
    response = client.post(
        "users/auth",
        json={
            "username": test_user_number_2["username"],
            "password": test_user_number_2["password"]
        }
      )
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == "Bearer"
    assert len(data['access_token']) != 0
    token = data['access_token']
    test_header_number_2["Authorization"] = f"Bearer {token}"