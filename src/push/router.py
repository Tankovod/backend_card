from fastapi import APIRouter, Depends
from sqlalchemy import insert, update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from card.models import CardTable
from database import get_async_session
from push.models import PushNotifTable, PushCardTable, PushGeoTable, PushGeoPushTable
from push.onesignal import OneSig
from push.utls import push_name_generator
from starlette.background import BackgroundTasks

from apple.models import AppleCertificateTable
from card.tasks import task_update_push

from apple.middleware import AppleCard

router = APIRouter(
    prefix="/push",
    tags=['web push']
)


@router.post('/push')
async def add_new_push(cabinet_id: int, push_type: str,
                       session: AsyncSession = Depends(get_async_session),
                       users: User = Depends(current_user)):
    """
    Добавление нового веб-пуш уведомления
    """
    await session.execute(insert(PushNotifTable).values(
        title=push_name_generator(),
        types=push_type,
        description='Описание',
        cabinet_id=cabinet_id
    ))
    await session.commit()

    return {'status': 200, 'description': 'Пуш создан'}


@router.put('/update/push')
async def update_push(push_id: int, title: str, description: str, status: bool,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    await session.execute(update(PushNotifTable).where(PushNotifTable.c.id == push_id).values(
        title=title,
        description=description,
        status=status
    ))
    await session.commit()
    return {'status': 200, 'description': 'Изменения применены'}


@router.get('/current/push')
async def get_current_push(push_id: int, session: AsyncSession = Depends(get_async_session),
                           users: User = Depends(current_user)):
    result = await session.execute(select(PushNotifTable).where(PushNotifTable.c.id == push_id))
    return result.mappings().all()


@router.put("/status/push")
async def status_push(push_id: int, status: bool,
                      background_tasks: BackgroundTasks,
                      session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    await session.execute(update(PushNotifTable).where(PushNotifTable.c.id == push_id).values(
        status=status
    ))
    await session.commit()

    if status:
        response = await session.execute(select(PushNotifTable).where(PushNotifTable.c.id == push_id))
        push = response.mappings().all()[0]
        if push['types'] == "Text":
            web_push = OneSig()
            web_push.send_notify(push['description'], push['title'])
        elif push['types'] == 'Geo':
            try:
                fk_q = await session.execute(select(PushCardTable).where(PushCardTable.c.push_id == push_id))
                fk = fk_q.mappings().all()[0]
                card_q = await session.execute(select(CardTable).where(CardTable.c.id == fk['card_id']))
                card_data = card_q.mappings().all()[0]
                apple_q = await session.execute(select(AppleCertificateTable).where(
                    AppleCertificateTable.c.pass_sn == card_data['programId']
                ))
                apple_data = apple_q.mappings().all()[0]
                geo_q = await session.execute(
                    select(PushGeoPushTable).where(
                        PushGeoPushTable.c.push_id == push_id
                    )
                )
                geo = geo_q.mappings().all()
                my_dict = {"locations": []}
                for geo_c in geo:
                    cordinate_q = await session.execute(
                        select(PushGeoTable).where(PushGeoTable.c.id == geo_c['geo_id'])
                    )
                    for cordinate in cordinate_q.mappings().all():
                        test = {"latitude": float(cordinate['coordinates_z']), "longitude": float(cordinate['coordinates_y']),
                                "relevantText": f"{push['description']}"}
                        my_dict['locations'].append(test)
                apples = AppleCard()
                await apples.update_push(
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
                    card_data['icon_push'],
                    my_dict
                )

                return {'status': 201, 'description': 'Изменения применены'}
            except Exception as error:
                print(error)
                return {'status': 200, 'description': 'Не выбран шаблон'}
    return {'status': 200, 'description': 'Изменения применены'}


@router.get("/push")
async def all_push(cabinet_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   users: User = Depends(current_user)):
    result = await session.execute(select(PushNotifTable).where(PushNotifTable.c.cabinet_id == cabinet_id))
    return result.mappings().all()


@router.post("/push/to/card")
async def make_push_to_card(card_id: int, push_id: int,
                            session: AsyncSession = Depends(get_async_session),
                            users: User = Depends(current_user)):
    try:
        await session.execute(insert(PushCardTable).values(
            card_id=card_id,
            push_id=push_id
        ))
        await session.commit()
        return {"status": 200, "description": "Связь создана"}
    except Exception as error:
        print(error)
        return {"status": 200, "description": "Возможно не найдена карта или ошибка внутри сервера"}


@router.get("/push/to/card")
async def get_push_to_card(push_id: int,
                           session: AsyncSession = Depends(get_async_session),
                           users: User = Depends(current_user)):
    result = await session.execute(select(PushCardTable).where(PushCardTable.c.push_id == push_id))
    return result.mappings().all()


@router.post('/coordinates')
async def create_new_coordinate(push_id: int, coordinates_z: str, coordinates_y: str, title: str,
                                session: AsyncSession = Depends(get_async_session),
                                users: User = Depends(current_user)):
    response = await session.execute(
        insert(PushGeoTable).values(
            coordinates_z=coordinates_z,
            coordinates_y=coordinates_y,
            title=title
        )
    )
    geo_id = response.inserted_primary_key[0]

    await session.execute(
        insert(PushGeoPushTable).values(
            geo_id=geo_id,
            push_id=push_id
        )
    )
    await session.commit()
    return {'status': 200, "description": "Карта создана"}


@router.get('/coordinates/coordinate')
async def get_all_coordinates(push_id: int, session: AsyncSession = Depends(get_async_session),
                              users: User = Depends(current_user)):
    query = select(PushGeoTable).where(PushGeoPushTable.c.push_id == push_id). \
        join(PushGeoTable, PushGeoPushTable.c.geo_id == PushGeoTable.c.id)
    result = await session.execute(query)
    return result.mappings().all()


@router.put('/coordinates/update')
async def update_coordinates(coordinate_id: int, coordinates_z: str, coordinates_y: str, title: str,
                             session: AsyncSession = Depends(get_async_session),
                             users: User = Depends(current_user)):
    await session.execute(update(PushGeoTable).where(PushGeoTable.c.id == coordinate_id).values(
        coordinates_z=coordinates_z,
        coordinates_y=coordinates_y,
        title=title
    ))

    await session.commit()
    return {'status': 200, 'description': "Изменения сохранены"}


@router.delete('/coordinates')
async def delete_coordinates(coordinate_id: int, session: AsyncSession = Depends(get_async_session),
                             users: User = Depends(current_user)):
    result = await session.execute(
        select(PushGeoPushTable).where(PushGeoPushTable.c.geo_id == coordinate_id)
    )
    data = result.mappings().all()

    await session.execute(
        delete(PushGeoPushTable).where(PushGeoPushTable.c.id == data[0]['id'])
    )

    await session.execute(
        delete(PushGeoTable).where(PushGeoTable.c.id == data[0]['geo_id'])
    )
    await session.commit()
    return {'status': 200, 'description': 'Удаление прошло успешно'}