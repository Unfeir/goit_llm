from fastapi import APIRouter, Depends, Query, Security, WebSocket
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.db import get_db
from db.models import User
from schemas.chat import ChatRequest, ChatResponse
from services.auth.user import AuthUser, security
from services.chat.chat_controller import manager, model_lln
from services.roles import allowed_all_roles_access
from services.textprocessor import RequestAnalyzer


router = APIRouter(prefix='/chat', tags=['chat'])


@router.post(
             '/',
             response_model=ChatRequest,
             dependencies=[Depends(allowed_all_roles_access)],
             name='Send question to app.'
             )
async def send_a_question(
                          file_id: int,
                          question: str,
                          current_user: User = Depends(AuthUser.get_current_user),
                          credentials: HTTPAuthorizationCredentials = Security(security),
                          db: Session = Depends(get_db)
                          ) -> ChatRequest:
    return await RequestAnalyzer.save_question(user=current_user, file_id=file_id, question=question, db=db)


@router.get(
            '/answer',
            response_model=ChatResponse,
            dependencies=[Depends(allowed_all_roles_access)],
            name='Get Answer from model.'
            )
async def get_answer(
                     file_id: int = Query(...),
                     question_id: int = Query(...),
                     current_user: User = Depends(AuthUser.get_current_user),
                     credentials: HTTPAuthorizationCredentials = Security(security),
                     db: Session = Depends(get_db)
                     ) -> ChatResponse:
    return await RequestAnalyzer.return_answer(user=current_user, file_id=file_id, question_id=question_id, db=db)


@router.websocket('/ws/{token}')
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):  # token: str
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        response = await model_lln.get_answer(data, db)
        await websocket.send_text(response)
