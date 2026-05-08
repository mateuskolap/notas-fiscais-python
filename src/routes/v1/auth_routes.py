from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import AuthAct, CurrentUser
from src.dtos.auth_dtos import RefreshTokenRequest, TokenResponse
from src.dtos.user_dtos import UserRead

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
async def login(
    actions: AuthAct,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return await actions.login(form_data.username, form_data.password)


@router.post('/refresh', response_model=TokenResponse)
async def refresh(data: RefreshTokenRequest, actions: AuthAct):
    return await actions.refresh(data.refresh_token)


@router.post('/logout', status_code=HTTPStatus.NO_CONTENT)
async def logout(data: RefreshTokenRequest, actions: AuthAct):
    await actions.logout(data.refresh_token)


@router.get('/me', response_model=UserRead)
async def me(current_user: CurrentUser):
    return current_user
