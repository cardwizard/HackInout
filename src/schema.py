from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float

Base = declarative_base()

class User(Base):
    __tablename__ = 'bus_tracker'
    user_name = Column(String, primary_key=True)
    bus_number = Column(String, primary_key=True)
    tracking_status = Column(Boolean)
    last_long = Column(Float)
    last_lat = Column(Float)

