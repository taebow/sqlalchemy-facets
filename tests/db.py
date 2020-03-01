from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

conn_str = "postgresql://test:test@localhost:7777/test"
engine = create_engine(conn_str, echo=False)
session = Session(bind=engine)
Base = declarative_base()
