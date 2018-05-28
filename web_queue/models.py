from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from web_queue.utils import singleton

Base = declarative_base()


class Queue(Base):
    __tablename__ = 'queue'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    params = Column(String(1000))
    worker = Column(String(10))

    def __repr__(self):
        return 'Task %s' % (self.name)


class Results(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    status = Column(String(10))
    result = Column(String(1000))



@singleton
class DB(object):

    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, pool_size=20, max_overflow=0)

    def get_session(self):
        session_factory = sessionmaker(autocommit=False, autoflush=True, bind=self.engine)
        session = scoped_session(session_factory)
        return session()

    @staticmethod
    def lock_db_sql():
        sql = 'BEGIN EXCLUSIVE;'
        return sql


