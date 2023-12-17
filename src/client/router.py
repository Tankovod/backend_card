import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy import insert, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from card.models import CardTable
from client.middleware import DemoLoyalty
from client.models import ClientTable
from client.utils import client_name_generator
from database import get_async_session
from forms.models import FormTable
from apple.models import AppleCertificateTable
from apple.middleware import AppleCard

router = APIRouter(
    prefix="/client",
    tags=['client']
)


@router.post("/new")
async def new_client(body: Request, session: AsyncSession = Depends(get_async_session)):
    data = await body.json()
    form = await session.execute(select(FormTable).where(
        or_(FormTable.c.id == data['form_id'])
    ))
    form_data = form.mappings().all()[0]
    query_card = await session.execute(select(CardTable).where(
        or_(
            CardTable.c.id == form_data['card_id']
        )
    ))
    card = query_card.mappings().all()[0]
    print("Карта", card)
    query_apple = await session.execute(select(AppleCertificateTable).where(
        AppleCertificateTable.c.pass_sn == card['programId']
    ))
    apple_data = query_apple.mappings().all()[0]

    # google_api = DemoLoyalty()
    # google_card = google_api.create_class('')

    await session.execute(insert(ClientTable).values(
        form_id=data['form_id'],
        cabinet_id=data['cabinet_id'],
        data=data['data'],
        google_wallet_url="https://google.com/1",
        apple_wallet_url=f"http://213.109.204.251:8010/api/passes/serve-single-pass/{apple_data['client_id']}/{apple_data['team_id']}/{apple_data['pass_id']}/{apple_data['pass_sn']}.pkpass"
    ))
    await session.commit()
    return {"google_url": "https://pay.google.com/gp/v/save/eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiYTYzZjFjYzU1M2E5ZGVjOTk1NDM3MmRiNjA0NGQzMjM4YTk1ZGUzOSJ9.eyJpc3MiOiAid2FsbGV0LXdlYi1jbGllbnRAb3B0aW1pc20tMzkwNTEzLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwgImF1ZCI6ICJnb29nbGUiLCAib3JpZ2lucyI6IFsid3d3LmV4YW1wbGUuY29tIl0sICJ0eXAiOiAic2F2ZXRvd2FsbGV0IiwgInBheWxvYWQiOiB7ImxveWFsdHlDbGFzc2VzIjogW3siaWQiOiAiMzM4ODAwMDAwMDAyMjI1MzIyNS5iODBhZjYwZS03OTM2LTQ2YjUtYTU1Yi1mMzA0NWNmOWRjOTIiLCAiaXNzdWVyTmFtZSI6ICJcdTA0MjBcdTA0NGZcdTA0MzZcdTA0MzVcdTA0M2RcdTA0M2FcdTA0MzAiLCAicmV2aWV3U3RhdHVzIjogIlVOREVSX1JFVklFVyIsICJoZXhCYWNrZ3JvdW5kQ29sb3IiOiAiI2ZmZmZmZiIsICJwcm9ncmFtTmFtZSI6ICJcdTA0MTRcdTA0MzVcdTA0M2JcdTA0MzBcdTA0MzVcdTA0M2MgXHUwNDQyXHUwNDMyXHUwNDNlXHUwNDRlIFx1MDQzNlx1MDQzOFx1MDQzN1x1MDQzZFx1MDQ0YyBcdTA0NDFcdTA0M2JcdTA0MzBcdTA0NDlcdTA0MzUiLCAicHJvZ3JhbUxvZ28iOiB7InNvdXJjZVVyaSI6IHsidXJpIjogImh0dHBzOi8vaS5pYmIuY28vS3dYNDU1ei9DMy05MC1DMi1BMS1DMy05MC1DMi1CRC1DMy05MC1DMi1COC1DMy05MC1DMi1CQy1DMy05MC1DMi1CRS1DMy05MC1DMi1CQS0yMDAzLnBuZyJ9LCAiY29udGVudERlc2NyaXB0aW9uIjogeyJkZWZhdWx0VmFsdWUiOiB7Imxhbmd1YWdlIjogInJ1LVJVIiwgInZhbHVlIjogIjEifX19fV0sICJsb3lhbHR5T2JqZWN0cyI6IFt7ImlkIjogIjMzODgwMDAwMDAwMjIyNTMyMjUuOTYxNmQ2NWQtNDJiZS00OGFlLWI0NmQtMDJmZmM1Y2JmY2JmIiwgImNsYXNzSWQiOiAiMzM4ODAwMDAwMDAyMjI1MzIyNS5iODBhZjYwZS03OTM2LTQ2YjUtYTU1Yi1mMzA0NWNmOWRjOTIiLCAic3RhdGUiOiAiQUNUSVZFIiwgImhlcm9JbWFnZSI6IHsic291cmNlVXJpIjogeyJ1cmkiOiAiaHR0cHM6Ly9pLmliYi5jby9reDRtYnRUL2xvZ28ucG5nIn0sICJjb250ZW50RGVzY3JpcHRpb24iOiB7ImRlZmF1bHRWYWx1ZSI6IHsibGFuZ3VhZ2UiOiAicnUtUlUiLCAidmFsdWUiOiAiMiJ9fX0sICJiYXJjb2RlIjogeyJ0eXBlIjogIlFSX0NPREUiLCAidmFsdWUiOiAiUVIgY29kZSJ9LCAiaGV4QmFja2dyb3VuZENvbG9yIjogIiNmZmZmZmYiLCAibG9jYXRpb25zIjogW3sibGF0aXR1ZGUiOiAzNy40MjQwMTU0OTk5OTk5OTYsICJsb25naXR1ZGUiOiAtMTIyLjA5MjU5NTYwMDAwMDAxfV0sICJhY2NvdW50SWQiOiAiMzAzMCAxMjY5IDMyMTUgMTM3NSIsICJhY2NvdW50TmFtZSI6ICJTZW0gUGVtIiwgImxveWFsdHlQb2ludHMiOiB7ImxhYmVsIjogIlx1MDQxMVx1MDQzZVx1MDQzZFx1MDQ0M1x1MDQ0MVx1MDQ0YiIsICJiYWxhbmNlIjogeyJzdHJpbmciOiAiNTc2XHUwNDQwIn19LCAic2Vjb25kYXJ5TG95YWx0eVBvaW50cyI6IHsibGFiZWwiOiAiXHUwNDEyXHUwNDNiXHUwNDMwXHUwNDM0XHUwNDM1XHUwNDNiXHUwNDM1XHUwNDQ2IiwgImJhbGFuY2UiOiB7InN0cmluZyI6ICJcdTA0MTBcdTA0M2JcdTA0MzVcdTA0M2FcdTA0NDFcdTA0MzVcdTA0MzkgXHUwNDFhLiJ9fX1dfX0.DKbgs1vhcsvSrHBSTTK06jlLuXw2UC4EBJiQWmNNDnXjf8FknWyZ3wdPSpoTL2jM3xK_gwhgouWEyUflkyOPKbwxBj_Y5MVkPUZuASNQcav8gx2iw2_dgb5-qm996iI72YFbBDa15ANt-lA7y0axPKqokhR45-2Yy4X4kv_BwuZuIHHVilaqNpmtKaMXAYV9jTl8FzKbM-PMMKABH1gWiNwsGTwuCzBoycUyKGToGLVJk2zQu0omqONRhbqQpJKPqQw-1fYVZbv93FPY1diYe58LpUyrUGXxHFdcDfN0m3Itvv95vqobKb1IkziTzxT-dLfOlMmmevMSX9sTKF5ojQ", "apple_url": f"http://213.109.204.251:8010/api/passes/serve-single-pass/{apple_data['client_id']}/{apple_data['team_id']}/{apple_data['pass_id']}/{apple_data['pass_sn']}.pkpass"}


