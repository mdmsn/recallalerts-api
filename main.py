import os
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, models, schemas, auth
from src.database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

allowed_origins = os.getenv('ORIGINS')

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    """
    Get SQLAlchemy database session
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 7200


@app.get("/")
def get_test_resource():
    return { "message":"welcome to the recall alerts api. Append '/docs' to the url and get started" }


# register for an account
# first, queries database to see if username already taken
@app.post("/users/register", status_code=201, response_model=schemas.Subscriber, tags=["user"])
def create_subscriber(subscriber: schemas.SubscriberCreate, db: Session = Depends(get_db)):
    db_subscriber = crud.get_subscriber(db, username=subscriber.username)
    if db_subscriber:
        raise HTTPException(status_code=409, detail="Username is taken or subscriber already registered")
    return crud.create_user(db=db, user=subscriber)


    
# get subscriber/user details
@app.post("/subscriber/me/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["subscribers"])
def read_subscriber(username:  str, db: Session = Depends(get_db)):
    db_subscriber = crud.get_subscriber(db, username=username)
    if db_subscriber is None:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return db_subscriber



# get subscriber/user details by id
@app.get("/subscriber/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["subscribers"])
def get_subscriber(user_id: int, db: Session = Depends(get_db)):
    db_subscriber = crud.get_subscriber_by_id(db, query_id=user_id)
    if db_subscriber is None:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return db_subscriber



# get subscriptions linked to a subscriber id
# and modify schema to receive list itemtypes
# or create new schema for both subscriptions and recalled subscriptions
@app.get("/subscriber/subscriptions/", dependencies=[Depends(auth.JWTBearer())], response_model=List[schemas.Subscription], tags=["subscribers"])
def get_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriptions = crud.get_user_subscriptions(db, query_id=subscriber_id)
	
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="Subscriptions for this user not found")
	return db_subscriptions



# get subscription by subscription id
@app.get("/subscription/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscription, tags=["subscribers"])
def get_subscription_by_id(subscription_id: int, db: Session = Depends(get_db)):
	db_subscription = crud.get_subscription_by_id(db, query_id=subscription_id)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription



# match new recalls with current subscriptions
@app.get("/match-recalls/", dependencies=[Depends(auth.JWTBearer())], response_model=List[schemas.Subscription], tags=["recalls"])
def match_recalls(product: str, db: Session = Depends(get_db)):
	db_subscriptions = crud.get_subscriptions_by_product(db, product=product)
	
	if not db_subscriptions:
		raise HTTPException(status_code=404, detail="New recalls don't appear in any current subscribed products")
	return db_subscriptions



# get all recalled subscriptions linked to a subscriber id
@app.get("/subscriber/recalls/", dependencies=[Depends(auth.JWTBearer())], response_model=List[schemas.RecalledSubscription], tags=["subscribers", "recalls"])
def read_recalled_subscriptions(subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber_recalls = crud.get_recalled_subs_by_subscriber_id(db, subscriber_id=subscriber_id)
	if not db_subscriber_recalls:
		raise HTTPException(status_code=404, detail="No recalls for this user found")
	
	return db_subscriber_recalls



# get subscription by product
@app.get("/subscriber/subscription/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscription, tags=["subscribers"])
def read_subscription(product: str, db: Session = Depends(get_db)):
	db_subscription = crud.get_subscription(db, product=product)
	if db_subscription is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	return db_subscription


# check if a given product has been recalled
@app.post("/isrecalled/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.RecalledSubscription, tags=["recalls"])
def check_recall(product: str, subscription_id: int, subscriber_id: int,  db: Session = Depends(get_db)):
	db_recall = crud.get_recall_by_name(db, product=product)
	if db_recall is None:
		raise HTTPException(status_code=404, detail="No recalls on this product according to the database")
	recall_id = db_recall.id
	db_new_recalled_sub = crud.new_recalled_subscription(db, subscriber_id = subscriber_id, subscription_id=subscription_id, recall_id=recall_id)
	return db_new_recalled_sub



# subscribe a new product for alerts
# if user hasn't already subscribed the given product
@app.post("/subscriber/new-subscription/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscription, tags=["subscribers"])
def add_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
	db_subscription = crud.get_subscription(db, product=subscription.product)
	if db_subscription:
		raise HTTPException(status_code=400, detail="Product already subscribed for alerts")
	return crud.create_subscription(db=db, subscription=subscription)



# update subscriber's email, 
@app.patch("/subscriber/update-email/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["user"])
def update_email(email: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	#is_user = crud.get_subscriber_by_id(db, id=subscriber.id)
	
	is_user = auth.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	return crud.update(db=db, field="email", attribute=email, username=user.username)


# update user password
@app.post("/subscriber/update-password/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["user"])
def update_password(new_password: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = auth.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	new_hashed_password = auth.hash_password(new_password)
	return crud.update(db=db, field="password", attribute=new_hashed_password, username=user.username)


# update mobile number
@app.patch("/subscriber/update-mobile/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["user"])
def update_mobile(new_mobile: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = auth.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	return crud.update(db=db, field="mobile", attribute=new_mobile, username=user.username)



# update subscriber's password, email and mobile chesks id exists first
@app.post("/subscriber/update-all/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["user"])
def update_all(updates: schemas.SubscriberUpdate, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	#existing_details = crud.get_subscriber_by_id(db, query_id=subscriber.id)
	is_user = auth.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	updates.new_password = auth.hash_password(updates.new_password)
	return crud.update_all(db=db, updates=updates, username=user.username)



# add or update fcm token
@app.patch("/update_fcm/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["user"])
def update_fcm_token(token: str, subscriber_id: int, db: Session = Depends(get_db)):
	db_subscriber = crud.get_subscriber_by_id(db=db,query_id=subscriber_id)
	if db_subscriber is None:
		raise HTTPException(status_code=404, detail="id - not found in database")
	return crud.update_fcm_token(db=db, new_fcm_token=token, subscriber_id=subscriber_id)


# get a specific recalled subscription
# queries recalled_subscription table using
# subscriber id and product name supplied in arguments
@app.get("/subscriber/recalled-product/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Recall, tags=["recalls"])
def read_recalled_subscription(product: str, subscriber_id: int, db: Session = Depends(get_db)):
	sub = crud.get_subscription(db, product=product)
	recalled_sub = crud.get_recalled_subscription(db, subscription_id=sub.id)
	
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	
	return crud.get_recall(db, recall_id=recalled_sub.recall_id)



# get a specific recalled subscription
# queries recalled_subscription table using
# ubscriber id and subscription id supplied in arguments
@app.get("/subscriber/recalled-subscription/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Recall, tags=["subscribers", "recalls"])
def read_recalled_subscription_by_id(subscription_id: int, subscriber_id: int, db: Session = Depends(get_db)):
	recalled_sub = crud.get_recalled_subscription(db, subscription_id=subscription_id)
	
	if recalled_sub is None:
		raise HTTPException(status_code=404, detail="Subscription not found")
	
	return crud.get_recall(db, recall_id=recalled_sub.recall_id)



# set subscriber table deactivated to true on the db
@app.post("/subscriber/deactivate/", dependencies=[Depends(auth.JWTBearer())], response_model=schemas.Subscriber, tags=["subscribers", "user"])
def deactivate_account(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = auth.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	
	return crud.deactivate_user(db=db, username=user.username)



# authenticate user (e.g. logins)
@app.post("/users/auth", response_model=schemas.Token, tags=["user"])
def authenticate_user(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
    db_user = crud.get_subscriber(db, username=user.username)
    if db_user is None:
        raise HTTPException(status_code=403, detail="Username or password is incorrect")
    else:
        is_password_correct = auth.check_username_password(db=db, user=user)
        if is_password_correct is False:
            raise HTTPException(status_code=403, detail="Username or password is incorrect")
        else:
            from datetime import timedelta
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = auth.encode_jwt_token(
                data={"sub": user.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "Bearer"}



# test protected resource access
@app.get("/protected", dependencies=[Depends(auth.JWTBearer())])
def get_protected_resource():
    return { "message": "protected resource" }



from fastapi.middleware.cors import CORSMiddleware

origins = allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
