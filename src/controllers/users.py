from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from .. import models, schemas

# create new user / subscriber
def create_user(db: Session, user: schemas.SubscriberCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf8'), bcrypt.gensalt())
    hashed_password = hashed_password.decode('utf8')
    db_user = models.Subscriber(username=user.username, password=hashed_password, fcm_token=user.fcm_token, email=user.email, mobile_number=user.mobile_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user