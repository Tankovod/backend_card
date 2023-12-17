from cabinet.models import CabinetTable
from sqlalchemy import Column, MetaData, String, Integer, ForeignKey
from sqlalchemy.testing.schema import Table

metadata = MetaData()

AppleCertificateTable = Table(
    'AppleCertificateTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('client_id', String),
    Column('pass_id', String),
    Column('team_id', String),
    Column('pass_sn', String, nullable=True),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
)

