from datetime import datetime
from typing import Union, Optional

from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from db.models import User
from repository.basic import BasicCRUD
from schemas.user import UserUpdate, UserFullUpdate
from services.auth.password import AuthPassword
from services.loggs.loger import logger


class UserCRUD(BasicCRUD):

    @classmethod
    async def get_or_create(cls, payload: dict, db: Session) -> User:
        email = payload.get("email")
        user: Optional[User] = await UserCRUD.get_user_by_email(email=email, db=db)

        if user is None:
            username = payload.get('username')
            dummy_password = AuthPassword.get_hash_password(password=f'{email}{datetime.utcnow().timestamp()}')
            password = payload.get('password', dummy_password)
            user = User(
                email=email,
                username=username,
                password=password
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.warning(f'creating User with {email=}')

        return user

    @classmethod
    async def get_user_by_email(cls, email: str, db: Session) -> User:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalars().first()
        return user


    @classmethod
    async def update_user_profile(cls, user: User, body: Union[UserUpdate, UserFullUpdate], db: Session) -> User:
        for field_name, value in body:
            if value not in ('string', 'user@example.com', None) and field_name in user.mapper:
                setattr(user, user.mapper[field_name], value)

        await db.commit()
        await db.refresh(user)
        changes = {el[0]: el[1] for el in body if el[1] not in ('string', 'user@example.com', None)}
        logger.warning(f'update user profile {user.email} with: {changes}')

        return user


    @classmethod
    async def ban_user(cls, user: User, active_status: bool,  db: Session) -> User:
        user.status_active = active_status
        await db.commit()
        await db.refresh(user)
        logger.warning(f'update user profile {user.email} was banned')
        return user
    