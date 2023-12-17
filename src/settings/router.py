from operator import or_

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from settings.models import SettingsTable, ValueTable, SettingsValueTable, VerifyTable, SettingsVerifyTable, \
    AccessTable, SettingsAccessTable

router = APIRouter(
    prefix="/settings",
    tags=['settings']
)


@router.get("/current")
async def get_all_data(cabinet_id: int,
                       session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    query = select(SettingsTable).where(SettingsTable.c.cabinet_id == cabinet_id)
    request_settings = await session.execute(query)
    response_settings = request_settings.mappings().all()

    query_value = select(ValueTable).where(
        SettingsValueTable.c.settings_id == response_settings[0]['id']
    ).join(ValueTable, SettingsValueTable.c.value_id == ValueTable.c.id)
    request_value = await session.execute(query_value)
    response_value = request_value.mappings().all()

    query_verify = select(VerifyTable).where(
        SettingsVerifyTable.c.settings_id == response_settings[0]['id']
    ).join(VerifyTable, SettingsVerifyTable.c.verify_id == VerifyTable.c.id)

    request_verify = await session.execute(query_verify)
    response_verify = request_verify.mappings().all()

    query_access = select(AccessTable).where(
        SettingsAccessTable.c.settings_id == response_settings[0]['id']
    ).join(AccessTable, SettingsAccessTable.c.access_id == AccessTable.c.id)

    request_access = await session.execute(query_access)
    response_access = request_access.mappings().all()

    if response_value:
        data = {
            "settings": response_settings,
            "value": response_value
        }
        if response_verify:
            data = {
                "settings": response_settings,
                "value": response_value,
                "verify": response_verify
            }
            if response_access:
                data = {
                    "settings": response_settings,
                    "value": response_value,
                    "verify": response_verify,
                    "access": response_access
                }
            else:
                data = {
                    "settings": response_settings,
                    "value": response_value,
                    "verify": response_verify,
                    "access": {}
                }
        else:
            data = {
                "settings": response_settings,
                "value": response_value,
                "verify": {}
            }
    else:
        data = {
            "settings": response_settings,
            "value": {}
        }
    return data


@router.post('/new/value')
async def new_value(settings_id: int,
                    name: str,
                    value: str,
                    description: str,
                    session: AsyncSession = Depends(get_async_session),
                    users: User = Depends(current_user)):
    """
    Создаем переменную в настройках, принчимает settings_id ( ID настроек ) и создает переменную
    """

    stmt_value = insert(ValueTable).values(
        name=name,
        value=value,
        description=description
    )
    result = await session.execute(stmt_value)
    value_id = result.inserted_primary_key[0]

    stmt = insert(SettingsValueTable).values(
        settings_id=settings_id,
        value_id=value_id
    )
    await session.execute(stmt)
    await session.commit()
    return {'status': 200}


@router.post("/update/value")
async def update_value(value_id: int,
                       name: str,
                       value: str,
                       description: str,
                       session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    stmt = update(ValueTable).where(ValueTable.c.id == value_id).values(
        name=name,
        value=value,
        description=description
    )
    await session.execute(stmt)
    await session.commit()
    return {'Изменения сохранены'}


@router.post('/new/verify')
async def new_verify(settings_id: int,
                     types: str,
                     email: str,
                     password: str,
                     token: str,
                     user: str,
                     session: AsyncSession = Depends(get_async_session),
                     users: User = Depends(current_user)):
    """
    Создаем переменную в настройках, принимает settings_id ( ID настроек ) и создает переменную
    """

    stmt_value = insert(VerifyTable).values(
        type=types,
        email=email,
        password=password,
        token=token,
        user=user
    )
    result = await session.execute(stmt_value)
    verify_id = result.inserted_primary_key[0]

    stmt = insert(SettingsVerifyTable).values(
        settings_id=settings_id,
        verify_id=verify_id
    )
    await session.execute(stmt)
    await session.commit()
    return {'status': 200}


@router.post('/new/access')
async def new_access(settings_id: int,
                     email: str,
                     session: AsyncSession = Depends(get_async_session),
                     users: User = Depends(current_user)):
    """
    Создаем переменную в настройках, принимает settings_id ( ID настроек ) и создает переменную
    """

    stmt_access = insert(AccessTable).values(
        email=email
    )
    result = await session.execute(stmt_access)
    access_id = result.inserted_primary_key[0]

    stmt = insert(SettingsAccessTable).values(
        settings_id=settings_id,
        access_id=access_id
    )
    await session.execute(stmt)
    await session.commit()
    return {'status': 200}
