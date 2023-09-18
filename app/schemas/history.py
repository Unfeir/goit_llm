from datetime import datetime

from pydantic import BaseModel


class History(BaseModel):
    id: int
    fil_id: int
    question: str
    answer: str
    created_at: datetime

    class ConfigDict:
        from_attributes = True
