from typing import List, Optional

from db.models import History, PDFfile
from repository.basic import BasicCRUD, UM
from schemas.history import HistoryResponse, Question
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from services.loggs.loger import logger
from services.pdf_controller import PDFController


# from services.pdf_controller import get_txt_from_pdf


class HistoryCRUD(BasicCRUD):

    @classmethod
    async def get_by_file(cls, file_id: int, skip: int, limit: int, db: Session) -> List[Optional[HistoryResponse]]:
        files = await db.execute(
                                 select(History)
                                 .join(PDFfile, PDFfile.id == History.fil_id)
                                 .where(PDFfile.id == file_id)
                                 .offset(skip)
                                 .limit(limit)
                                 )
        return files.scalars().all()

    # @classmethod
    # async def update_history(cls, user: User, payload: dict, db: Session) -> History:
    #     file_id = payload.get("file_id")
    #     pdf_file: Optional[PDFfile] = await PDFController.get_pdf_text(user=user, file_id=file_id, db=db)
    #
    #     if pdf_file:
    #         history = History(
    #                             file_id=file_id,
    #                             question=payload.question,
    #                             answer=payload.answer
    #                             )
    #         db.add(history)
    #         await db.commit()
    #         await db.refresh(user)
    #         logger.warning(f'Update history for file ID: {payload.fil_id}')
    #
    #     return history
