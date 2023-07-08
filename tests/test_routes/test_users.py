from tests.fake_user import test_user


def test_create_duplicate_user(client):
    response = client.post(
        "users/register",
         json=test_user
            )
    assert response.status_code == 409
    assert response.json() == {"detail":"Username is taken or subscriber already registered"}


def test_auth_with_wrong_user(client):
    response = client.post(
        "users/auth",
        json={
            "username": test_user["username"],
            "password": "udsid78hjs"
        }
      )
    data = response.json()
    assert response.status_code == 403
    assert data['detail'] == "Username or password is incorrect"