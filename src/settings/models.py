from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Boolean, ForeignKey

from cabinet.models import CabinetTable

metadata = MetaData()

SettingsTable = Table(
    'SettingsTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
    Column('phone', String),
    Column('language', String),
    Column('card_number', String),
    Column('message', Text),
    Column('export', Boolean),
    Column('device', Integer),
    Column('token', String),
    Column('public_key', String)
)

ValueTable = Table(
    'ValueTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('value', String),
    Column('description', String)
)

SettingsValueTable = Table(
    'SettingsValueTable',
    metadata,
    Column('settings_id', ForeignKey(SettingsTable.c.id)),
    Column('value_id', ForeignKey(ValueTable.c.id))
)

VerifyTable = Table(
    'VerifyTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('type', String),
    Column('email', String),
    Column('password', String),
    Column('token', String),
    Column('user', String)
)

SettingsVerifyTable = Table(
    'SettingsVerifyTable',
    metadata,
    Column('settings_id', ForeignKey(SettingsTable.c.id)),
    Column('verify_id', ForeignKey(VerifyTable.c.id))
)

AccessTable = Table(
    'AccessTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String)
)

SettingsAccessTable = Table(
    'SettingsAccessTable',
    metadata,
    Column('settings_id', ForeignKey(SettingsTable.c.id)),
    Column('access_id', ForeignKey(AccessTable.c.id))
)
