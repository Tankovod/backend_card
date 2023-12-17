import uuid
import zipfile
from typing import Optional

import requests
from auth.base_config import current_user
from auth.models import User
from card.middleware import save_static
from card.models import CardTable, BackTextTable, CardAndBackTextTable, AdditionTable, CardAndAdditionTable
from card.utils import card_name_generator
from card.tasks import task_update_card
from config import DOMAIN, STATIC_URL
from database import get_async_session
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from cabinet.models import CabinetTable
from apple.models import AppleCertificateTable
from apple.middleware import AppleCard

router = APIRouter(
    prefix="/card",
    tags=['Card']
)


@router.post("/new")
async def new_card(card_type: str, cabinet_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   users: User = Depends(current_user)):
    try:
        pass_sn = str(uuid.uuid4())[:12].replace("-", '').upper()
        stmt = insert(CardTable).values(
            card_name=card_name_generator(),
            card_type=card_type,
            logo=DOMAIN + "static/img/logo.jpg",
            background=DOMAIN + "static/img/shablonkart.jpg",
            icon_push=DOMAIN + 'static/img/logo.jpg',
            cabinet_id=cabinet_id,
            programId=pass_sn
        )
        request_id = await session.execute(stmt)
        card_id = request_id.inserted_primary_key[0]
        await session.commit()

        request_card = await session.execute(select(CardTable).where(CardTable.c.id == card_id))
        card = request_card.mappings().all()[0]

        cabinet_q = await session.execute(select(CabinetTable).where(CabinetTable.c.id == cabinet_id))
        cabinet = cabinet_q.mappings().all()[0]
        client_id = cabinet['apple_id']
        passes_q = await session.execute(
            select(AppleCertificateTable).where(AppleCertificateTable.c.cabinet_id == cabinet_id))
        passes = passes_q.mappings().all()[0]
        # Создание карты
        apple = AppleCard()
        await apple.create_card(client_id, passes['team_id'], passes['pass_id'], pass_sn,
                                company_name=card['corp_name'], logo_text=card['top_text_header'],
                                logo_description=card['top_text_content'], text_left_header=card['text_left_header'],
                                text_left_content=card['text_left_content'],
                                text_right_header=card['text_right_header'],
                                text_right_content=card['text_right_content'],
                                color_background=card['color_background'],
                                color_text=card['color_text'])
        # Добавление пассу sn номера
        await session.execute(insert(AppleCertificateTable).values(
            client_id=client_id,
            pass_id=passes['pass_id'],
            team_id=passes['team_id'],
            pass_sn=pass_sn,
            cabinet_id=cabinet_id
        ))
        await session.commit()
        return {'status': 200, 'description': 'Карта успешно создана'}
    except Exception as error:
        print(error)
        return {'status': 500, 'description': 'Ошибка внутри сервера'}


