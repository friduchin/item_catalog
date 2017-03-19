from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime


Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name =Column(String(80), nullable=False)
    description = Column(String(250))
    c_date = Column(DateTime, nullable=False, default=datetime.utcnow())
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)


engine = create_engine('sqlite:///itemcatalog.db')


Base.metadata.create_all(engine)
