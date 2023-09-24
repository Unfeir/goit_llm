from typing import List, Optional

from fastapi import APIRouter, Depends, Security, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.db import get_db
from db.models import User
from schemas.history import HistoryResponse
from services.auth.user import AuthUser, security
from services.history_controller import HistoryController
from services.roles import allowed_all_roles_access


router = APIRouter(prefix='/history', tags=['history'])


@router.get(
            '/get_file_history',
            response_model=List[HistoryResponse],
            dependencies=[Depends(allowed_all_roles_access)],
            name='Get history on file.'
            )
async def get_file_history(
                           file_id: int = Query(...),
                           skip: int = 0,
                           limit: int = 10,
                           current_user: User = Depends(AuthUser.get_current_user),
                           credentials: HTTPAuthorizationCredentials = Security(security),
                           db: Session = Depends(get_db)
                           ) -> List[Optional[HistoryResponse]]:
    return await HistoryController.get_file_history(
                                                    file_id=file_id,
                                                    user_id=current_user.id,
                                                    skip=skip,
                                                    limit=limit,
                                                    db=db
                                                    )
