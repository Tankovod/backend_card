from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from aiohttp import ClientSession

from .base_config import auth_backend, fastapi_users
from .models import User
from .schemas import UserRead, UserCreate
from .html import HTML_CODE

router = APIRouter(
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
router.include_router(
    fastapi_users.get_reset_password_router()
)

current_user = fastapi_users.current_user()


@router.get("/get_current_user", response_model=UserRead)
async def get_data_current_user(user: User = Depends(current_user)):
    users = {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'phone': user.phone,
        'role_id': user.role_id,
        'balance': user.balance,
        'is_active': user.is_active,
        'is_superuser': user.is_superuser,
        'is_verified': user.is_verified
    }
    return users


@router.get("/users/me")
async def get_user(user: User = Depends(current_user)):
    return {"username": user.email}


@router.get("/users/auto_auth")
async def auto_auth(email: str, password: str):
    data = f"username={email}&password={password}"
    async with ClientSession(headers={'Content-Type': 'application/x-www-form-urlencoded'}) as client:
        r = await client.post("http://213.109.204.251:8000/auth/login", data=data)
        json_r = await r.json()

    HTML_CODE_ADD_TOKEN = HTML_CODE.replace("__access_token__", json_r["access_token"])
    HTML_CODE_ADD_USERNAME = HTML_CODE_ADD_TOKEN.replace("__username__", email)
    return HTMLResponse(HTML_CODE_ADD_USERNAME)
