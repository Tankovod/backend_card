from fastapi import APIRouter, Depends
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from .models import SegmentTable, CriteriaTable, SegmentCategoryTable
from segment.utils import segment_name_generator

router = APIRouter(
    prefix="/segment",
    tags=['segment']
)


@router.post('/new')
async def new_segment(cabinet_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    await session.execute(insert(SegmentTable).values(
        name=segment_name_generator(),
        cabinet_id=cabinet_id
    ))
    await session.commit()


@router.post('/new/criteria')
async def new_criteria(body: dict,
                       session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    """
    {
    "segment_id": 1,
    "data": {
        "criteria": "Критерия",
        "action": "Сравнение",
        "value": "Значение"
        }
    }
    """
    criteria = await session.execute(
        insert(CriteriaTable).values(
            body=body['data']
        )
    )
    criteria_id = criteria.inserted_primary_key[0]

    await session.execute(insert(SegmentCategoryTable).values(
        segment_id=body['segment_id'],
        criteria_id=criteria_id
    ))

    await session.commit()


@router.get('/all')
async def all_segment(cabinet_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    query = select(SegmentTable, CriteriaTable).where(SegmentTable.c.cabinet_id == cabinet_id). \
        join(SegmentCategoryTable, SegmentTable.c.id == SegmentCategoryTable.c.segment_id). \
        join(CriteriaTable, CriteriaTable.c.id == SegmentCategoryTable.c.criteria_id)
    result = await session.execute(query)
    response = result.mappings().all()
    if response:
        return response
    else:
        result = await session.execute(
            select(SegmentTable).where(SegmentTable.c.cabinet_id == cabinet_id)
        )
        return result.mappings().all()


@router.get('/current')
async def current_segment(segment_id: int,
                          session: AsyncSession = Depends(get_async_session),
                          users: User = Depends(current_user)):
    query = select(SegmentTable, CriteriaTable).where(SegmentTable.c.id == segment_id). \
        join(SegmentCategoryTable, SegmentTable.c.id == SegmentCategoryTable.c.segment_id). \
        join(CriteriaTable, CriteriaTable.c.id == SegmentCategoryTable.c.criteria_id)
    result = await session.execute(query)
    response = result.mappings().all()
    if response:
        return response
    else:
        result = await session.execute(
            select(SegmentTable).where(SegmentTable.c.id == segment_id)
        )
        return result.mappings().all()


@router.post('/update/criteria')
async def update_criteria(body: dict,
                          session: AsyncSession = Depends(get_async_session),
                          users: User = Depends(current_user)):
    """
    {
    "criteria_id": 2,
    "data": {
        "criteria": "Критер2ия",
        "action": "Сравнени3е",
        "value": "Значение4"
        }
    }
    """
    data = body['data']
    updt = update(CriteriaTable).where(CriteriaTable.c.id == body['criteria_id']).values(
        body=data
    )
    await session.execute(updt)
    await session.commit()


@router.post('/update')
async def update_segment(segment_id: int,
                         name: str,
                         session: AsyncSession = Depends(get_async_session),
                         users: User = Depends(current_user)):
    updt = update(SegmentTable).where(SegmentTable.c.id == segment_id).values(
        name=name
    )
    await session.execute(updt)
    await session.commit()


@router.post('/delete/criteria')
async def delete_criteria(criteria_id: int, session: AsyncSession = Depends(get_async_session),
                          users: User = Depends(current_user)):
    stmt_m2m = delete(SegmentCategoryTable).where(SegmentCategoryTable.c.criteria_id == criteria_id)
    await session.execute(stmt_m2m)
    stmt = delete(CriteriaTable).where(CriteriaTable.c.id == criteria_id)
    await session.execute(stmt)
    await session.commit()


@router.post('/delete/segment')
async def delete_segment(segment_id: int, session: AsyncSession = Depends(get_async_session),
                         users: User = Depends(current_user)):
    try:
        query = select(SegmentCategoryTable).where(SegmentCategoryTable.c.segment_id == segment_id)
        result = await session.execute(query)
        response = result.mappings().all()[0]
        del_m2m = delete(SegmentCategoryTable).where(SegmentCategoryTable.c.segment_id == segment_id)
        del_criteria = delete(CriteriaTable).where(CriteriaTable.c.id == response['criteria_id'])
        await session.execute(del_m2m)
        await session.execute(del_criteria)

        stmt = delete(SegmentTable).where(SegmentTable.c.id == segment_id)
        await session.execute(stmt)
        await session.commit()
    except Exception as error:
        stmt = delete(SegmentTable).where(SegmentTable.c.id == segment_id)
        await session.execute(stmt)
        await session.commit()
        print(error)
