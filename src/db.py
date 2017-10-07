import sqlalchemy

from sqlalchemy import Column, Integer, String, Boolean, Float, Table
from typing import Dict, List

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
        pass

def select_values(table, values: List[Dict]):
    con, meta = connect('postgres', 'AADesh123', 'hackinout')
    base_table = table()
    table = meta.tables[base_table.__tablename__]

    cmd = table.select().where(table.c[list(values[0].keys())[0]] == list(values[0].values())[0])

    for commands in values[1:]:
        cmd = cmd.where(table.c[list(commands.keys())[0]] == list(commands.values())[0])

    rows = con.execute(cmd)

    return rows

def main()->None:
    create_table(User)
    to_insert = [{"user_name": "Deepika", "bus_number": "KA 01 AB 1994", "tracking_status": True, "route_number": "341H",
                          "last_lat": 12.9734115802915, "last_long": 77.5962565802915, "timestamp": datetime.now()}]
    insert_values(User, to_insert)
#     to_select = [{"bus_number": "KA 01 AB 1994"}, {"user_name": "Aadesh"}]
#     select_values(User, to_select)


if __name__ == '__main__':
    from schema import User
    main()