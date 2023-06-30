## python
import logging
import os
import random


## mysql
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker

## secret
from src.secrets.secrets import get_secrets

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


def retrieve_url_conn(write=False):
    
    secret_name = os.environ.get('SECRET_NAME_DB')
    secret_region = os.environ.get('REGION_SECRET')
        
    secrets = get_secrets(secret=secret_name,region=secret_region)
    password = secrets['password']
    username = secrets['username']
    
    hosts_read = [
        secrets['replica_1'],
        secrets['replica_2'],
    ]
    
    host = random.choice(hosts_read)
    
    if write:
        host = secrets['host']
    
    database = secrets['database']
    
    return  f'mysql+pymysql://{username}:{password}@{host}/{database}'

class DatabaseSession:
    
    __instance = None
        
    def __new__(cls):
        
        if cls.__instance is None:
            url_con = retrieve_url_conn()
            engine = create_engine(url=url_con)
            Session = scoped_session(sessionmaker(bind=engine))
            cls.__instance = Session()
        return cls.__instance

    @classmethod
    def read_session(cls):
        return cls.__instance
    
    @classmethod
    def write_session(cls):
        url_con = retrieve_url_conn(write=True)
        engine = create_engine(url=url_con)
        Session = scoped_session(sessionmaker(bind=engine))
        return Session()

    @classmethod
    def execute_query(cls, query, params=None):
        results = []
        try:
            statement = text(query)
            result = cls.read_session().execute(statement.params(params))
            rows = result.fetchall()
            for row in rows:
                results.append(row._asdict())
            return results 
        except Exception as err:
            print(f'Error executing query: {err}')
            
    @classmethod
    def insert_row(cls, query, params):
        session = cls.write_session()
        try:
            statement = text(query)
            session.execute(statement, params)
            session.commit()
        except Exception as err:
            print(f"Error inserting row: {err}")
            session.rollback()
        finally:
            session.close()