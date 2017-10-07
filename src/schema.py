from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Table, DateTime

Base = declarative_base()

class User:
    def __init__(self):
        self.__tablename__ = "bus_tracker"
        self.__table__ =  ""

    def add_table_info(self, meta) -> None:
        self.__table__ =  Table(self.__tablename__,
              meta,
              Column("user_name", String, primary_key=True),
              Column("bus_number", String, primary_key=True),
              Column("timestamp", DateTime),
              Column("tracking_status", Boolean),
              Column("last_long", Float),
              Column("last_lat", Float))

