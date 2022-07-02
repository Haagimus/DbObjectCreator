from dateutil.utils import today
from sqlalchemy import Column, Date, MetaData, Time
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()
BaseFactSchema = declarative_base(metadata=MetaData(schema='fact'))
BaseDimensionSchema = declarative_base(metadata=MetaData(schema='dimension'))


class MyBase(Base):
    # @declared_attr
    # def __tablename__(cls):
    #     if cls.__tablename__ is None:
    #         return cls.__name__.lower()
    #     else:
    #         return cls.__tablename__.lower()

    __abstract__ = True  # abstract means no table is created for this class
    date_created = Column('date_created', Date(), default=today().date())
    ts_last_edited = Column('ts_last_edited', Time(timezone=True), default=today().time())
