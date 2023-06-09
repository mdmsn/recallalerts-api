from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import schemas
from src.controllers import subscriber as subscriber_controller, subscriptions as subscriptions_controller
from src.security import tokens, user_credentials
from ..database import get_db


router = APIRouter(
    prefix="/subscriber",
    tags=["subscribers"],
    dependencies=[Depends(tokens.JWTBearer())]
)


@router.post("/me/", response_model=schemas.Subscriber)
def read_subscriber(username:  str, db: Session = Depends(get_db)):
    db_subscriber = subscriber_controller.get_subscriber(db, username=username)
    if db_subscriber is None:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return db_subscriber


@router.get("/", response_model=schemas.Subscriber)
def get_subscriber(user_id: int, db: Session = Depends(get_db)):
    db_subscriber = subscriber_controller.get_subscriber_by_id(db, query_id=user_id)
    if db_subscriber is None:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return db_subscriber


@router.patch("/update-email/", response_model=schemas.Subscriber)
def update_email(email: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	return subscriber_controller.update(db=db, field="email", attribute=email, username=user.username)


@router.post("/update-password/", response_model=schemas.Subscriber)
def update_password(new_password: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	new_hashed_password = user_credentials.hash_password(new_password)
	return subscriber_controller.update(db=db, field="password", attribute=new_hashed_password, username=user.username)


@router.patch("/update-mobile/", response_model=schemas.Subscriber)
def update_mobile(new_mobile: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	return subscriber_controller.update(db=db, field="mobile", attribute=new_mobile, username=user.username)


@router.post("/update-all/", response_model=schemas.Subscriber)
def update_all(updates: schemas.SubscriberUpdate, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	# update subscriber's password, email and mobile chesks id exists first
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	updates.new_password = user_credentials.hash_password(updates.new_password)
	return subscriber_controller.update_all(db=db, updates=updates, username=user.username)


@router.patch("/update_fcm/{new_token}", response_model=schemas.Subscriber)
def update_fcm_token(new_token: str, user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=404, detail="Username - password don't match")
	return subscriber_controller.update(db=db, field="fcm_token", attribute=new_token, username=user.username)


# deactivate user's account
# set subscriber table deactivated to true on the db
@router.post("/deactivate/", response_model=schemas.Subscriber)
def deactivate_account(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
	'''
	deactivate user's account
	set subscriber table deactivated to true on the db
	'''
	is_user = user_credentials.check_username_password(db=db, user=user)
	if is_user is False:
		raise HTTPException(status_code=403, detail="Username - password don't match")
	return subscriber_controller.deactivate_user(db=db, username=user.username)