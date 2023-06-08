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
