import os
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from src.routes import subscriber, subscriptions, users
from src import models
from src.security import tokens
from src.database import engine
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

allowed_origins = os.getenv('ORIGINS')
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(users.router)
app.include_router(subscriber.router)
app.include_router(subscriptions.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_test_resource():
    return { "welcome to the recall alerts api developed with FastAPI. Append '/docs' to the url to get started" }


# test protected resource access
@app.get("/protected", dependencies=[Depends(tokens.JWTBearer())])
def get_protected_resource():
    return { "message": "protected resource" }