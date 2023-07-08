from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas


def get_subscriber(db: Session, username: str):
    return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()


def get_subscriber_by_id(db: Session, query_id: int):
    return db.query(models.Subscriber).filter(models.Subscriber.id == query_id).first()


def get_email(db: Session, query_id: int):
	user = db.query(models.Subscriber).filter_by(models.Subscriber.id == query_id).first()
	return user.email


def update(db: Session, field: str, attribute: str, username: str):
	# changes row in database corresponding to given field name
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.username == username).first()
	match field:
		case "email":
			db_subscriber.email = attribute
		case "mobile":
			db_subscriber.mobile_number = attribute
		case "password":
			db_subscriber.password = attribute
		case "fcm_token":
			db_subscriber.fcm_token = attribute
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber


def update_all(db: Session, updates: schemas.SubscriberUpdate, username: str):
	# updates all personal details (does not include fcm token)
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.username == username).first()
	db_subscriber.email = updates.new_email
	db_subscriber.mobile_number = updates.new_mobile
	db_subscriber.password = updates.new_password
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber


def deactivate_user(db: Session, username: str):
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.username == username).first()
	db_subscriber.deactivated = True
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber


def get_recalled_subs_by_subscriber_id(db: Session, subscriber_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscriber_id == subscriber_id).offset(skip).limit(limit).all()


# add token to database
def update_fcm_token(db: Session, new_fcm_token: str, subscriber_id: int):
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == subscriber_id).first()
	db_subscriber.fcm_token = new_fcm_token
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber