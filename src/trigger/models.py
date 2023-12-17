from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, JSON

from cabinet.models import CabinetTable

metadata = MetaData()


TriggerTable = Table(
    'TriggerTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
    Column('title', String),
    Column('status', Boolean, default=False),
    Column('last_date', TIMESTAMP),
    Column('segment', String),
    Column('activation', JSON),
    Column('days_end', Integer),
    Column('action', String)
)
