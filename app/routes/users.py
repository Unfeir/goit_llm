from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Security, status, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from conf.messages import Msg
from db.db import get_db
from db.models import User, UserRole
from repository.users import UserCRUD
from schemas.user import UserFullUpdate, UserResponse, UserUpdate
from services.auth.user import AuthUser, security
from services.images import CloudImage
from services.loggs.loger import logger
from services.roles import allowed_admin, allowed_all_roles_access


router = APIRouter(prefix='/users', tags=['users'])


@router.get(
            '/',
            dependencies=[Depends(allowed_all_roles_access)],
            response_model=List[UserResponse],
            name='Get all users.'
            )
async def get_all_users(
                        skip: int = 0, limit: int = 10,
                        current_user: User = Depends(AuthUser.get_current_user),
                        credentials: HTTPAuthorizationCredentials = Security(security),
                        db: Session = Depends(get_db)
                        ) -> List[User]:
    users: Optional[List[User]] = await UserCRUD.get_all(skip=skip, limit=limit, model=User, db=db)
    if not users:
        logger.debug('No users')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_user_not_found.value)

    return users


@router.get(
            '/{user_id}',
            dependencies=[Depends(allowed_all_roles_access)],
            response_model=UserResponse,
            name='Get user info by id.'
            )
async def get_user_by_id(
                         user_id: int,
                         current_user: User = Depends(AuthUser.get_current_user),
                         credentials: HTTPAuthorizationCredentials = Security(security),
                         db: Session = Depends(get_db)
                         ) -> Optional[User]:
    user: Optional[User] = await UserCRUD.get_by_id(id_=user_id, model=User, db=db)

    if not user:
        logger.debug(f'No user with {user_id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_user_not_found.value)

    return user


@router.patch(
              '/',
              dependencies=[Depends(allowed_all_roles_access)],
              response_model=UserResponse,
              name='Update own username, password.'
              )
async def update_user_profile(
                              body: UserUpdate,
                              current_user: User = Depends(AuthUser.get_current_user),
                              credentials: HTTPAuthorizationCredentials = Security(security),
                              db: Session = Depends(get_db)
                              ) -> User:
    updated_user = await UserCRUD.update_user_profile(user=current_user, body=body, db=db)
    return updated_user


@router.patch(
              '/admin/{user_id}',
              dependencies=[Depends(allowed_admin)],
              response_model=UserResponse,
              name='Update userprofile.'
              )
async def update_user_profile_by_admin(
                                       user_id: int,
                                       body: UserFullUpdate,
                                       credentials: HTTPAuthorizationCredentials = Security(security),
                                       db: Session = Depends(get_db)
                                       ) -> User:
    user: Optional[User] = await UserCRUD.get_by_id(id_=user_id, model=User, db=db)
    if not user:
        logger.debug(f'No user with {user_id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_user_not_found.value)

    updated_user: User = await UserCRUD.update_user_profile(user=user, body=body, db=db)

    return updated_user


@router.delete(
               '/',
               dependencies=[Depends(allowed_all_roles_access)],
               name='Delete user.',
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_user(
                      current_user: User = Depends(AuthUser.get_current_user),
                      credentials: HTTPAuthorizationCredentials = Security(security),
                      db: Session = Depends(get_db)
                      ) -> None:
    await UserCRUD.delete_by_id(id_=current_user.id, model=User, db=db)

    return status.HTTP_204_NO_CONTENT


@router.patch(
              '/ban/{user_id}',
              dependencies=[Depends(allowed_admin)],
              name='Ban user.',
              response_model=UserResponse
              )
async def ban_user(
                   user_id: int,
                   active_status: bool,
                   credentials: HTTPAuthorizationCredentials = Security(security),
                   db: Session = Depends(get_db)
                   ) -> User:
    user = await UserCRUD.get_by_id(id_=user_id, model=User, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_user_not_found.value)

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_ban_admin.value)

    user = await UserCRUD.ban_user(user=user, active_status=active_status, db=db)

    return user


@router.patch(
              '/avatar',
              response_model=UserResponse,
              dependencies=[Depends(allowed_all_roles_access)],
              name='Update user avatar.'
              )
async def update_avatar_user(
                             file: UploadFile = File(),
                             current_user: User = Depends(AuthUser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> User:
    typ = User.__name__
    src_url: str = CloudImage.avatar_upload(file=file.file, typ=typ, email=current_user.email)
    user: User = await UserCRUD.update_avatar(model=current_user, url=src_url, db=db)

    return user


@router.patch(
              '/avatar_delete',
              response_model=UserResponse,
              dependencies=[Depends(allowed_all_roles_access)],
              name='Delete user avatar.'
              )
async def delete_user_avatar(
                             current_user: User = Depends(AuthUser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> User:
    user: User = await UserCRUD.update_avatar(model=current_user, url=None, db=db)

    return user
