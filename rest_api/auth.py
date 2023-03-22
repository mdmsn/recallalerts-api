import datetime
import time
import bcrypt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from . import models, schemas, crud
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY =  os.getenv("GENERATED_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_TIME_IN_MINUTES = 720

def hash_password(password: str):
	hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
	hashed_password = hashed_password.decode('utf8')
	return hashed_password

def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.Subscriber = crud.get_subscriber(db, username=user.username)
    db_pass = db_user_info.password.encode('utf8')
    request_pass = user.password.encode('utf8')
    return bcrypt.checkpw(request_pass, db_pass)
    

def encode_jwt_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        # Changed from:
        # expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRY_TIME_IN_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM)
    print(decoded_token)
    return decoded_token if decoded_token['exp'] >= time.time() else None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials : HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=401, detail="Invalid authentication code.")

    def verify_jwt(self, jwtToken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt_token(jwtToken)
        except:
            payload = None

        if payload:
            isTokenValid = True
        return isTokenValid

