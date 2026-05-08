from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from src.exceptions.base_exceptions import UnauthorizedException
from src.settings import Settings


def create_access_token(subject: int, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {'sub': str(subject), 'exp': expire, 'type': 'access'}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get('type') != 'access':
            raise UnauthorizedException('Invalid token type')
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException('Token expired')
    except jwt.InvalidTokenError:
        raise UnauthorizedException('Invalid token')


def generate_refresh_token() -> str:
    return str(uuid4())
