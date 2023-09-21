from typing import Any, Annotated

from starlette.responses import RedirectResponse

from db.db import get_db
from db.models import User
from services.auth.token import AuthToken
from fastapi import APIRouter, Depends, Query, Security, WebSocket
from fastapi.security import HTTPAuthorizationCredentials
from schemas.chat import ChatRequest, ChatResponse
from services.auth.user import AuthUser, security
from services.chat.chat_controller import manager, model
from services.loggs.loger import logger
from services.roles import allowed_all_roles_access
from services.textprocessor import RequestAnalyzer
from sqlalchemy.orm import Session

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


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    logger.debug(f'{client_id=}')
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        logger.debug(f'{data=}')
        response = await model.get_answer(data)
        # await manager.broadcast(f"Client {client_id}: {data}")
        await websocket.send_text(f'response = {response}')


from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")


@router.get(
    '/get_caht',
    response_class=RedirectResponse,
    dependencies=[Depends(allowed_all_roles_access)],
    name='Get Answer from model.'
)
async def get_answer(request: Request,
                     token: Annotated[str, Depends(AuthToken.oauth2_scheme)],
                     current_user: User = Depends(AuthUser.get_current_user),
                     credentials: HTTPAuthorizationCredentials = Security(security),
                     db: Session = Depends(get_db)
                     ) -> Any:
    variable = token

    print(f'{templates=}')
    return templates.TemplateResponse("chat.html", {"request": request, "variable": variable})
