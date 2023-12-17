import datetime

from sqlalchemy import Column, MetaData, String, Integer, ForeignKey, TIMESTAMP, Text, Table, Boolean, JSON

from cabinet.models import CabinetTable
from card.models import CardTable

metadata = MetaData()

PushNotifTable = Table(
    'PushNotifTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('types', String),
    Column('status', Boolean, default=False),
    Column('description', String),
    Column('date', TIMESTAMP, default=datetime.datetime.now()),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
)

PushCardTable = Table(
    'PushCardTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('card_id', ForeignKey(CardTable.c.id)),
    Column('push_id', ForeignKey(PushNotifTable.c.id))
)

PushGeoTable = Table(
    'PushGeoTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('coordinates_z', String),
    Column('coordinates_y', String),
)

PushGeoPushTable = Table(
    'PushGeoPushTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('geo_id', ForeignKey(PushGeoTable.c.id)),
    Column('push_id', ForeignKey(PushNotifTable.c.id)),
)
