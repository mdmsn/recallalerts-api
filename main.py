import os
from fastapi import FastAPI
from src.routes import subscriber, subscriptions, users, recalls
from src import models
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
app.include_router(recalls.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message":"welcome to the recall alerts api developed with FastAPI. Append '/docs' to the url to get started"}