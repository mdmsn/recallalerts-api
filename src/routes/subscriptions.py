from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import schemas
from src.security import tokens
from src.controllers import subscriber as subscriber_controller, subscriptions as subscriptions_controller, recalls as recalls_controller
from ..database import get_db


router = APIRouter(
    prefix="/subscription",
    tags=["subscriptions"],
    responses={404: {"detail": "Subscription not found"}},
    dependencies=[Depends(tokens.JWTBearer())]
)


# get subscription by subscription id
@router.get("/", response_model=schemas.Subscription)
def get_subscription_by_id(subscription_id: int, db: Session = Depends(get_db)):
	db_subscription = subscriptions_controller.get_subscription_by_id(db, query_id=subscription_id)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription


# get subscription by product
@router.get("/match/", response_model=schemas.Subscription)
def read_subscription(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	db_subscription = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscriber_id, product=product)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription


# get subscriptions linked to a subscriber id
# and modify schema to receive list itemtypes
# or create new schema for both subscriptions and recalled subscriptions
@router.get("/subscriptions/", response_model=List[schemas.Subscription])
def get_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriptions = subscriptions_controller.get_user_subscriptions(db, query_id=subscriber_id)
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="Subscriptions for this user not found")
	return db_subscriptions


# match new recalls with current subscriptions
@router.get("/product/all/", response_model=List[schemas.Subscription])
def match_recall_to_subscriptions(recalled_product: str, db: Session = Depends(get_db)):
	db_subscriptions = subscriptions_controller.get_subscriptions_by_product(db, product=recalled_product)
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="This recall does not appear in any current subscribed products")
	return db_subscriptions


# subscribe a new product for alerts
# if user hasn't already subscribed the given product
@router.post("/new/", response_model=schemas.Subscription)
def add_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
	db_subscription = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscription.subscriber_id, product=subscription.product)
	if db_subscription:
		raise HTTPException(status_code=400, detail="Product already subscribed for alerts")
	return subscriptions_controller.create_subscription(db=db, subscription=subscription)


# check if a given product (e.g new additon by the user) has been recalled
# create a new recalled subscription row if a recall is found
@router.post("/isrecalled/", response_model=schemas.RecalledSubscription)
def check_recall(product: str, subscription_id: int, subscriber_id: int,  db: Session = Depends(get_db)):
	db_recall = recalls_controller.get_recall_by_name(db, product=product)
	if db_recall is None:
		raise HTTPException(status_code=404, detail="No recalls on this product according to the database")
	recall_id = db_recall.id
	db_new_recalled_sub = subscriptions_controller.new_recalled_subscription(db, subscriber_id = subscriber_id, subscription_id=subscription_id, recall_id=recall_id)
	return db_new_recalled_sub


# get all recalled subscriptions linked to a subscriber id
@router.get("/recalled/",  response_model=List[schemas.RecalledSubscription], tags=["recalls"])
def read_recalled_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber_recalls = subscriber_controller.get_recalled_subs_by_subscriber_id(db, subscriber_id=subscriber_id)
	if not db_subscriber_recalls:
		raise HTTPException(status_code=404, detail="No recalls for this user found")
	return db_subscriber_recalls


## MAYBE MOVE TO RECALLS
# get a specific recalled subscription
# queries recalled_subscription table using
# subscriber id and product name supplied in arguments
@router.get("/recalled-product/", response_model=schemas.Recall, tags=["recalls"])
def read_recalled_subscription(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	sub = subscriptions_controller.get_subscription(db, product=product)
	recalled_sub = subscriptions_controller.get_recalled_subscription(db, subscription_id=sub.id)	
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription not found")	
	return recalls_controller.get_recall(db, recall_id=recalled_sub.recall_id)