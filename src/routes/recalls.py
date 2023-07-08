from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import schemas
from src.security.user_credentials import check_user_role
from src.security import tokens
from src.controllers import subscriptions as subscriptions_controller, recalls as recalls_controller, subscriber as subscriber_controller
from ..database import get_db


router = APIRouter(
    prefix="/recalls",
    tags=["recalls"],
    responses={404: {"detail": "Recall not found"}},
    dependencies=[Depends(tokens.JWTBearer())]
)


# TODO add a get recall with recall id 
@router.get("/{id}", response_model=schemas.Recall)
def get_recall_with_id(id: int, db: Session = Depends(get_db)):
	db_recall = recalls_controller.get_recall(db, recall_id=id)
	if db_recall is None:
		raise HTTPException(status_code=404, detail="No recall associated with this id")
	return db_recall



@router.post("/new", response_model=schemas.Recall)
def add_new_recall(user: schemas.UserAuthenticate , recall: schemas.RecallCreate, db: Session = Depends(get_db)):
	'''
	add new recall
	only accesible from backend and admins etc
	'''
	db_user = subscriber_controller.get_subscriber(db, username=user.username)
	if db_user is None:
		raise HTTPException(status_code=403, detail="User not authourised to add recall")
	is_allowed = check_user_role(user_id=db_user.id)
	if is_allowed is False:
		raise HTTPException(status_code=403, detail="User not authourised to add recall")
	db_recall = recalls_controller.new_recall(db, recall=recall)
	if db_recall is None:
		raise HTTPException(status_code=403, detail="Something went wrong")
	return db_recall



# TODO get recall
# add a get recall with recall id
# appears in any subscriptions
# and then return list of subscriptions that do
@router.get("/{product}", response_model=List[schemas.Recall])
def get_recalls_for_product(product: str, db: Session = Depends(get_db)):
	db_subscriptions = recalls_controller.get_product_recalls(db, product=product)
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="This recall does not appear in any current subscribed products")
	return db_subscriptions

# check if a given product (e.g new additon by the user) has been recalled
# create a new recalled subscription row if a recall is found
@router.post("recalled-subscriptions/new", response_model=schemas.RecalledSubscription, tags=['subscriptions'])
def add_new_recalled_subscription(product: str, subscription_id: int, subscriber_id: int,  db: Session = Depends(get_db)):
	db_recall = recalls_controller.get_recall_by_name(db, product=product)
	if db_recall is None:
		raise HTTPException(status_code=404, detail="No recalls on this product according to the database")
	recall_id = db_recall.id
	db_new_recalled_sub = recalls_controller.new_recalled_subscription(db, subscriber_id = subscriber_id, subscription_id=subscription_id, recall_id=recall_id)
	return db_new_recalled_sub


# check if a recalled product
# appears in any subscriptions
# and then return list of subscriptions that do
@router.get("/subscriptions/{product}", response_model=List[schemas.Subscription])
def match_recall_to_subscriptions(product: str, db: Session = Depends(get_db)):
	db_subscriptions = subscriptions_controller.get_subscriptions_by_product(db, product=product)
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="This recall does not appear in any current subscribed products")
	return db_subscriptions


# get all recalled subscriptions linked to a subscriber id
@router.get("/recalled-subscriptions/{subscriber_id}",  response_model=List[schemas.RecalledSubscription], tags=["subscriptions"])
def read_recalled_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber_recalls = recalls_controller.get_recalled_subs_by_subscriber_id(db, subscriber_id=subscriber_id)
	if not db_subscriber_recalls:
		raise HTTPException(status_code=404, detail="No recalls for this user found")
	return db_subscriber_recalls



# get recall details from recalkl table
# for a specific recalled subscription
# Used only if no id for the recalled subscription is provided
# queries recalled_subscription table using
# subscriber id and subscription id is supplied in arguments
# and queries recalls table using the recall id returned
@router.get("/recalled-subscriptions", response_model=schemas.Recall, tags=["subscriptions"])
def get_recall_details_for_subscription(subscription_id: int, subscriber_id: int, db: Session = Depends(get_db)):
	recalled_sub = recalls_controller.get_recalled_subscription(db, subscription_id=subscription_id, subscriber_id=subscriber_id)
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription is not recalled")
	return recalls_controller.get_recall(db, recall_id=recalled_sub.recall_id)


# MAYBE MOVE TO RECALLS
# get a specific recalled subscription
# Used only if product name and user id is provied
# queries subscription table to get subscription id
# queries recalled subscriptions table for recalled subscription id
# lastly queries recalls table using returned ids
# and returns recall details
@router.get("/recalled-subscriptions", response_model=schemas.Recall, tags=["subscriptions"])
def get_recall_details_for_subscribed_product(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	sub = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscriber_id, product=product)
	if sub is None:
		raise HTTPException(status_code=404, detail="Product not matching with user Id")
	recalled_sub = recalls_controller.get_recalled_subscription(db, subscription_id=sub.id, subscriber_id=subscriber_id)
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription is not recalled")
	return recalls_controller.get_recall(db, recall_id=recalled_sub.recall_id)