@router.get("/all")
async def all_client(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                     users: User = Depends(current_user)):
    result = await session.execute(
        select(ClientTable).where(ClientTable.c.cabinet_id == cabinet_id)
    )
    return result.mappings().all()


@router.get('/current')
async def current_client(client_id: int, session: AsyncSession = Depends(get_async_session),
                         users: User = Depends(current_user)):
    result = await session.execute(
        select(ClientTable).where(ClientTable.c.id == client_id)
    )
    return result.mappings().all()


@router.post("/update")
async def update_client(body: Request, session: AsyncSession = Depends(get_async_session),
                        users: User = Depends(current_user)):
    """
    Обновление клиента, точнее данных внутри data параметров
    :param body: Передавай сюда только DATA параметры запроса, изменяем только его
    :param session: База данных
    :param users: Пользователь
    :return: новая ссылка на карту
    """
    data = await body.json()
    form = await session.execute(select(FormTable).where(
        or_(FormTable.c.id == data['form_id'])
    ))
    query_card = await session.execute(select(CardTable).where(
        or_(
            CardTable.c.id == form.mappings().all()[0]['card_id']
        )
    ))
    card = query_card.mappings().all()[0]
    api = DemoLoyalty()
    number = uuid.uuid4()
    api.create_class('3388000000022253225', str(number), card['corp_name'], card['top_text_content'])
    url_google = api.create_jwt_new_objects('3388000000022245217',
                                            str(number),
                                            client_name_generator(),
                                            card['corp_name'],
                                            card['top_text_content'],
                                            card['text_left_header'],
                                            card['text_left_content'],
                                            card['text_right_header'],
                                            card['text_right_content'],
                                            '1',
                                            '1',
                                            data['data']['first_name'] + " " + data['data']['last_name'])
    await session.execute(
        update(ClientTable).where(or_(ClientTable.c.id == data['client_id'])).values(
            data=data['data'],
            google_wallet_url=url_google,
            apple_wallet_url='2'
        )
    )
    await session.commit()
    return {'url': url_google}
