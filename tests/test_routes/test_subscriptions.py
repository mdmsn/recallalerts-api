from tests.fake_user import test_user, test_header, test_user_registration_response
import logging

logging.basicConfig(level="info")

new_subscription = {
        "product": "Diet Coke 1.25L",
        "description": "Sparkling Low Calorie Soft Drink with Plant Extracts with Sweeteners",
        "subscription_date": "2023-06-16",
        "subscriber_id": test_user_registration_response['id']
    }


def test_get_empty_subscriptions(client):
    response = client.get(f"subscriptions/all/{test_user_registration_response['id']}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 200
    assert data['detail'] == "No subscriptions for this user"


def test_create_subscription(client):
    response = client.post(
        "subscriptions/new/",
        headers=test_header,
        json=new_subscription
    )
    data = response.json()
    assert response.status_code == 200
    print(data)
    test_subscription = {**new_subscription, "id": data['id']}
    assert data == test_subscription
    test_user_registration_response['subscriptions'].append(test_subscription)
    logging.info(test_user_registration_response['subscriptions'])


def test_create_duplicate_subscription(client):
    response = client.post(
        "subscriptions/new/",
        headers=test_header,
        json=new_subscription
    )
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == "Product already subscribed for alerts"


def test_get_subscription_by_id(client):
    test_sub = test_user_registration_response['subscriptions'][0]
    response = client.get(
        f"subscriptions/{test_sub['id']}",
        headers=test_header
        )
    data = response.json()
    assert response.status_code == 200
    assert data == test_sub


def test_get_subscription_by_wrong_id(client):
    response = client.get(
        "subscriptions/2",
        headers=test_header
        )
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "Subscription not found"


def test_get_subscription_by_product(client):
    response = client.get(f"subscriptions/match/?product={new_subscription['product']}&subscriber_id={new_subscription['subscriber_id']}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 200
    assert data == test_user_registration_response['subscriptions'][0]


def test_match_subscription_by_wrong_product(client):
    product = "Diet Pepsi Cola 250ml"
    response = client.get(f"subscriptions/match/?product={product}&subscriber_id={new_subscription['subscriber_id']}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "Subscription not found"


def test_match_subscription_by_wrong_id(client):
    wrong_id = 9
    response = client.get(f"subscriptions/match/?product={new_subscription['product']}&subscriber_id={wrong_id}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "Incorrect subscriber id provided"


def test_get_subscriptions(client):
    response = client.get(f"subscriptions/all/{test_user_registration_response['id']}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 200
    assert data == test_user_registration_response['subscriptions']


def test_get_subscriptions_wrong_id(client):
    wrong_id = 900
    response = client.get(f"subscriptions/all/{wrong_id}",
                          headers=test_header)
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == "Incorrect subscriber id provided"