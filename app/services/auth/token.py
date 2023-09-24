from datetime import datetime, timedelta
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt as jwt_2
from starlette import status

from conf.config import settings
from conf.messages import Msg
from db.models import User
from services.loggs.loger import logger


class AuthToken:
    jwks_url = f'https://{settings.domain}/.well-known/jwks.json'
    jwks_client = jwt.PyJWKClient(jwks_url)
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl='/auth/login')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    credentials_exception = HTTPException(
                                          status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=Msg.m_401_credentials.value,
                                          headers={'WWW-Authenticate': 'Bearer'},
                                          )

    @classmethod
    async def create_token(cls, data: User, expires_delta: Optional[float] = None) -> str:
        to_encode = data.to_dict().copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(expires_delta)

        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_timer)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token: Annotated[str, Depends(AuthToken.oauth2_scheme)] = jwt_2.encode(
                                                                               claims=to_encode,
                                                                               key=AuthToken.SECRET_KEY,
                                                                               algorithm=AuthToken.ALGORITHM
                                                                               )

        return token

    @classmethod
    async def verify_auth2(cls, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
        try:
            payload: dict = jwt_2.decode(
                                         token=token,
                                         key=AuthToken.SECRET_KEY,
                                         algorithms=[AuthToken.ALGORITHM]
                                         )
            user_email: str = payload.get('email')
            if user_email is None:
                logger.error({'status': 'error', 'message': 'no email in token'})
                raise AuthToken.credentials_exception

        except JWTError:
            logger.error({'status': AuthToken.credentials_exception})
            raise AuthToken.credentials_exception

        return payload

    @classmethod
    async def verify_auth0(cls, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
        try:
            signing_key = AuthToken.jwks_client.get_signing_key_from_jwt(
                token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            logger.error({'status': 'error', 'msg': error.__str__()})
            raise AuthToken.credentials_exception

        except jwt.exceptions.DecodeError as error:
            logger.error({'status': 'error', 'msg': error.__str__()})
            raise AuthToken.credentials_exception

        try:
            payload: dict = jwt.decode(
                                       token,
                                       signing_key,
                                       algorithms=settings.auth0_algorithm,
                                       audience=settings.audience,
                                       )
        except Exception as e:
            logger.error({'status': 'error', 'message': str(e)})
            raise AuthToken.credentials_exception

        return payload