@router.get("/all")
async def get_all_card(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    """
    :param users: Пользователь
    :return: все карты пользователя 
    """
    query = select(CardTable).where(CardTable.c.cabinet_id == cabinet_id)
    res = await session.execute(query)
    return res.mappings().all()


@router.get("/back-route-apple")
async def get_all_back_card_data(card_id: int, session: AsyncSession = Depends(get_async_session),
                                 users: User = Depends(current_user)):
    """
    :param users: Пользователь
    :return: Обратная сторона Эппла
    """
    query = select(BackTextTable).where(CardAndBackTextTable.c.card_id == card_id). \
        join(BackTextTable, CardAndBackTextTable.c.back_text_table_id == BackTextTable.c.id)
    back_text = await session.execute(query)
    result = back_text.mappings().all()
    if result:
        return result
    else:
        return {"status": 500, "description": "Записи не найдены"}


@router.post('/update/back-route-apple')
async def update_back_route_apple(back_id: int,
                                  title: str,
                                  content: str,
                                  session: AsyncSession = Depends(get_async_session),
                                  users: User = Depends(current_user)):
    try:
        updt = update(BackTextTable).where(BackTextTable.c.id == back_id).values(
            title=title,
            content=content
        )
        await session.execute(updt)
        await session.commit()
        return {'status': 200, "description": "Успешно, данные сохранены"}
    except Exception as error:
        print(error)
        return {'status': 500, "description": "Ошибка, данные не сохранены!"}


@router.delete('/delete/back-route-apple')
async def delete_back_route_apple(back_id: int,
                                  session: AsyncSession = Depends(get_async_session),
                                  users: User = Depends(current_user)):
    try:
        updt_d = delete(CardAndBackTextTable).where(CardAndBackTextTable.c.back_text_table_id == back_id)
        updt = delete(BackTextTable).where(BackTextTable.c.id == back_id)
        await session.execute(updt_d)
        await session.execute(updt)
        await session.commit()
        return {'status': 200, "description": "Успешно, данные удалены"}
    except Exception as error:
        print(error)
        return {'status': 500, "description": "Ошибка, данные не удалены!"}


@router.post("/new/back-route-apple")
async def new_back_route(card_id: int, title: str, content: str,
                         session: AsyncSession = Depends(get_async_session),
                         users: User = Depends(current_user)):
    # Вставка записи в таблицу BackTextTable
    back_text_stmt = insert(BackTextTable).values(
        title=title,
        content=content
    )
    back_text_res = await session.execute(back_text_stmt)
    back_text_id = back_text_res.inserted_primary_key[0]

    # Вставка записи в таблицу CardAndBackTextTable
    card_and_back_text_stmt = insert(CardAndBackTextTable).values(
        back_text_table_id=back_text_id,
        card_id=card_id
    )
    await session.execute(card_and_back_text_stmt)
    await session.commit()


@router.get("/back-route-google")
async def get_all_back_card_data_google(card_id: int,
                                        session: AsyncSession = Depends(get_async_session),
                                        users: User = Depends(current_user)):
    """
    :param users: Пользователь
    :return: Обратная сторона Эппла
    """
    query = select(AdditionTable).where(CardAndAdditionTable.c.card_id == card_id). \
        join(AdditionTable, CardAndAdditionTable.c.addition_table_id == AdditionTable.c.id)
    back_text = await session.execute(query)
    result = back_text.mappings().all()
    if result:
        return result
    else:
        return {"status": 500, "description": "Записи не найдены"}


@router.post('/update/back-route-google')
async def update_back_route_google(addition_id: int,
                                   title: str,
                                   content: str,
                                   session: AsyncSession = Depends(get_async_session),
                                   users: User = Depends(current_user)):
    try:
        updt = update(AdditionTable).where(AdditionTable.c.id == addition_id).values(
            title=title,
            content=content
        )
        await session.execute(updt)
        await session.commit()
        return {'status': 200, "description": "Успешно, данные сохранены"}
    except Exception as error:
        print(error)
        return {'status': 500, "description": "Ошибка, данные не сохранены!"}


@router.delete('/delete/back-route-google')
async def delete_back_route_google(addition_id: int,
                                   session: AsyncSession = Depends(get_async_session),
                                   users: User = Depends(current_user)):
    try:
        updt_d = delete(CardAndAdditionTable).where(CardAndAdditionTable.c.addition_table_id == addition_id)
        updt = delete(AdditionTable).where(AdditionTable.c.id == addition_id)
        await session.execute(updt_d)
        await session.execute(updt)
        await session.commit()
        return {'status': 200, "description": "Успешно, данные удалены"}
    except Exception as error:
        print(error)
        return {'status': 500, "description": "Ошибка, данные не удалены!"}


@router.post("/new/back-route-google")
async def new_back_route_google(card_id: int, title: str, content: str,
                                session: AsyncSession = Depends(get_async_session),
                                users: User = Depends(current_user)):
    # Вставка записи в таблицу BackTextTable
    addition_stmt = insert(AdditionTable).values(
        title=title,
        content=content
    )
    back_text_google_res = await session.execute(addition_stmt)
    back_text_google_id = back_text_google_res.inserted_primary_key[0]

    # Вставка записи в таблицу CardAndBackTextTable
    card_and_back_text_stmt = insert(CardAndAdditionTable).values(
        addition_table_id=back_text_google_id,
        card_id=card_id
    )
    await session.execute(card_and_back_text_stmt)
    await session.commit()


@router.post("/update/card")
async def update_card(
        card_id: int,
        card_name: str,
        name: str,
        corp_name: str,
        top_text_header: str,
        top_text_content: str,
        top_text_notify: str,
        color_text: str,
        color_background: str,
        color_title: str,
        text_left_header: str,
        text_left_notify: str,
        text_left_content: str,
        text_center_header: str,
        text_center_content: str,
        text_center_notify: str,
        text_right_header: str,
        text_right_content: str,
        text_right_notify: str,
        barcode: str,
        barcode_code: str,
        barcode_text: str,
        background_tasks: BackgroundTasks,
        logo: Optional[UploadFile] = File(None),  # Making 'logo' field optional
        background: Optional[UploadFile] = File(None),  # Making 'background' field optional
        icon_push: Optional[UploadFile] = File(None),  # Making 'background' field optional
        session: AsyncSession = Depends(get_async_session),
        users: User = Depends(current_user),
):
    try:
        query = select(CardTable).where(CardTable.c.id == card_id)
        query_card = await session.execute(query)
        card_data = query_card.mappings().all()[0]
        # Check if 'logo' and 'background' are provided before saving them
        if logo:
            await save_static(logo)
            logo_img = f"{STATIC_URL}{logo.filename}"
        else:
            logo_img = card_data['logo']
        if background:
            await save_static(background)
            background_img = f"{STATIC_URL}{background.filename}"
        else:
            background_img = card_data['background']
        if icon_push:
            await save_static(icon_push)
            icon_push_img = f"{STATIC_URL}{icon_push.filename}"
        else:
            icon_push_img = card_data['icon_push']

        if top_text_header == 'null':
            top_text_header = None
            top_text_notify = None
            top_text_content = None
        else:
            top_text_header = top_text_header
        if text_left_header == 'null':
            text_left_header = None
            text_left_content = None
            text_left_notify = None
        else:
            text_left_header = text_left_header
            text_left_notify = text_left_notify
            text_left_content = text_left_content
        if text_center_header == 'null':
            text_center_header = None
            text_center_content = None
            text_center_notify = None
        else:
            text_center_header = text_center_header
            text_center_notify = text_center_notify
            text_center_content = text_center_content
        if text_right_header == 'null':
            text_right_header = None
            text_right_content = None
            text_right_notify = None
        else:
            text_right_header = text_right_header
            text_right_notify = text_right_notify
            text_right_content = text_right_content

        updt = update(CardTable).where(CardTable.c.id == card_id).values(
            card_name=card_name,
            name=name,
            corp_name=corp_name,
            # Check if logo is provided before updating its value
            logo=logo_img,
            # Check if background is provided before updating its value
            background=background_img,
            # Check if background is provided before updating its value
            icon_push=icon_push_img,
            color_text=color_text,
            color_background=color_background,
            color_title=color_title,
            top_text_header=top_text_header,
            top_text_content=top_text_content,
            top_text_notify=top_text_notify,
            text_left_header=text_left_header,
            text_left_notify=text_left_notify,
            text_left_content=text_left_content,
            text_center_header=text_center_header,
            text_center_notify=text_center_notify,
            text_center_content=text_center_content,
            text_right_header=text_right_header,
            text_right_content=text_right_content,
            text_right_notify=text_right_notify,
            barcode=barcode,
            barcode_code=barcode_code,
            barcode_text=barcode_text

        )
        await session.execute(updt)
        await session.commit()
        apple_q = await session.execute(select(AppleCertificateTable).where(
            AppleCertificateTable.c.pass_sn == card_data['programId']
        ))
        apple_data = apple_q.mappings().all()[0]
        apple = AppleCard()
        await apple.update_card(
            apple_data['client_id'],
            apple_data['team_id'],
            apple_data['pass_id'],
            apple_data['pass_sn'],
            card_data['corp_name'],
            card_data['top_text_header'],
            card_data['top_text_content'],
            card_data['text_left_header'],
            card_data['text_left_content'],
            card_data['text_right_header'],
            card_data['text_right_content'],
            card_data['color_background'],
            card_data['color_text'],
            card_data['logo'],
            card_data['background'],
            card_data['icon_push']
        )
        return {'status': 200, "description": 'Изменение сохранены'}
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'Изменение не сохранены'}


