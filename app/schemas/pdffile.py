from pydantic import BaseModel, Field


class PdfFile(BaseModel):
    user_id: int
    filename: str = Field(max_length=50)
    context: str = Field()
    # log_id: int
