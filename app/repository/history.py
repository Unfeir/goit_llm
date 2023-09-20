from typing import List, Optional

from db.models import History, PDFfile
from repository.basic import BasicCRUD
from schemas.history import HistoryResponse
from sqlalchemy.future import select
from sqlalchemy.orm import Session

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
