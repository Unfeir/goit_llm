from typing import List, Optional

from db.db import get_db
from db.models import User
from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPAuthorizationCredentials
from schemas.history import HistoryResponse
from services.auth.user import AuthUser, security
from services.history_controller import HistoryController
from services.roles import allowed_all_roles_access
from sqlalchemy.orm import Session

router = APIRouter(prefix='/history', tags=['history'])


@router.get(
    '/get_file_history',
    response_model=List[HistoryResponse],
    dependencies=[Depends(allowed_all_roles_access)],
    name='Get history on file'
)
async def get_file_history(
        file_id: int = Query(...),
        skip: int = 0,
        limit

        : int = 10,
        current_user: User = Depends(AuthUser.get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db)
) -> List[Optional[HistoryResponse]]:

    return await HistoryController.get_file_history(file_id=file_id, user_id=current_user.id,
                                                    skip=skip, limit=limit, db=db)

#
# @router.get(
#             '/',
#             response_model=PdfFileResponse,
#             dependencies=[Depends(allowed_all_roles_access)],
#             name='Get user pdf-file text.'
#             )
# async def get_pdf_text(
#                        file_id: int = Query(...),
#                        current_user: User = Depends(AuthUser.get_current_user),
#                        credentials: HTTPAuthorizationCredentials = Security(security),
#                        db: Session = Depends(get_db)
#                        ) -> PdfFileResponse:
#     return await PDFController.get_pdf_text(user=current_user, file_id=file_id, db=db)
#

# @router.delete(
#                '/',
#                status_code=status.HTTP_204_NO_CONTENT,
#                dependencies=[Depends(allowed_all_roles_access)],
#                name='Delete user pdf-file text.'
#                )
# async def del_pdf_text(
#                        file_id: int = Query(...),
#                        current_user: User = Depends(AuthUser.get_current_user),
#                        credentials: HTTPAuthorizationCredentials = Security(security),
#                        db: Session = Depends(get_db)
#                        ) -> None:
#     await PDFController.del_pdf_text(user=current_user, file_id=file_id, db=db)
#     return status.HTTP_204_NO_CONTENT