@router.get('/card/data')
async def get_current_card(card_id: int, session: AsyncSession = Depends(get_async_session),
                           users: User = Depends(current_user)):
    query = select(CardTable).where(CardTable.c.id == card_id)
    res = await session.execute(query)
    return res.mappings().all()


@router.post('/update/value')
async def get_update_card_field(card_id: int, card_field: str,
                                session: AsyncSession = Depends(get_async_session),
                                users: User = Depends(current_user)):
    stmt = update(CardTable).where(CardTable.c.id == card_id).values(
        **{card_field: None}
    )
    await session.execute(stmt)
    await session.commit()


@router.post("/apple")
async def get_apple_certificate(client_id: str, team_id: str, pass_identifier: str,
                                files: list[UploadFile] = File(...)):
    # Создаем буфер для архива
    zip_filename = client_id + team_id + ".zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file in files:
            # Получение содержимого файла
            file_content = await file.read()
            zipf.writestr(file.filename, file_content)

    url = ("http://213.109.204.251:8010/api/certs/save-single-cert/"
           + client_id + "/" + team_id + "/" + pass_identifier)
    # url = ("http://127.0.0.1:8086/api/certs/save-single-cert/" + client_id + "/" + team_id + "/" + pass_identifier)
    files = {'file': open(zip_filename, 'rb')}
    response = requests.post(url, files=files)
    return {'status': 200, "description": 'Передача файлов прошла успешно'}
