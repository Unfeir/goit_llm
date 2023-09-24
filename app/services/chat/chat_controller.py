import json
from typing import List

from conf.messages import Msg
from db.db import get_db
from db.models import History, PDFfile
from fastapi import WebSocket, Depends
from repository.basic import BasicCRUD
from repository.history import HistoryCRUD
from schemas.history import HistoryBase
from services.auth.user import AuthUser
from services.loggs.loger import logger
from transformers import pipeline
from sqlalchemy.orm import Session


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket, user: str):
        self.connections.remove((websocket, user))

    async def broadcast(self, data: str):
        logger.debug(f'{data=}')
        logger.debug(f'{self.connections=}')
        for connection in self.connections:
            logger.debug(f'{connection=}')

            await connection.send_text(data)


manager = ConnectionManager()


class LLMHandler:

    def __init__(self, model) -> None:
        self.db = None
        self.model = model

    async def get_session(self):
        db = [db async for db in get_db()]
        self.db = db[0]

    async def get_answer(self, data: str) -> str:
        """Returns an answer by model."""
        await self.get_session()
        data_dict = json.loads(data)
        file_id = data_dict['file_id']
        question = data_dict['text']
        token = data_dict['accessToken']

        user = await AuthUser.get_current_user(token=token, db=self.db)
        logger.debug(f'{user.__dict__=}')
        pdf_text = await BasicCRUD.get_by_id(int(file_id), PDFfile, self.db)

        if not pdf_text or user.id != pdf_text.user_id:
            return Msg.m_404_file_not_found.value

        result = self.model(question=question, context=pdf_text.context)

        # logger.debug(f'{result=}')
        await self.write_answer(int(file_id), question, result['answer'])

        return result['answer']
        ## {'answer': 'Kyiv', 'end': 39, 'score': 0.953, 'start': 31}

    async def write_answer(self, file_id: int, question: str, answer: str) -> None:
        body = HistoryBase(fil_id=file_id, question=question, answer=answer)
        logger.debug(f'{body=}')

        await HistoryCRUD.create_item(History, body, self.db)


qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
model = LLMHandler(qa_model)

#
# class RequestAnalyzer:
#
#     @staticmethod
#     async def get_the_answer(
#             qa_model: pipeline = qa_model,
#             question: str = 'Is there a question?',
#             context: str = 'I don\'t see the request.'
#     ) -> dict:
#         """Returns an answer by model."""
#         # question = "Where do we live?"
#         # context = "We are the Fast Rabbit team and we live in Kyiv."
#         return qa_model(question=question, context=context)
#         ## {'answer': 'Kyiv', 'end': 39, 'score': 0.953, 'start': 31}
#
#     # user=current_user, pdffile_id=pdffile_id, question=question, db=db
#     @staticmethod
#     async def return_answer(user: User, file_id: int, question_id: int, db: Session) -> ChatResponse:
#         # get txt from db
#         pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
#         question = await BasicCRUD.get_by_id(id_=question_id, model=Question, db=db)  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         if not pdf_text:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
#         if user.id != pdf_text.user_id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
#         # throw question and text to model
#         return await RequestAnalyzer.get_the_answer(qa_model=qa_model, question=question, context=pdf_text)
#
#     @staticmethod
#     async def save_question(user: User, file_id: int, question: str, db: Session) -> ChatRequest:
#         # get txt from db
#         pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
#         if not pdf_text:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
#         if user.id != pdf_text.user_id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
#         # save question ? history ? to db!
#         question = ChatRequest(
#             user_id=user.id,
#             pdffile_id=file_id,
#             question=question,
#             # created_at: datetime
#         )
#         return await BasicCRUD.create_item(Question, question, db)
