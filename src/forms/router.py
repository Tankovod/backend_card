from fastapi import APIRouter, Depends, Request
from sqlalchemy import insert, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from forms.models import FormTable, FieldsTable, FormTableAndFieldsTable
from forms.utils import form_name_generator

router = APIRouter(
    prefix="/form",
    tags=['form']
)


@router.post('/new')
async def create_new_form(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                          users: User = Depends(current_user)):
    try:
        stmt = insert(FormTable).values(
            cabinet_id=cabinet_id,
            form_name=form_name_generator(),
            link='2',
            title='Текст',
            description='Текст',
            web_push='Веб пуши',
            color='00000',
            language='Русский',
            phone='+79999999999',
            politics='null',
            ads_link='null',
            ads_form='null',
            ads_button='null',
            ads_qr='null',

        )
        form_response = await session.execute(stmt)
        form_id = form_response.inserted_primary_key[0]

        # Вставка записи в таблицу имени
        field_first_stmt = insert(FieldsTable).values(
            name='Имя',
            middle_name='first_name',
            string='Строка',
            error='Ошибка',
            power=False,
            require=False
        )
        field_first_response = await session.execute(field_first_stmt)
        field_first_id = field_first_response.inserted_primary_key[0]

        # Вставка записи в таблицу CardAndBackTextTable
        form_and_field_first_stmt = insert(FormTableAndFieldsTable).values(
            form_id=form_id,
            fields_id=field_first_id
        )

        # Вставка записи в таблицу Фамилии
        field_last_stmt = insert(FieldsTable).values(
            name='Фамилия',
            middle_name='last_name',
            string='Строка',
            error='Ошибка',
            power=False,
            require=False
        )
        field_last_response = await session.execute(field_last_stmt)
        field_last_id = field_last_response.inserted_primary_key[0]

        # Вставка записи в таблицу CardAndBackTextTable
        form_and_field_last_stmt = insert(FormTableAndFieldsTable).values(
            form_id=form_id,
            fields_id=field_last_id
        )
        await session.execute(form_and_field_first_stmt)
        await session.execute(form_and_field_last_stmt)
        await session.commit()
        return {'status': 200, 'description': 'Форма создана'}
    except Exception as error:
        print(error)


@router.get('/all')
async def get_all_form(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    try:
        query = select(FormTable).where(FormTable.c.cabinet_id == cabinet_id)
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as error:
        print(error)


@router.get('/current')
async def get_current_form(form_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(FormTable).where(FormTable.c.id == form_id)
        result = await session.execute(query)
        response = result.mappings().all()[0]
        data = {
            "id": response['id'],
            "cabinet_id": response['cabinet_id'],
            "form_name": response['form_name'],
            "link": response['link'],
            "title": response['title'],
            "description": response['description'],
            "description_block": response['description_block'],
            "card_id": response['card_id'],
            "web_push": response['web_push'],
            "color": response['color'],
            "language": response['language'],
            "sms": response['sms'],
            "call": response['call'],
            "voice": response['voice'],
            "telegram": response['telegram'],
            "phone": response['phone'],
            "politics": response['politics'],
            "ads_link": f"https://platforma.oppti.me/form?form_id={form_id}&cabinet_id={response['cabinet_id']}",
            "ads_form": "null",
            "ads_button": "null",
            "ads_form_button": "null",
            "ads_qr": "null"
        }
        return [data]
    except Exception as error:
        print(error)


@router.post('/update')
async def update_form(form_id: int, form_name: str, title: str, description: str, description_block: bool,
                      card_id: int, web_push: str, color: str, language: str, sms: bool, call: bool,
                      voice: bool, telegram: bool, phone: str, politics: str,
                      session: AsyncSession = Depends(get_async_session), users: User = Depends(current_user)):
    try:
        stmt = update(FormTable).where(FormTable.c.id == form_id).values(
            form_name=form_name,
            title=title,
            description=description,
            description_block=description_block,
            card_id=card_id,
            web_push=web_push,
            color=color,
            language=language,
            sms=sms,
            call=call,
            voice=voice,
            telegram=telegram,
            phone=phone,
            politics=politics
        )
        await session.execute(stmt)
        await session.commit()
    except Exception as error:
        print(error)


@router.post('/field/new')
async def field_new(form_id: int, name: str, middle_name: str, string: str, error: str, power: bool, require: bool,
                    session: AsyncSession = Depends(get_async_session), users: User = Depends(current_user)):
    try:
        # Вставка записи в таблицу BackTextTable
        field_stmt = insert(FieldsTable).values(
            name=name,
            middle_name=middle_name,
            string=string,
            error=error,
            power=power,
            require=require
        )
        field_response = await session.execute(field_stmt)
        field_id = field_response.inserted_primary_key[0]

        # Вставка записи в таблицу CardAndBackTextTable
        form_and_field_stmt = insert(FormTableAndFieldsTable).values(
            form_id=form_id,
            fields_id=field_id
        )
        await session.execute(form_and_field_stmt)
        await session.commit()
        return {'status': 200, 'description': 'Изменения не сохранены'}
    except Exception as error:
        print(error)
        return {'status': 500, 'description': 'Изменения не сохранены'}


@router.get('/field/all')
async def field_all(form_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(FieldsTable).where(FormTableAndFieldsTable.c.form_id == form_id).join(
            FieldsTable,
            or_(FormTableAndFieldsTable.c.fields_id == FieldsTable.c.id)
        )
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as error:
        print(error)
        return {'status': 200, 'description': 'Форма не найдена или произошел внутренний конфликт'}


@router.post('/field/update')
async def field_update(fields_id: int, name: str, middle_name: str, string: str, error: str, power: bool, require: bool,
                       session: AsyncSession = Depends(get_async_session), users: User = Depends(current_user)):
    try:
        updt = update(FieldsTable).where(FieldsTable.c.id == fields_id).values(
            name=name,
            middle_name=middle_name,
            string=string,
            error=error,
            power=power,
            require=require
        )
        await session.execute(updt)
        await session.commit()
        return {'status': 200, 'description': 'Изменения сохранены'}
    except Exception as error:
        print(error)
        return {'status': 500, 'description': 'Изменения не сохранены'}
