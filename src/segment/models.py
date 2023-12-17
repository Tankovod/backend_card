from sqlalchemy import Table, Column, String, Integer, MetaData, Boolean, ForeignKey, Text, JSON

from cabinet.models import CabinetTable

metadata = MetaData()

SegmentTable = Table(
    'SegmentTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('cabinet_id', ForeignKey(CabinetTable.c.id))
)

CriteriaTable = Table(
    'CriteriaTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('body', JSON)
)

SegmentCategoryTable = Table(
    'SegmentCategoryTable',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('segment_id', ForeignKey(SegmentTable.c.id)),
    Column('criteria_id', ForeignKey(CriteriaTable.c.id))
)
