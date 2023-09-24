import json
from typing import List

from fastapi import WebSocket, Depends
from transformers import pipeline
# from sqlalchemy.orm import Session  # ? test!

from conf.messages import Msg
from db.db import get_db
from db.models import History, PDFfile
from repository.basic import BasicCRUD
from repository.history import HistoryCRUD
from schemas.history import HistoryBase
from services.auth.user import AuthUser
from services.loggs.loger import logger


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket, user: str):
        self.connections.remove((websocket, user))

    async def broadcast(self, data: str):
        # logger.debug(f'{data=}')
        # logger.debug(f'{self.connections=}')
        for connection in self.connections:
            # logger.debug(f'{connection=}')
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
        # logger.debug(f'{user.__dict__=}')
        pdf_text = await BasicCRUD.get_by_id(int(file_id), PDFfile, self.db)

        if not pdf_text or user.id != pdf_text.user_id:
            return Msg.m_404_file_not_found.value

        result = self.model(question=question, context=pdf_text.context)

        # logger.debug(f'{result=}')
        await self.write_answer(int(file_id), question, result['answer'])

        return result['answer']  # {'answer': 'Kyiv', 'end': 39, 'score': 0.953, 'start': 31}

    async def write_answer(self, file_id: int, question: str, answer: str) -> None:
        body = HistoryBase(fil_id=file_id, question=question, answer=answer)
        # logger.debug(f'{body=}')
        await HistoryCRUD.create_item(History, body, self.db)


qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
model = LLMHandler(qa_model)
