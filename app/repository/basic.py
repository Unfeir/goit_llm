from typing import TypeVar, Generic, List, Optional, Union

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from db.models import User, UserRole
from schemas.user import UserSignUp
from services.loggs.loger import logger

UM = TypeVar('UM')


class BasicCRUD(Generic[UM]):
    @classmethod
    async def create_item(cls, model: UM, body: Union[UserSignUp], db: Session) -> UM:
        new_item = model(**body.model_dump())
        # check if there is data in the table, first user = admin
        if model == User:
            query = select(func.count()).select_from(User)
            result = await db.execute(query)
            count = result.scalar()
            new_item.role = UserRole.ADMIN if count == 0 else UserRole.USER

        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        logger.warning(f'creating {model.__name__} {new_item.id}')
        return new_item

    @classmethod
    async def get_by_id(cls, id_: int, model: UM, db: Session) -> Optional[UM]:
        return await db.get(model, id_)

    @classmethod
    async def delete_by_id(cls, id_: int, model: UM, db: Session) -> bool:
        item: UM = await db.get(model, id_)
        if item:
            await db.delete(item)
            await db.commit()
            logger.warning(f'delete {model.__name__} {item.id}')
            return True
        else:
            return False

    @classmethod
    async def get_all(cls, skip: int, limit: int, model: UM, db: Session) -> Optional[List[UM]]:
        query = select(model)
        query = query.limit(limit).offset(skip)
        result = await db.execute(query)
        items = result.scalars().all()
        return items

    @classmethod
    async def update_avatar(cls, model: UM, url: Optional[str], db: Session) -> UM:
        model.avatar = url
        await db.commit()
        await db.refresh(model)
        logger.warning(f'set avatar {model.id} with: {model.avatar=}')
        return model
