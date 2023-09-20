from typing import Annotated, Optional, Union

from conf.messages import Msg
from db.db import get_db
from db.models import User
from fastapi import APIRouter, Depends, HTTPException, Security, status, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from repository.users import UserCRUD
from schemas.user import Token, UserResponse, UserSignUp
from services.auth.password import AuthPassword
from services.auth.token import AuthToken
from services.auth.user import AuthUser, security
from services.chat.chat_controller import manager, model
from services.loggs.loger import logger
from sqlalchemy.orm import Session

router = APIRouter(prefix='/chat', tags=['chat'])


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    logger.debug(f'{client_id=}')
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        logger.debug(f'{data=}')
        logger.debug(f'{websocket.__dict__=}')
        response = await model.get_answer('test_text', 'test_answer')
        # await manager.broadcast(f"Client {client_id}: {data}")
        await websocket.send_text(f'response = {response}')

@router.get('/')
async def get_chats():
    return []