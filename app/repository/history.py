from typing import List, Optional

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.models import History, PDFfile
from repository.basic import BasicCRUD
from schemas.history import HistoryResponse


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

    @classmethod
    async def delete_by_file(cls, file_id: int, db: Session) -> bool:
        items = await db.execute(
            select(History)
            .join(PDFfile, PDFfile.id == History.fil_id)
            .where(PDFfile.id == file_id)
        )

        items = items.scalars().all()
        if items:
            for item in items:
                await db.delete(item)
                await db.commit()

            return True

        else:
            return False
