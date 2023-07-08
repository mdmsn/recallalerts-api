from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from .. import models, schemas


def get_recall(db: Session, recall_id: int):
	return db.query(models.Recall).filter(models.Recall.id == recall_id).first()

def new_recall(db: Session, recall: schemas.RecallCreate):
	''''''
	db_recall = models.Recall(
		recall_date = recall.recall_date,
		summary = recall.summary,
		product = recall.product
	)
	db.add(db_recall)
	db.commit()
	db.refresh(db_recall)
	return db_recall


def get_product_recalls(db: Session, product: str):
    '''gets list of recalls for specific product
		a product can be recalled any number of times'''
    return db.query(models.Recall).filter(models.Recall.product == product).all()


def get_recall_by_name(db: Session, product: str):
	'''gets a recall for specific product
		ideally used to check if a user's subscription
		should also be added to the recalled subscriptions table'''
	return db.query(models.Recall).filter(models.Recall.product == product).first()


# get recalled sub by subscription id
def get_recalled_subscription(db: Session, subscription_id: int, subscriber_id):
	return db.query(models.RecalledSubscription).filter(
		models.RecalledSubscription.subscription_id == subscription_id,
		models.RecalledSubscription.subscriber_id == subscriber_id
		).first()


# TODO: perhaps combine it with the above controller
# see update controller in subcriber module
def get_recalled_subs_by_subscriber_id(db: Session, subscriber_id: int):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscriber_id == subscriber_id).all()


# after a product is found to be present in the recall table
# use this to create a recalled subscription for user
def new_recalled_subscription(db: Session, subscriber_id: int, recall_id: int, subscription_id: int):
	db_recalled_subscription = models.RecalledSubscription(
		subscription_id=subscription_id, 
		subscriber_id = subscriber_id, 
		recall_id=recall_id)
	db.add(db_recalled_subscription)
	db.commit()
	db.refresh(db_recalled_subscription)
	return db_recalled_subscription