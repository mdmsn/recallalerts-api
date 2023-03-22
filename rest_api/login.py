'''from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas, main, crud

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "64a1c3076606e2283fbf7c3a954c5adbe20d1eb156948276c409954056dd4114"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
'''
'''
class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    disabled: bool

    class Config:
        orm_mode = True



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.on_event("startup")
async def start_db():
    async with models.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, username: str) -> schemas.Subscriber:
    result = await db.execute(select(models.Subscriber).filter_by(username=username))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> schemas.Subscriber:
    user = crud.get_subscriber(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: AsyncSession = Depends(main.get_db), token: str = Depends(oauth2_scheme)) -> schemas.Subscriber:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await crud.get_subscriber(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.Subscriber = Depends(get_current_user)) -> models.Subscriber:
       
    if current_user.deactivated:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(db: AsyncSession = Depends(main.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.Subscriber)
async def read_users_me(current_user: schemas.Subscriber = Depends(get_current_active_user)):
    return current_user
'''

