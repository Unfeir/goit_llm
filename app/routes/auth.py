from typing import Annotated, Any, Optional, Union

from conf.messages import Msg
from db.db import get_db
from db.models import User
from fastapi import APIRouter, Depends, HTTPException, Security, status  # , Form
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
# from pydantic import Json
from repository.users import UserCRUD
from schemas.user import Token, UserResponse, UserSignUp #, UserAny
from services.auth.password import AuthPassword
from services.auth.token import AuthToken
from services.auth.user import AuthUser, security
from services.loggs.loger import logger
from sqlalchemy.orm import Session
# from urllib.parse import urlsplit, parse_qs

router = APIRouter(prefix='/auth', tags=['auth'])


# response_model=UserResponse  response_model=None
@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='Create new user')
async def sign_up(
        body: UserSignUp,  # UserSignUp or Json or dict,  # = Form(),  # UserSignUp
        db: Session = Depends(get_db)
) -> UserResponse:  # UserResponse:
    # body = UserSignUp(dict(body))
    # logger.warning(f'{body}')
    # print('='*50, body)
    # body = UserSignUp({k: v[0] for k, v in parse_qs(body).items()})
    check_user: Optional[User] = await UserCRUD.get_user_by_email(email=body.email,
                                                                  db=db)
    if check_user:
        logger.error(f'try to signup with exist email: {Msg.m_409_conflict.value}')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Msg.m_409_conflict.value)

    body.password = AuthPassword.get_hash_password(body.password)
    user: User = await UserCRUD.create_item(model=User, body=body, db=db)
    # logger.warning(f'{user.to_dict()}')
    # print('=' * 50, user.to_dict())
    # resp = {
    #     'id': user.id,
    #     'username': user.username,
    #     'email': user.email,
    #     'created_at': user.created_at,
    #     'avatar': user.avatar,
    #     'role': user.role,
    #     'status_active': user.status_active
    # }
    # # resp = {
    # #     'id': user.id,
    # #     'username': user.username,
    # #     'email': user.email,
    # #     'created_at': user.created_at,
    # #     'avatar': user.avatar,
    # #     'role': user.role,
    # #     'status_active': user.status_active
    # # }
    # logger.warning(f'{resp}')
    # print('=' * 50, resp)
    return user  # resp  #user  # user.to_dict()


@router.post('/login', response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    # logger.warning(f'{body}')
    # print('=' * 50, body)
    user: Union[User, bool] = await AuthUser.authenticate_user(username=body.username, password=body.password, db=db)
    if not user:
        logger.error(f'{body.username} - {Msg.m_401_unauthorized.value}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Msg.m_401_unauthorized.value)
    if user.status_active is False:
        logger.error(f'{body.username} - {Msg.m_403_user_banned.value}')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_user_banned.value)
    access_token: Annotated[str, Depends(AuthToken.oauth2_scheme)] = await AuthToken.create_token(data=user)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get('/me', response_model=UserResponse, name='Get user info')
async def read_users_me(
        current_user: User = Depends(AuthUser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db)
) -> User:
    return current_user
