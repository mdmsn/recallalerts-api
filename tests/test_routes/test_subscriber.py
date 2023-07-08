from tests.fake_user import test_user, test_header


def test_get_subscriber(client):
    test_username = test_user['username']
    print(test_username)
    response = client.post(
        f"subscriber/me/?username={test_username}", headers=test_header)
    print(test_user)
    print(response.json())
    assert response.status_code == 200


def test_get_subscriber_by_id(client):
    response = client.get("subscriber/?user_id=1", headers=test_header)
    print(response.json())
    assert response.status_code == 200


def test_get_subscriber_with_wrong_id(client):
    response = client.get("subscriber/?user_id=100", headers=test_header)
    assert response.status_code == 404
    assert response.json()['detail'] == "Subscriber not found"


def test_update_subscriber_email(client):
    new_email = "new@mail.com"
    response = client.patch(f"subscriber/update-email/?email={new_email}",
                            headers=test_header,
                            json={
                                "username": test_user['username'],
                                "password": test_user['password']
                            }
                            )
    assert response.status_code == 200
    assert response.json()['email'] == new_email


def test_update_subscriber_email_with_wrong_login(client):
    new_email = "new@mail.com"
    response = client.patch(f"subscriber/update-email/?email={new_email}",
                            headers=test_header,
                            json={
                                "username": "jvAA",
                                "password": "hgjvKYVG8fgH"
                            }
                            )
    assert response.status_code == 403
    assert response.json()['detail'] == "Username - password don't match"


def test_update_subscriber_password(client):
    new_mobile_num = "0937244354"
    response = client.patch(f"subscriber/update-mobile/?new_mobile={new_mobile_num}",
                            headers=test_header,
                            json={
                                "username": test_user['username'],
                                "password": test_user['password']
                            }
                            )
    assert response.status_code == 200
    assert response.json()['mobile_number'] == new_mobile_num


def test_update_subscriber_password_wrong_login(client):
    new_mobile_num = "0937244354"
    response = client.patch(f"subscriber/update-mobile/?new_mobile={new_mobile_num}",
                            headers=test_header,
                            json={
                                "username": "jh",
                                "password": "jh8ASAn8w"
                            }
                            )
    assert response.status_code == 403
    assert response.json()['detail'] == "Username - password don't match"


def test_update_all_subscriber_details(client):
    new_details = {
        "new_password": "92hd98sKS8h",
        "new_email": "new@new.mail",
        "new_mobile": "0779372422"
    }
    response = client.post("subscriber/update-all",
                           headers=test_header,
                           json={
                               "updates": new_details,
                               "user": {
                                   "username": test_user['username'],
                                   "password": test_user['password']
                               }
                           })
    assert response.status_code == 200
    data = response.json()
    assert data['email'] == new_details['new_email']
    assert data['mobile_number'] == new_details['new_mobile']

    # Make sure password was changed in the db
    check_user = client.post(
        "users/auth",
        json={
            "username": test_user["username"],
            "password": new_details['new_password']
        }
    )
    check_user_data = check_user.json()
    assert check_user.status_code == 200
    assert check_user_data['token_type'] == "Bearer"
    assert len(check_user_data['access_token']) != 0
    token = check_user_data['access_token']
    test_header["Authorization"] = f"Bearer {token}"
    test_user['password'] = new_details['new_password']


def test_update_subscriber_fcm(client):
    new_fcm = "if76df5rv76byth98"
    response = client.patch(f"subscriber/update_fcm/{new_fcm}",
                            headers=test_header,
                            json={                            
                                "username": test_user['username'],
                                "password": test_user['password']  
                            }
                            )
    assert response.status_code == 200
    assert response.json()['fcm_token'] == new_fcm


def test_update_subscriber_fcm_token_with_wrong_login(client):
    new_fcm = "if76df5rv76byth98"
    response = client.patch(f"subscriber/update_fcm/{new_fcm}",
                            headers=test_header,
                            json={
                                "username": "hdjs9",
                                "password": "HkjHJjhKH96H"
                            }
                            )
    assert response.status_code == 404
    assert response.json()['detail'] == "Username - password don't match"


def test_deactivate_user(client):
    response = client.post(
        "subscriber/deactivate",
        headers=test_header,
        json={
            "username": test_user["username"],
            "password": test_user['password']
        }
    )
    assert response.status_code == 200
    assert response.json()['deactivated']


def test_deactivate_user_with_wrong_login(client):
    response = client.post(
        "subscriber/deactivate",
        headers=test_header,
        json={
            "username": "kjsk",
            "password": test_user['password']
        }
    )
    assert response.status_code == 403
    assert response.json()['detail'] == "Username - password don't match"
