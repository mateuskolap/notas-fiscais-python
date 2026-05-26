from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import AuthAct, CurrentUser
from src.dtos.auth_dtos import RefreshTokenRequest, TokenResponse
from src.dtos.response_dtos import ErrorResponse
from src.dtos.user_dtos import UserMeRead

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/login',
    response_model=TokenResponse,
    summary='User authentication',
    responses={
        401: {'model': ErrorResponse, 'description': 'Invalid username or password'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def login(
    actions: AuthAct,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Authenticate a user using their email (as username) and password.

    On successful authentication, it generates and returns an OAuth2 compatible
    Access Token and a Refresh Token.
    """
    return await actions.login(form_data.username, form_data.password)


@router.post(
    '/refresh',
    response_model=TokenResponse,
    summary='Refresh access token',
    responses={
        401: {
            'model': ErrorResponse,
            'description': 'Invalid or expired refresh token',
        },
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def refresh(data: RefreshTokenRequest, actions: AuthAct):
    """
    Retrieve a new short-lived Access Token using a valid Refresh Token.

    This extends the session without requiring user credentials.
    """
    return await actions.refresh(data.refresh_token)


@router.post(
    '/logout',
    status_code=HTTPStatus.NO_CONTENT,
    summary='User logout',
    responses={
        401: {'model': ErrorResponse, 'description': 'Invalid or expired token'},
        422: {'model': ErrorResponse, 'description': 'Validation error'},
    },
)
async def logout(data: RefreshTokenRequest, actions: AuthAct):
    """
    Log out the user by revoking and invalidating the provided Refresh Token.
    """
    await actions.logout(data.refresh_token)


@router.get(
    '/me',
    response_model=UserMeRead,
    summary='Get current user profile',
    responses={
        401: {'model': ErrorResponse, 'description': 'Missing or invalid token'},
    },
)
async def me(current_user: CurrentUser):
    """
    Retrieve details and permissions of the currently authenticated user.
    """
    return current_user
