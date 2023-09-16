from typing import Optional, Annotated, Union

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from conf.config import settings
from conf.messages import Msg
from db.db import get_db
from db.models import User
from services.auth.password import AuthPassword
from services.auth.token import AuthToken
from repository.users import UserCRUD as ucrud

security = HTTPBearer()


class AuthUser(AuthToken):
    @classmethod
    async def get_current_user(cls, token: Annotated[str, Depends(AuthToken.oauth2_scheme)],
                               db: Session = Depends(get_db)) -> User:
        try:
            token_type = jwt.get_unverified_header(token)
            if token_type.get('alg') == settings.algorithm:
                payload: dict = await AuthToken.verify_auth2(token)
            else:
                payload: dict = await AuthToken.verify_auth0(token)
        except Exception:
            raise AuthToken.credentials_exception

        user: User = await ucrud.get_or_create(payload=payload, db=db)
        if user is None:
            raise AuthToken.credentials_exception
        if not user.status_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Msg.m_400_inactive_user.value)
        return user


    @classmethod
    async def authenticate_user(cls, username: str, password: str, db: Session) -> Union[bool, User]:
        user: Optional[User] = await ucrud.get_user_by_email(email=username, db=db)
        if not user:
            return False
        if not AuthPassword.verify_password(password, user.password):
            return False
        return user
