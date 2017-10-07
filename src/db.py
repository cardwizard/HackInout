import sqlalchemy

from sqlalchemy import Column, Integer, String, Boolean, Float, Table
from typing import Dict, List
from schema import User
from datetime import datetime

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
    base_table = table()

    if not con.dialect.has_table(con, base_table.__tablename__):
        base_table.add_table_info(meta)
        base_table.__table__.create()


def insert_values(table, values: List[Dict]):
    con, meta = connect('postgres', 'AADesh123', 'hackinout')
    base_table = table()
    table = meta.tables[base_table.__tablename__]
    try:
        # Try to insert if it is new.
        con.execute(table.insert(), values)
    except:
        # If it is not, update the row.
        con.execute(table.update(), values)

def main()->None:
    create_table(User)
    insert_values(User, [{"user_name": "Aadesh", "bus_number": "KA 01 AB 1994", "tracking_status": True,
                          "last_lat": 19.09, "last_long": 20.1, "timestamp": datetime.now()}])

if __name__ == '__main__':
    main()