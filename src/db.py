import sqlalchemy
from schema import User
from sqlalchemy import Column, Integer, String, Boolean, Float, Table

def connect(user: str, password: str, db: str, host: str='localhost', port: int=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta

def create_table(table):
    con, meta = connect('postgres', 'AADesh123', 'hackinout')
    base_table = table(meta)

    if not con.dialect.has_table(con, base_table.__tablename__):
        base_table.__table__.create()

def main()->None:
    create_table(User)

if __name__ == '__main__':
    main()