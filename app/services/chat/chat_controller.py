import json
from typing import List, Optional

from fastapi import WebSocket, Depends
from sqlalchemy.orm import Session
from transformers import pipeline, Pipeline

from conf.messages import Msg
from db.db import get_db
from db.models import History, PDFfile, User
from repository.basic import BasicCRUD
from repository.history import HistoryCRUD
from schemas.history import HistoryBase
from services.auth.user import AuthUser
from services.history_controller import HistoryController
from services.loggs.loger import logger
from services.pdf_controller import PDFController


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

    def __init__(self, model: Pipeline, addition: Optional[dict]) -> None:
        self.model = model
        self.addition = addition

    async def get_answer(self, data: str, db: Session) -> str:
        """Returns an answer by model."""
        data_dict = json.loads(data)
        file_id = int(data_dict['file_id'])
        question = data_dict['text']
        token = data_dict['accessToken']

        user = await AuthUser.get_current_user(token=token, db=db)
        # logger.debug(f'{user.__dict__=}')
        pdf_text = await BasicCRUD.get_by_id(file_id, PDFfile, db)

        if not pdf_text or user.id != pdf_text.user_id:
            return Msg.m_404_file_not_found.value

        commanding_word = question.split()[0].lower()
        logger.warning(f'{commanding_word=}')
        if self.addition and commanding_word in self.addition:
            result = await self.run_addition(
                                             commanding_word,
                                             pdf_text.context,
                                             file_id,
                                             user,
                                             db
                                             )

        else:
            result = self.model(question=question, context=pdf_text.context)

        if commanding_word[:3] not in 'del rem cle':  # 'del rem cle rub emp'
            await self.write_answer(int(file_id), question, result.get('answer', 'None!'), db=db)  # result['answer'])

        return result['answer']

    @staticmethod
    async def write_answer(file_id: int, question: str, answer: str, db: Session) -> None:
        body = HistoryBase(fil_id=file_id, question=question, answer=answer or 'Done.')
        # logger.debug(f'{body=}')
        await HistoryCRUD.create_item(History, body, db)

    async def run_addition(
                           self,
                           command: str,
                           text: str,
                           file_id: int,
                           user: User,
                           db: Session
                           ) -> dict:
        ad_model = self.addition[command]
        # logger.warning(f'{ad_model=}')
        # command = command[:3]
        # logger.warning(f':3 {command=}')
        match command[:3]:
            case 'sum':
                # do_sample=False -> ensures that the generated summary is deterministic (non-random)
                return {'answer': ad_model(text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']}

            case 'del' | 'rem':
                await ad_model(user=user, file_id=int(file_id), db=db)  # await incorrect ?
                # + remove all history of file !?
                return {'answer': f'File({file_id}) deleted. Please return to the previous screen.'}
                # return {'answer': '...that may be a removing file and history...'}

            case 'cle' | 'rub' | 'emp':
                # remove all history of file
                result = await ad_model(file_id=file_id, user_id=user.id, db=db)
                return {'answer': result}  # remove all history of file

            case _:
                # logger.warning(f':UNK {command=}')
                return {'answer': 'Something is WRONG!'}


qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

ADDITION = {
            'sum': pipeline("summarization"),
            'summary': pipeline("summarization"),
            'summarize': pipeline("summarization"),
            'del': PDFController.del_pdf_text,
            'delete': PDFController.del_pdf_text,
            'remove': PDFController.del_pdf_text,
            'clean': HistoryController.delete_file_history,
            'rub': HistoryController.delete_file_history,
            'empty': HistoryController.delete_file_history,
            }

model_lln = LLMHandler(qa_model, ADDITION)
