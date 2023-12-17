import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as router_auth
from cabinet.router import router as router_cabinet
from card.router import router as router_card
from payment.router import router as router_payment
from forms.router import router as router_forms
from client.router import router as router_client
from settings.router import router as router_settings
from trigger.router import router as router_trigger
from segment.router import router as router_segment
from push.router import router as router_push
from apple.router import router as router_apple

# Название проекта и документации
app = FastAPI(
    title="Optimism"
)

current_dir = os.path.join(os.path.dirname(__file__))
app.mount('/static', StaticFiles(directory=os.path.join(current_dir, 'static')), name='static')
# app.mount('/static', StaticFiles(directory='static'), name='static')

# Routers - Роутеры нужные для подключения сторонних приложений в отдельных
#           директориях, избавляет от проблемы нагруженности файлов

# Авторизация
app.include_router(
    router_auth,
    prefix="/auth",
    tags=["Auth"],
)

# Кабинеты и действия с ним
app.include_router(
    router_cabinet
)

# Карты и действия с ними
app.include_router(
    router_card
)

# Платежная система
app.include_router(
    router_payment
)
# Форма выдачи карты клиентам
app.include_router(
    router_forms
)
# Клиенты и карты
app.include_router(
    router_client
)
# Настройки кабинета
app.include_router(
    router_settings
)
# Триггеры
app.include_router(
    router_trigger
)

# Сегменты
app.include_router(
    router_segment
)

# Веб пуши
app.include_router(
    router_push
)

app.include_router(
    router_apple
)

origins = [
    'http://localhost:3000',
    'https://213.109.204.251:8000',
    'https://213.109.204.251:3000',
    'http://213.109.204.251:8000',
    'http://213.109.204.251:3000',
    'https://admin-platforma.oppti.me',
]

# Настройки CORS и конфигурации
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)