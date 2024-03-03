from db.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32))
    nikename = Column(String(32))
    password = Column(String(32))
    email = Column(String(50))

    