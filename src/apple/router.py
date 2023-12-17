import os
import uuid

from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from .middleware import AppleCard
from auth.models import User
from auth.base_config import current_user
from database import get_async_session

from cabinet.models import CabinetTable

from .models import AppleCertificateTable
from .test import test

router = APIRouter(
    prefix="/apple",
    tags=['apple']
)


@router.post("/download/certs/")
async def certs(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                users: User = Depends(current_user)):
    cabinet_q = await session.execute(select(CabinetTable).where(CabinetTable.c.id == cabinet_id))
    cabinet = cabinet_q.mappings().all()[0]
    apple = AppleCard()
    url = await apple.generate_cert(cabinet['apple_id'])
    print(url)
    # Определите путь и содержимое файла
    return FileResponse(url, filename='request.certSigningRequest', media_type='multipart/form-data')


@router.post("/upload/certs/")
async def certs2(cabinet_id: int, team_id: str, pass_id: str, file: UploadFile,
                 session: AsyncSession = Depends(get_async_session), users: User = Depends(current_user)):
    cabinet_q = await session.execute(select(CabinetTable).where(CabinetTable.c.id == cabinet_id))
    cabinet = cabinet_q.mappings().all()[0]
    client_id = cabinet['apple_id']
    await session.execute(insert(AppleCertificateTable).values(
        client_id=client_id,
        pass_id=pass_id,
        team_id=team_id,
        cabinet_id=cabinet_id
    ))
    await session.commit()
    path_client = str(os.getcwd() + f"""/apple/client/{client_id}/certs/""")
    cert_path = os.path.join(path_client, "pass.cer")
    with open(cert_path, 'wb') as cert_file:
        content = await file.read()
        cert_file.write(content)
    apple = AppleCard()
    await apple.upload_certifi(team_id, pass_id, client_id)
    return {"status": 200}


@router.post("/create/card/")
async def card_create(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                      users: User = Depends(current_user)):
    cabinet_q = await session.execute(select(CabinetTable).where(CabinetTable.c.id == cabinet_id))
    cabinet = cabinet_q.mappings().all()[0]
    client_id = cabinet['apple_id']
    passes_q = await session.execute(select(AppleCertificateTable).where(AppleCertificateTable.c.id == cabinet_id))
    passes = passes_q.mappings().all()[0]
    print(passes)
    apple = AppleCard()
    await apple.create_card(client_id, passes['team_id'], passes['pass_id'], "QWERTY2")


@router.get('/certificate')
async def get_cert(cabinet_id: int, session: AsyncSession = Depends(get_async_session),
                   users: User = Depends(current_user)):
    passes_q = await session.execute(
        select(AppleCertificateTable).where(AppleCertificateTable.c.cabinet_id == cabinet_id))
    return passes_q.mappings().all()[0]
