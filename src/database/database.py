## python
import logging
import os


## mysql
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker

## secret
from src.secrets.secrets import get_secrets

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)


def retrieve_url_conn():
    global url_con

    secret_name = os.environ.get('SECRET_NAME_DB')
    secret_region = os.environ.get('REGION_SECRET')
        
    secrets = get_secrets(secret=secret_name,region=secret_region)
    password = secrets['password']
    username = secrets['username']
    host = secrets['host']
    database = secrets['database']
    
    url_con = f'mysql+pymysql://{username}:{password}@{host}/{database}'

class DatabaseSession:
    
    __instance = None
    
    def __new__(cls):
        
        if cls.__instance is None:
            print('No existe la instancia')
            engine = create_engine(url=url_con)
            Session = scoped_session(sessionmaker(bind=engine))
            cls.__instance = Session()
        
        print('isando la misma instancia')
        return cls.__instance

    @classmethod
    def execute_query(cls, query, params=None):
        
        results = []
        
        try:
            statement = text(query)
            result = cls.__instance.execute(statement.params(params))
            rows = result.fetchall()
            for row in rows:
                results.append(row._asdict())
            return results 
        except Exception as err:
            print(f'Error executing query: %s' % err)
            
    
    @classmethod
    def insert_row(cls, query, params):
        
        with cls.__instance as conn:
            
            try:
                statement = text(query)
                conn.execute(statement, params)
                conn.commit()
            except Exception as err:
                print("Error inserting row: %s" % err)
                conn.rollback()
