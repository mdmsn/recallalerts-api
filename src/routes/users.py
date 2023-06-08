from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import schemas
from ..database import get_db
from src.security import tokens, user_credentials
from src.controllers import subscriber as subscriber_controller, subscriptions as subscriptions_controller, users as user_controller

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"detail": "Problem with User"}}
)

ACCESS_TOKEN_EXPIRE_MINUTES = 7200

# register for an account
# first, queries database to see if username already taken
@router.post("/register", response_model=schemas.Subscriber)
def create_subscriber(subscriber: schemas.SubscriberCreate, db: Session = Depends(get_db)):
    db_subscriber = subscriber_controller.get_subscriber(db, username=subscriber.username) #check if user exists first
    if db_subscriber:
        raise HTTPException(status_code=409, detail="Username is taken or subscriber already registered")
    return user_controller.create_user(db=db, user=subscriber)


# authenticate user (e.g. logins)
@router.post("/auth", response_model=schemas.Token)
def authenticate_user(user: schemas.UserAuthenticate, db: Session = Depends(get_db)):
    db_user = subscriber_controller.get_subscriber(db, username=user.username)
    if db_user is None:
        raise HTTPException(status_code=403, detail="Username or password is incorrect")
    else:
        is_password_correct = user_credentials.check_username_password(db=db, user=user)
        if is_password_correct is False:
            raise HTTPException(status_code=403, detail="Username or password is incorrect")
        else:
            from datetime import timedelta
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = tokens.encode_jwt_token(
                data={"sub": user.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "Bearer"}