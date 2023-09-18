from datetime import datetime

from pydantic import BaseModel


class PdfFileBase(BaseModel):
    user_id: int
    filename: str
    context: str


class PdfFileResponse(PdfFileBase):
    id: int
    created_at: datetime

    class ConfigDict:
        from_attributes = True
