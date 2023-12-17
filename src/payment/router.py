import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cabinet.models import CabinetTable
from config import PAYMENT_USER, PAYMENT_PASSWORD
from database import get_async_session
from payment.middleware import generate_payment_link
from payment.models import PaymentOrderTable, ContractPaymentTable, PaymentHistoryPayment, PaymentOrderOfflineTable

router = APIRouter(
    prefix="/payment",
    tags=['payment']
)


@router.post('/create/online')
async def create_new_payment(cabinet_id: int, amount: int, session: AsyncSession = Depends(get_async_session)):
    result = generate_payment_link(
        merchant_login=PAYMENT_USER,
        merchant_password_1=PAYMENT_PASSWORD,
        cost=f"{amount}",
        number=int(uuid.uuid4()),
        description='',
        is_test=1,
    )

    stmt = insert(PaymentOrderTable).values(
        amount=amount,
        cabinet_id=cabinet_id
    )
    await session.execute(stmt)
    await session.commit()

    return {"pay_url": result}


@router.post('/create/offline')
async def create_new_order(cabinet_id: int, amount: int, placeholder: str,
                           session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = insert(PaymentOrderOfflineTable).values(
            amount=amount,
            placeholder=placeholder,
            cabinet_id=cabinet_id
        )
        await session.execute(stmt)
        await session.commit()
        return {'status': 200, "description": 'Платеж создан'}
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'внутреняя ошибка'}


@router.get('/contract')
async def create_new_contract(cabinet_id: int, text: str, session: AsyncSession = Depends(get_async_session)):
    query = select(ContractPaymentTable).where(ContractPaymentTable.c.cabinet_id == cabinet_id)
    result = await session.execute(query)
    row = result.mappings().all()
    if row:
        return {"text": row[0]['document']}
    else:
        stmt = insert(ContractPaymentTable).values(
            document=text,
            cabinet_id=cabinet_id
        )
        await session.execute(stmt)
        await session.commit()
        return {'text': 'Контракт не найден'}


@router.post('/change/tariff')
async def change_cabinet_tariff(cabinet_id: int, amount: int, tariff: str,
                                session: AsyncSession = Depends(get_async_session)):
    query = select(CabinetTable).where(CabinetTable.c.id == cabinet_id)
    result = await session.execute(query)
    cabinet = result.mappings().all()[0]
    if cabinet['balance'] >= float(amount):
        updt = update(CabinetTable).where(CabinetTable.c.id == cabinet_id).values(
            Tariff=tariff,
            balance=cabinet['balance'] - float(amount)
        )
        stmt = insert(PaymentHistoryPayment).values(
            amount=amount,
            type='Абонентская плата',
            cabinet_id=cabinet_id
        )
        await session.execute(updt)
        await session.execute(stmt)
        await session.commit()
        return {'status': 200, 'description': 'Тариф успешно изменнен'}
    else:
        return {'status': 422, 'description': 'Денежных средств не хватает, пожалуйста, пополните баланс!'}


@router.get('/history')
async def get_cabinet_payment_history(cabinet_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(PaymentHistoryPayment).where(PaymentHistoryPayment.c.cabinet_id == cabinet_id)
        result = await session.execute(query)
        row = result.mappings().all()
        if row:
            return row
        else:
            return {'status': 404, "description": 'Не найдены платежи'}
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'внутреняя ошибка'}


@router.get('/history/offline')
async def get_cabinet_offline_payment_hostory(cabinet_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(PaymentOrderOfflineTable).where(PaymentOrderOfflineTable.c.cabinet_id == cabinet_id)
        result = await session.execute(query)
        row = result.mappings().all()
        if row:
            return row
        else:
            return {'status': 404, "description": 'Не найдены платежи'}
    except Exception as error:
        print(error)
        return {'status': 500, "description": 'внутреняя ошибка'}
