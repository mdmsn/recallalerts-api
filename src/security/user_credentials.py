from sqlalchemy.orm import Session
import bcrypt
from .. import models, schemas
from src.controllers import subscriber as subscriber_controller


def hash_password(password: str):
	hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
	hashed_password = hashed_password.decode('utf8')
	return hashed_password

def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.Subscriber = subscriber_controller.get_subscriber(db, username=user.username)
    if db_user_info is None:
          return False
    db_pass = db_user_info.password.encode('utf8')
    request_pass = user.password.encode('utf8')
    return bcrypt.checkpw(request_pass, db_pass)