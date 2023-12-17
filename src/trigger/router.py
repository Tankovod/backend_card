import datetime
import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy import insert, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from trigger.models import TriggerTable

router = APIRouter(
    prefix="/trigger",
    tags=['trigger']
)


@router.post('/new')
async def new_trigger(cabinet_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    try:
        id_tr = int(uuid.uuid4())
        title = f"Trigger{str(id_tr)[:4]}"
        query = insert(TriggerTable).values(
            cabinet_id=cabinet_id,
            title=title,
            status=False,
            days_end=0,
            last_date=datetime.datetime.utcnow(),
            segment='null',
            activation={
                "type": "По дате",
                "date": "09.08.2023"
            },
            action='null'
        )

        await session.execute(query)
        await session.commit()
        return {'status': 200, "description": "Триггер создан"}
    except Exception as error:
        return {'status': 500, 'description': str(error)}


@router.get('/all')
async def all_trigger(cabinet_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    query = select(TriggerTable).where(TriggerTable.c.cabinet_id == cabinet_id)

    result = await session.execute(query)
    return result.mappings().all()


@router.get('/current')
async def current_trigger(trigger_id: int, session: AsyncSession = Depends(get_async_session),
                          users: User = Depends(current_user)):
    query = select(TriggerTable).where(or_(TriggerTable.c.id == trigger_id))
    result = await session.execute(query)
    return result.mappings().all()


@router.post('/update')
async def update_trigger(body: Request, session: AsyncSession = Depends(get_async_session),
                         users: User = Depends(current_user)):
    """
    Пример запроса
    {
        "trigger_id": 1,
        "cabinet_id": 1,
        "title": "Trigger292312314",
        "status": false,
        "last_date": "2023-08-09T13:33:58.305684",
        "days_end": 1,
        "segment": "null",
        "activation": {
            "null": "null"
        },
        "action": "null"
    }
    """
    data = await body.json()
    stmt = update(TriggerTable).where(or_(TriggerTable.c.id == data['trigger_id'])).values(
        title=data['title'],
        status=data['status'],
        segment=data['segment'],
        activation=data['activation'],
        days_end=data['days_end'],
        action=data['action']
    )

    await session.execute(stmt)
    await session.commit()


@router.post('/update/status')
async def update_status_trigger(status: bool, trigger_id: int,
                                session: AsyncSession = Depends(get_async_session),
                                users: User = Depends(current_user)):
    stmt = update(TriggerTable).where(or_(
        TriggerTable.c.id == trigger_id
    )).values(status=status)
    await session.execute(stmt)
    await session.commit()
