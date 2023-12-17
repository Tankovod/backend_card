import datetime

from sqlalchemy import Column, MetaData, String, Integer, ForeignKey, TIMESTAMP, Text
from sqlalchemy.testing.schema import Table

from cabinet.models import CabinetTable

metadata = MetaData()

PaymentOrderTable = Table(
    'PaymentOrderTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('amount', Integer),
    Column('date', TIMESTAMP, default=datetime.datetime.now()),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)

PaymentOrderOfflineTable = Table(
    'PaymentOrderOfflineTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('amount', Integer),
    Column('target', String, default='Отсутсвует'),
    Column('placeholder', String),
    Column('document', String, default='Отсутсвует'),
    Column('date', TIMESTAMP, default=datetime.datetime.now()),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)

PaymentHistoryPayment = Table(
    'PaymentHistoryPayment',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('amount', Integer),
    Column('type', String),
    Column('date', TIMESTAMP, default=datetime.datetime.now()),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)


ContractPaymentTable = Table(
    'ContractPaymentTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('document', Text),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)