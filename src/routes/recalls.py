from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import schemas
from src.security import tokens
from src.controllers import subscriptions as subscriptions_controller, recalls as recalls_controller
from ..database import get_db


router = APIRouter(
    prefix="/recall",
    tags=["recalls"],
    responses={404: {"detail": "Recall not found"}},
    dependencies=[Depends(tokens.JWTBearer())]
)


# check if a given product (e.g new additon by the user) has been recalled
# create a new recalled subscription row if a recall is found
@router.post("/isrecalled/", response_model=schemas.RecalledSubscription, tags=['subscriptions'])
def check_recall(product: str, subscription_id: int, subscriber_id: int,  db: Session = Depends(get_db)):
	db_recall = recalls_controller.get_recall_by_name(db, product=product)
	if db_recall is None:
		raise HTTPException(status_code=404, detail="No recalls on this product according to the database")
	recall_id = db_recall.id
	db_new_recalled_sub = recalls_controller.new_recalled_subscription(db, subscriber_id = subscriber_id, subscription_id=subscription_id, recall_id=recall_id)
	return db_new_recalled_sub


# get all recalled subscriptions linked to a subscriber id
@router.get("/recalled/",  response_model=List[schemas.RecalledSubscription], tags=["subscriptions"])
def read_recalled_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber_recalls = recalls_controller.get_recalled_subs_by_subscriber_id(db, subscriber_id=subscriber_id)
	if not db_subscriber_recalls:
		raise HTTPException(status_code=404, detail="No recalls for this user found")
	return db_subscriber_recalls


## MAYBE MOVE TO RECALLS
# get a specific recalled subscription
# queries recalled_subscription table using
# subscriber id and product name supplied in arguments
@router.get("/recalled-product/", response_model=schemas.Recall, tags=["subscriptions"])
def read_recalled_subscription(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	sub = subscriptions_controller.match_subscription_to_subscriber(db, query_id=subscriber_id, product=product)
	if sub is None:
		raise HTTPException(status_code=404, detail="Product not matching with user Id")
	recalled_sub = recalls_controller.get_recalled_subscription(db, subscription_id=sub.id)
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription is not recalled")
	return recalls_controller.get_recall(db, recall_id=recalled_sub.recall_id)