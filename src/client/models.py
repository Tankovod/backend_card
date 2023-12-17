from sqlalchemy import Table, MetaData, Column, Integer, JSON, ForeignKey, String

from cabinet.models import CabinetTable
from forms.models import FormTable

metadata = MetaData()

ClientTable = Table(
    'ClientTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('form_id', ForeignKey(FormTable.c.id)),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
    Column('data', JSON),
    Column('google_wallet_url', String),
    Column('apple_wallet_url', String)
)
