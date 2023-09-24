from typing import List

from fastapi import APIRouter, Depends, File, Query, Security, status, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.db import get_db
from db.models import User
from schemas.pdffile import PdfFileResponse
from services.auth.user import AuthUser, security
from services.pdf_controller import PDFController
from services.roles import allowed_all_roles_access


router = APIRouter(prefix='/pdffiles', tags=['pdffiles'])


@router.post(
             '/',
             response_model=PdfFileResponse,
             dependencies=[Depends(allowed_all_roles_access)],
             name='Upload text from pdf-file.'
             )
async def create_upload_file(
                             file: UploadFile = File(),
                             current_user: User = Depends(AuthUser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> PdfFileResponse:
    return await PDFController.upload_pdffile(user=current_user, file=file, db=db)


@router.get(
            '/',
            response_model=PdfFileResponse,
            dependencies=[Depends(allowed_all_roles_access)],
            name='Get user pdf-file text.'
            )
async def get_pdf_text(
                       file_id: int = Query(...),
                       current_user: User = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)
                       ) -> PdfFileResponse:
    return await PDFController.get_pdf_text(user=current_user, file_id=file_id, db=db)


@router.delete(
               '/',
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_all_roles_access)],
               name='Delete user pdf-file text.'
               )
async def del_pdf_text(
                       file_id: int = Query(...),
                       current_user: User = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)
                       ) -> None:
    await PDFController.del_pdf_text(user=current_user, file_id=file_id, db=db)
    return status.HTTP_204_NO_CONTENT


@router.get(
            '/get_user_files',
            response_model=List[PdfFileResponse],
            dependencies=[Depends(allowed_all_roles_access)],
            name='Get user pdf-file text.'
            )
async def get_pdf_text(
                       skip: int = 0,
                       limit: int = 10,
                       current_user: User = Depends(AuthUser.get_current_user),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: Session = Depends(get_db)
                       ) -> list[PdfFileResponse]:
    return await PDFController.get_all_user_pdf_text(user=current_user, skip=skip, limit=limit, db=db)
