from tests.fake_user import test_user, test_header, test_user_number_2, test_header_number_2
from datetime import date

recall_date = str(date.today())


'''
TODO
ADD A RECALLTO RECALL TABLE OR TESTING
RECALL TABLE IS EMPTY AND 
NO CONTROLLER/ROUTES EXIST FOR THIS
'''


def test_new_recall(client):
    new_recall = {
        "product": "pepsi 250",
        "summary": "somethij kjhsd kj",
        "recall_date": recall_date
    }
    response = client.post("recalls/new",
                           headers=test_header,
                           json={
                               "recall": new_recall,
                               "user": {
                                   "username": test_user['username'],
                                   "password": test_user['password']
                               }

                           })
    print(response)
    data = response.json()
    assert response.status_code == 200
    assert data == { **new_recall, "id": data['id'] }



def test_new_recall_unauthourised_user(client):
    new_recall = {
        "product": "pepsi 250",
        "summary": "somethij kjhsd kj",
        "recall_date": recall_date
    }
    response = client.post("recalls/new",
                           headers=test_header_number_2,
                           json={
                               "recall": new_recall,
                               "user": {
                                   "username": test_user_number_2['username'],
                                   "password": test_user_number_2['password']
                               }

                           })
    print(response)
    data = response.json()
    assert response.status_code == 403
    #assert data == { **new_recall, "id": data['id'] }
    assert data['detail'] == "User not authourised to add recall"



def test_new_recall_wrong_user_details(client):
    pass



def test_get_recall_by_id(client):
    pass



def test_test_get_recall_by_wrong_id(client):
    pass