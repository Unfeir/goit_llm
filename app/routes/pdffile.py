import pathlib
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Security, status, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from conf.messages import Msg
from db.db import get_db
from db.models import User, UserRole
from repository.users import UserCRUD
from repository.pdffile import PDFfiles
from schemas.user import UserResponse, UserUpdate, UserFullUpdate
from services.auth.user import AuthUser, security
from services.images import CloudImage
from services.loggs.loger import logger
from services.roles import allowed_all_roles_access, allowed_admin

# from services.textprocessor import get_txt_from_pdf


router = APIRouter(prefix='/pdffiles', tags=['pdffiles'])


@router.post('/uploadfile/',
             # response_model=UserResponse,
             dependencies=[Depends(allowed_all_roles_access)],
             name='Upload text from pdf-file.')
async def create_upload_file(
                             file: UploadFile = File(),
                             current_user: User = Depends(AuthUser.get_current_user),
                             credentials: HTTPAuthorizationCredentials = Security(security),
                             db: Session = Depends(get_db)
                             ) -> dict:
    
    # typ = User.__name__
    # src_url: str = CloudImage.avatar_upload(file=file.file, typ=typ, email=current_user.email)
    user = await PDFfiles.upload_pdffile(user=current_user, file=file, db=db)
    return user
   