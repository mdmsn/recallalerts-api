from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from . import models, schemas

# create new user / subscriber
def create_user(db: Session, user: schemas.SubscriberCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf8'), bcrypt.gensalt())
    hashed_password = hashed_password.decode('utf8')
    db_user = models.Subscriber(username=user.username, password=hashed_password, fcm_token=user.fcm_token, email=user.email, mobile_number=user.mobile_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_subscriber(db: Session, username: str):
    return db.query(models.Subscriber).filter(models.Subscriber.username == username).first()
    

def get_subscriber_by_id(db: Session, query_id: int):
    return db.query(models.Subscriber).filter(models.Subscriber.id == query_id).first()


def get_email(db: Session, query_id: int):
	user = db.query(models.Subscriber).filter_by(models.Subscriber.id == query_id).first()
	return user.email


def create_subscriber(db: Session, subscriber: schemas.SubscriberCreate):
    # research hash password + database interaction 
    password = subscriber.password# not really hashed
    db_subscriber = models.Subscriber(username=subscriber.username, fcm_token=subscriber.fcm_token, password=subscriber.password, email=subscriber.email, mobile_number=subscriber.mobile_number)
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber


def get_subscription(db: Session, product: str):
    return db.query(models.Subscription).filter(models.Subscription.product == product).first()

  
def is_subscription(db: Session, product: str):
	return db.query(models.Subscription).filter(models.Subscription.product == product).exists()


def get_subscription_by_id(db: Session, query_id: int):
	return db.query(models.Subscription).filter(models.Subscription.subscriber_id == query_id).first()
	
	
def get_user_subscriptions(db: Session, query_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.Subscription).filter(models.Subscription.subscriber_id == query_id).offset(skip).limit(limit).all()


def get_subscriptions_by_product(db: Session, product: str, skip: int = 0, limit: int = 100):
	return db.query(models.Subscription).filter(models.Subscription.product == product).offset(skip).limit(limit).all()
	

def create_subscription(db: Session, subscription: schemas.SubscriptionCreate):
	# probably should be left to client side code: query db to see if user exists then user their id for subscriber_id
	# if user not in db run create a new subscriber after
	db_subscription = models.Subscription(product=subscription.product, subscriber_id = subscription.subscriber_id, description=subscription.description, subscription_date=subscription.subscription_date)
	db.add(db_subscription)
	db.commit()
	db.refresh(db_subscription)
	return db_subscription


# update subscriber email
def update_all(db: Session, subscriber: models.Subscriber, updates: schemas.SubscriberBase):
    update_data = updates.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(subscriber, key, value)
    db.commit()
    db.refresh(db_subscription)
    return db_subscriber


def update(db: Session, field: str, attribute: str, username: str):
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.username == username).first()
	if field=="email": db_subscriber.email = attribute
	elif field=="mobile": db_subscriber.mobile_number = attribute
	elif field=="password": db_subscriber.password = attribute
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber


def update_all(db: Session, updates: schemas.SubscriberUpdate, username: str):
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


# get recalled sub by subscription id
def get_recalled_subscription(db: Session, subscription_id: int):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscription_id == subscription_id).first()


# get recalled sub linked to subscriber_id
def get_recalled_subs_by_subscriber_id(db: Session, subscriber_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.RecalledSubscription).filter(models.RecalledSubscription.subscriber_id == subscriber_id).offset(skip).limit(limit).all()


def get_recalls(db: Session, product: str):
    return db.query(models.Recall).filter(models.Recall.product == product).all()


# get recall by id
def get_recall(db: Session, recall_id: int):
	return db.query(models.Recall).filter(models.Recall.id == recall_id).first()
	

# get recall by product name
# ideally used to check if a user's subscription
# should also be added to ther recalled subscriptions table
def get_recall_by_name(db: Session, product: str):
	return db.query(models.Recall).filter(models.Recall.product == product).first()
	

# create a recalled subscription for a user
# after a product is found to be present in the recall table
def new_recalled_subscription(db: Session, subscriber_id: int, recall_id: int, subscription_id: int):
	db_recalled_subscription = models.RecalledSubscription(subscription_id=subscription_id, subscriber_id = subscriber_id, recall_id=recall_id)
	db.add(db_recalled_subscription)
	db.commit()
	db.refresh(db_recalled_subscription)
	return db_recalled_subscription


# add token to database
def update_fcm_token(db: Session, new_fcm_token: str, subscriber_id: int):
	db_subscriber = db.query(models.Subscriber).filter(models.Subscriber.id == subscriber_id).first()
	db_subscriber.fcm_token = new_fcm_token
	db.commit()
	db.refresh(db_subscriber)
	return db_subscriber
