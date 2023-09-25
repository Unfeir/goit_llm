from typing import List, Optional

from fastapi import HTTPException, status
from repository.history import HistoryCRUD
from sqlalchemy.orm import Session

from conf.messages import Msg
from db.models import PDFfile
from schemas.history import HistoryResponse
from services.loggs.loger import logger


class HistoryController:

    @staticmethod
    async def get_file_history(
            file_id: int,
            user_id: int,
            skip: int,
            limit: int,
            db: Session
    ) -> List[Optional[HistoryResponse]]:
        file = await HistoryCRUD.get_by_id(file_id, PDFfile, db)
        if not file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)


        if user_id != file.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)

        return await HistoryCRUD.get_by_file(file_id, skip, limit, db)

    @staticmethod
    async def delete_file_history(file_id: int,
                                  user_id: int,
                                  db: Session) -> str:
        file = await HistoryCRUD.get_by_id(file_id, PDFfile, db)
        # logger.warning(f'{file.__dict__=}')
        if not file:
            # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
            return 'Cant find such file'

        if user_id != file.user_id:
            # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
            return 'Its not you file'

        result = await HistoryCRUD.delete_by_file(file_id, db)
        return f'history was delete' if result else 'something going wrong'
