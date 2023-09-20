from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, status, WebSocket

from services.loggs.loger import logger


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    # def disconnect(self, websocket: WebSocket, user: str):
    #     self.connections.remove((websocket, user))

    async def broadcast(self, data: str):
        logger.debug(f'{data=}')
        logger.debug(f'{self.connections=}')
        for connection in self.connections:
            logger.debug(f'{connection=}')

            await connection.send_text(data)


manager = ConnectionManager()


class LLMHandler():

    def __init__(self, model):
        self.model = model


    async def get_answer(self, text: str, question: str):
        #there some logic
        return f'{question} on {text}. Answer: {self.model}'


model = LLMHandler('My_model_answer')
