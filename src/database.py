from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re
from dotenv import load_dotenv

load_dotenv()

db_URL = os.getenv("DATABASE_URL") 

if db_URL.startswith("postgres://"):
    db_URL = db_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Get SQLAlchemy database session
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
