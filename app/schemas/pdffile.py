from pydantic import BaseModel, Field


class PdfFileRequest(BaseModel):
    user_id: int
    filename: str
    context: str
    # log_id: int
