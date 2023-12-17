from sqlalchemy import Column, MetaData, String, Integer, ForeignKey
from sqlalchemy.testing.schema import Table

from cabinet.models import CabinetTable

metadata = MetaData()

CardTable = Table(
    'CardTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('card_name', String),
    Column('card_type', String),
    Column('name', String, default='Название шаблона'),
    Column('corp_name', String, default='Название организации'),
    Column('top_text_header', String, default='Заголовок'),
    Column('top_text_content', String, default='Содержимое'),
    Column('top_text_notify', String, default='Уведомление'),
    Column('logo', String),
    Column('background', String),
    Column('icon_push', String),
    Column('color_text', String, default="000000"),
    Column('color_background', String, default="ffffff"),
    Column('color_title', String, default="000000"),
    Column('text_left_header', String, default='Заголовок'),
    Column('text_left_content', String, default='Содержимое'),
    Column('text_left_notify', String, default='Уведомление'),
    Column('text_center_header', String, default='Заголовок'),
    Column('text_center_content', String, default='Содержимое'),
    Column('text_center_notify', String, default='Уведомление'),
    Column('text_right_header', String, default='Заголовок'),
    Column('text_right_content', String, default='Содержимое'),
    Column('text_right_notify', String, default='Уведомление'),
    Column('barcode', String, default='Отсутствует'),
    Column('barcode_code', String, default='Отсутствует'),
    Column('barcode_text', String, default='Отсутствует'),
    Column('tierId', String, default='null'),
    Column('programId', String, default='null'),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)

BackTextTable = Table(
    'BackTextTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('content', String)
)

AdditionTable = Table(
    'AdditionTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('content', String)
)

CardAndBackTextTable = Table(
    'CardAndBackTextTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('back_text_table_id', ForeignKey(BackTextTable.c.id)),
    Column('card_id', ForeignKey(CardTable.c.id))
)

CardAndAdditionTable = Table(
    'CardAndAdditionTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('addition_table_id', ForeignKey(AdditionTable.c.id)),
    Column('card_id', ForeignKey(CardTable.c.id))
)
