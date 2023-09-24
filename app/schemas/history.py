from datetime import datetime

from pydantic import BaseModel


class Question(BaseModel):
    fil_id: int
    question: str


class HistoryBase(Question):
    # fil_id: int
    # question: str
    answer: str


class HistoryResponse(HistoryBase):
    id: int
    created_at: datetime

    class ConfigDict:
        from_attributes = True
