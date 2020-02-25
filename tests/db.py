from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

conn_str = "postgresql://test:test@localhost:7777/test"
engine = create_engine(conn_str, echo=False)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
