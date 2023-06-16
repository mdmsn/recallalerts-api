from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas


def create_subscription(db: Session, subscription: schemas.SubscriptionCreate):
	# probably should be left to client side code: query db to see if user exists then user their id for subscriber_id
	# if user not in db run create a new subscriber after
	db_subscription = models.Subscription(product=subscription.product, subscriber_id = subscription.subscriber_id, description=subscription.description, subscription_date=subscription.subscription_date)
	db.add(db_subscription)
	db.commit()
	db.refresh(db_subscription)
	return db_subscription


def get_subscription(db: Session, product: str):
    return db.query(models.Subscription).filter(models.Subscription.product == product).first()


def is_subscription(db: Session, product: str):
	return db.query(models.Subscription).filter(models.Subscription.product == product).exists()


def get_subscription_by_id(db: Session, query_id: int):
	return db.query(models.Subscription).filter(models.Subscription.subscriber_id == query_id).first()


def match_subscription_to_subscriber(db: Session, query_id: int, product: str):
	return db.query(models.Subscription).filter(models.Subscription.subscriber_id == query_id, models.Subscription.product == product).first()


def get_user_subscriptions(db: Session, query_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.Subscription).filter(models.Subscription.subscriber_id == query_id).offset(skip).limit(limit).all()


def get_subscriptions_by_product(db: Session, product: str, skip: int = 0, limit: int = 100):
	return db.query(models.Subscription).filter(models.Subscription.product == product).offset(skip).limit(limit).all()


# get recalled sub by subscription id
def get_recalled_subscription(db: Session, subscription_id: int):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscription_id == subscription_id).first()


# after a product is found to be present in the recall table
# use this to create a recalled subscription for user
def new_recalled_subscription(db: Session, subscriber_id: int, recall_id: int, subscription_id: int):
	db_recalled_subscription = models.RecalledSubscription(subscription_id=subscription_id, subscriber_id = subscriber_id, recall_id=recall_id)
	db.add(db_recalled_subscription)
	db.commit()
	db.refresh(db_recalled_subscription)
	return db_recalled_subscription