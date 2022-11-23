from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create engine : create_engine is considered as database url
engine = create_engine("sqlite:///todo.db")
Base = declarative_base()


# Create SessionLocal class from sessionmaker factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


