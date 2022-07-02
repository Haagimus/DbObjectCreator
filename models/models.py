from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Unicode, Date, Boolean, JSON, Time, Numeric, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from Models.base import MyMixin, Base


class MyMixin(object):
    @declared_attr
    def get_name(cls):
        return cls.__tablename__


Base = declarative_base()
class city(MyMixin, Base):
    __tablename__ = 'city'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    city_id = Column('sity_id', Integer(), primary_key=True, autoincrement=True)
    city_name = Column('city_name', String(length=450), nullable=False)
    country_id = Column('country_id', Integer(), nullable=False)

    fk_country = Column(Integer(), ForeignKey('facts.country.country_id', ondelete='CASCADE', onupdate='CASCADE'))

class country(MyMixin, Base):
    __tablename__ = 'country'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    country_id = Column('country_id', Integer(), primary_key=True, autoincrement=True)
    name = Column('name', String())
    
class order_status(MyMixin, Base):
    __tablename__ = 'order_status'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    order_status_id = Column('order_status_id', string(length=200), primary_key=True, nullable=False)
    update_at = Column('update_at', Time(timezone=True), nullable=False)
    sale_id = Column('sale_id', varchar(length=200), nullable=False)
    status_name_id = Column('status_name_id', Integer(), nullable=False)

    fk_sale = Column(Integer(), ForeignKey('fact.sale.sale_id', ondelete='CASCADE', onupdate='CASCADE'))
    fk_status_name = Column(Integer(), ForeignKey('fact.status_name.status_name_id', ondelete='CASCADE', onupdate='CASCADE'))

class product(MyMixin, Base):
    __tablename__ = 'product'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    product_id = Column('product_id', Integer(), primary_key=True, autoincrement=True)
    name = Column('name', String(length=250))
    
class sale(MyMixin, Base):
    __tablename__ = 'sale'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    sale_id = Column('sale_id', string(length=250), primary_key=True, nullable=False)
    amount = Column('amount', Numeric(precision=20, scale=3), nullable=False)
    date_sale = Column('sate_sale', Time(timezone=True), nullable=False)
    product_id = Column('product_id', Integer(), nullable=False)
    user_id = Column('user_id', Integer(), nullable=False)
    store_id = Column('store_id', Integer(), nullable=False)

    fk_product = Column(Integer(), ForeignKey('fact.product.product_id', ondelete='CASCADE', onupdate='CASCADE'))
    fk_user = Column(Integer(), ForeignKey('fact.user.user_id', ondelete='CASCADE', onupdate='CASCADE'))
    fk_store = Column(Integer(), ForeignKey('fact.store.store_id', ondelete='CASCADE', onupdate='CASCADE'))

class status_name(MyMixin, Base):
    __tablename__ = 'status_name'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    status_name_id = Column('status_name_id', Integer(), primary_key=True, autoincrement=True)
    status_name = Column('status_name', String(length=450), nullable=False)

class store(MyMixin, Base):
    __tablename__ = 'store'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    store_id = Column('store_id', Integer(), primary_key=True, autoincrement=True)
    name = Column('name', String(length=250), nullable=False)
    city_id = Column('city_id', Integer(), nullable=False)

    fk_city = Column(Integer(), ForeignKey('fact.city.city_id', ondelete='CASCADE', onupdate='CASCADE'))
    
class users(MyMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'fact', 'extend_existing': True}

    user_id = Column('user_id', Integer(), primary_key=True, autoincrement=True)
    name = Column('name', String(length=250), nullable=False)
