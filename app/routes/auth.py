from typing import Annotated, Optional, Union

from conf.messages import Msg
from db.db import get_db
from db.models import User
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from repository.users import UserCRUD
from schemas.user import Token, UserResponse, UserSignUp
from services.auth.password import AuthPassword
from services.auth.token import AuthToken
from services.auth.user import AuthUser, security
from services.loggs.loger import logger
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(
        body: UserSignUp,
        db: Session = Depends(get_db)
) -> User:
    logger.debug(f'{body}')
    check_user: Optional[User] = await UserCRUD.get_user_by_email(email=body.email, db=db)
    if check_user:
        logger.error(f'try to signup with exist email: {Msg.m_409_conflict.value}')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Msg.m_409_conflict.value)

    body.password = AuthPassword.get_hash_password(body.password)
    user: User = await UserCRUD.create_item(model=User, body=body, db=db)
    return user


@router.post('/login', response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    logger.debug(f'{body=}')
    user: Union[User, bool] = await AuthUser.authenticate_user(username=body.username, password=body.password, db=db)
    if not user:
        logger.error(f'{body.username} - {Msg.m_401_unauthorized.value}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Msg.m_401_unauthorized.value)
    if user.status_active is False:
        logger.error(f'{body.username} - {Msg.m_403_user_banned.value}')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_user_banned.value)
    access_token: Annotated[str, Depends(AuthToken.oauth2_scheme)] = await AuthToken.create_token(data=user)
    return {'access_token': access_token, 'token_type': 'Bearer', 'success': True}


@router.get('/me', response_model=UserResponse, name='Get user info')
async def read_users_me(
        current_user: User = Depends(AuthUser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db)
) -> User:
    return current_user
