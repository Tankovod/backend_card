import datetime
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from cabinet.models import CabinetTable
from card.models import CardTable
from database import get_async_session
from settings.models import SettingsTable, ValueTable, SettingsValueTable
from settings.utils import generic_public_key

router = APIRouter(
    prefix="/cabinet",
    tags=['Cabinet']
)


@router.post('/new')
async def new_cabinet(login: str,
                      phone: str,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    try:
        apple_id = str(uuid.uuid4())[:12].replace("-", '').upper()
        stmt = insert(CabinetTable).values(
            login=login,
            phone=phone,
            date_end=datetime.datetime.now(),
            balance=0.0,
            user=users.id,
            apple_id=apple_id
        )
        text = """
        Приветствуем в нашей компании!
        предлагаем установить нашу электронную карту 
        """
        cabinet_response = await session.execute(stmt)
        cabinet_id = cabinet_response.inserted_primary_key[0]
        stmt_settings = insert(SettingsTable).values(
            cabinet_id=cabinet_id,
            phone=phone,
            card_number='1001',
            message=text,
            export=False,
            device=1,
            token=str(uuid.uuid4()),
            public_key=generic_public_key()
        )
        settings = await session.execute(stmt_settings)
        settings_id = settings.inserted_primary_key[0]

        # переменная имени

        stmt_value = insert(ValueTable).values(
            name='Имя',
            value='first_name',
            description='Имя клиента'
        )
        result = await session.execute(stmt_value)
        value_id = result.inserted_primary_key[0]

        stmt = insert(SettingsValueTable).values(
            settings_id=settings_id,
            value_id=value_id
        )
        await session.execute(stmt)

        # переменная фамилии

        stmt_value2 = insert(ValueTable).values(
            name='Фамилия',
            value='last_name',
            description='Фамилия клиента'
        )
        result2 = await session.execute(stmt_value2)
        value_id2 = result2.inserted_primary_key[0]

        stmt = insert(SettingsValueTable).values(
            settings_id=settings_id,
            value_id=value_id2
        )
        await session.execute(stmt)

        await session.commit()
        await session.close()
        return {"status": 200, "description": "Кабинет успешно создан"}
    except Exception as error:
        print(error)
        return {"status": 500, "description": "Ошибка внутри сервера"}


@router.get("/cabinet")
async def get_current_cabinet(session: AsyncSession = Depends(get_async_session),
                              users: User = Depends(current_user)):
    try:
        query = select(CabinetTable).where(CabinetTable.c.user == users.id)
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'Не найден кабинет'}


@router.get("/get_current_cabinet")
async def get_current_cabinet_id(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                                 users: User = Depends(current_user)):
    try:
        query = select(CabinetTable).where(CabinetTable.c.user == users.id).where(CabinetTable.c.id == cabinet_id)
        query_card = select(CardTable).where(CardTable.c.cabinet_id == cabinet_id)
        result = await session.execute(query)
        result_card = await session.execute(query_card)
        cabinet = result.mappings().all()
        cards = result_card.mappings().all()
        days_end = (cabinet[0]['date_end'].date() - datetime.datetime.now().date()).days
        if cards:
            data = {
                'id': cabinet[0]['id'],
                'login': cabinet[0]['login'],
                'Tariff': cabinet[0]['Tariff'],
                'days': days_end,
                'card_counts': len(cards),
                'phone': cabinet[0]['phone'],
                'balance': cabinet[0]['balance'],
                'user': cabinet[0]['user'],
            }
        else:
            data = {
                'id': cabinet[0]['id'],
                'login': cabinet[0]['login'],
                'Tariff': cabinet[0]['Tariff'],
                'days': days_end,
                'card_counts': '0',
                'phone': cabinet[0]['phone'],
                'balance': cabinet[0]['balance'],
                'user': cabinet[0]['user'],
            }

        return data
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'Не найден кабинет'}
