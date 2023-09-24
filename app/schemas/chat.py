from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: int
    pdffile_id: int
    question: str
    created_at: datetime


class ChatResponse(BaseModel):
    answer: str
    score: float
    start: int
    end: int

    class ConfigDict:
        from_attributes = True
