from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.models import PDFfile
from repository.basic import BasicCRUD
from schemas.pdffile import PdfFileResponse


class PDFCRUD(BasicCRUD):

    @classmethod
    async def get_by_user(cls, user_id: int, skip: int, limit: int, db: Session) -> List[PdfFileResponse]:
        files = await db.execute(
                                 select(PDFfile)
                                 .where(PDFfile.user_id == user_id)
                                 .offset(skip)
                                 .limit(limit)
                                 )

        return files.scalars().all()
