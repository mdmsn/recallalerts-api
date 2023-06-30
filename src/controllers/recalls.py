from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from .. import models, schemas


def get_recalls(db: Session, product: str):
    return db.query(models.Recall).filter(models.Recall.product == product).all()


def get_recall(db: Session, recall_id: int):
	return db.query(models.Recall).filter(models.Recall.id == recall_id).first()


# get recall by product name
# ideally used to check if a user's subscription
# should also be added to ther recalled subscriptions table
def get_recall_by_name(db: Session, product: str):
	return db.query(models.Recall).filter(models.Recall.product == product).first()


# get recalled sub by subscription id
def get_recalled_subscription(db: Session, subscription_id: int):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscription_id == subscription_id).first()

# TODO: perhaps combine it with the above controller
# see update controller in subcriber module
def get_recalled_subs_by_subscriber_id(db: Session, subscriber_id: int):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscriber_id == subscriber_id).first()

# after a product is found to be present in the recall table
# use this to create a recalled subscription for user
def new_recalled_subscription(db: Session, subscriber_id: int, recall_id: int, subscription_id: int):
	db_recalled_subscription = models.RecalledSubscription(subscription_id=subscription_id, subscriber_id = subscriber_id, recall_id=recall_id)
	db.add(db_recalled_subscription)
	db.commit()
	db.refresh(db_recalled_subscription)
	return db_recalled_subscription