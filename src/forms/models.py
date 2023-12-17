from sqlalchemy import Table, Column, String, Integer, MetaData, Boolean, ForeignKey, Text

from cabinet.models import CabinetTable
from card.models import CardTable

metadata = MetaData()

FormTable = Table(
    'FormTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id)),
    Column('form_name', String),
    Column('link', String),
    Column('title', String),
    Column('description', Text),
    Column('description_block', Boolean, default=False),
    Column('card_id', ForeignKey(CardTable.c.id), nullable=True),
    Column('web_push', String),
    Column('color', String),
    Column('language', String),
    Column('sms', Boolean, default=False),
    Column('call', Boolean, default=False),
    Column('voice', Boolean, default=False),
    Column('telegram', Boolean, default=False),
    Column('phone', String),
    Column('politics', Text),
    Column('ads_link', String),
    Column('ads_form', String),
    Column('ads_button', String),
    Column('ads_form_button', String),
    Column('ads_qr', String),
)

FieldsTable = Table(
    'FieldsTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('middle_name', String),
    Column('string', String),
    Column('error', String),
    Column('power', Boolean, default=False),
    Column('require', Boolean, default=False)
)

FormTableAndFieldsTable = Table(
    'FormTableAndFieldsTable',
    metadata,
    Column('form_id', ForeignKey(FormTable.c.id)),
    Column('fields_id', ForeignKey(FieldsTable.c.id))
)
