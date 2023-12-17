from sqlalchemy import Column, MetaData, String, Integer, Float, ForeignKey, TIMESTAMP
from sqlalchemy.testing.schema import Table

from auth.models import User

metadata = MetaData()

CabinetTable = Table(
    'CabinetTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('login', String, nullable=False),
    Column('Tariff', String, default='Не выбран'),
    Column('date_end', TIMESTAMP),
    Column('phone', String),
    Column('balance', Float, default=0.0),
    Column('user', ForeignKey(User.id)),
    Column('apple_id', String)
)

