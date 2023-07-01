from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import schemas
from src.security import tokens
from src.controllers import subscriber as subscriber_controller, subscriptions as subscriptions_controller, recalls as recalls_controller
from ..database import get_db


router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    responses={404: {"detail": "Subscription not found"}},
    dependencies=[Depends(tokens.JWTBearer())]
)


# get subscription by subscription id
@router.get("/{subscription_id}", response_model=schemas.Subscription)
def get_subscription_by_id(subscription_id: int, db: Session = Depends(get_db)):
	db_subscription = subscriptions_controller.get_subscription_by_id(db, query_id=subscription_id)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription


# get subscription by product
@router.get("/match/", response_model=schemas.Subscription)
def read_subscription(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber = subscriber_controller.get_subscriber_by_id(db, query_id=subscriber_id)
	if db_subscriber is None:
		raise HTTPException(status_code=404, detail="Incorrect subscriber id provided")
	db_subscription = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscriber_id, product=product)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription


# get subscriptions linked to a subscriber id
# and modify schema to receive list itemtypes
# or create new schema for both subscriptions and recalled subscriptions
@router.get("/all/{subscriber_id}", response_model=List[schemas.Subscription])
def get_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber = subscriber_controller.get_subscriber_by_id(db, query_id=subscriber_id)
	if db_subscriber is None:
		raise HTTPException(status_code=404, detail="Incorrect subscriber id provided")
	db_subscriptions = subscriptions_controller.get_user_subscriptions(db, query_id=subscriber_id)
	if not db_subscriptions:
		raise HTTPException(status_code=200, detail="No subscriptions for this user")
	return db_subscriptions



# subscribe a new product for alerts
# if user hasn't already subscribed the given product
@router.post("/new/", response_model=schemas.Subscription)
def add_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
	db_subscription = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscription.subscriber_id, product=subscription.product)
	if db_subscription:
		raise HTTPException(status_code=400, detail="Product already subscribed for alerts")
	return subscriptions_controller.create_subscription(db=db, subscription=subscription)