from io import BytesIO
from typing import List

from fastapi import HTTPException, UploadFile, status
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session

from conf.messages import Msg
from db.models import PDFfile, User
from repository.basic import BasicCRUD
from repository.pdffile import PDFCRUD
from schemas.pdffile import PdfFileBase, PdfFileResponse


class PDFController:

    @staticmethod
    async def upload_pdffile(user: User, file: UploadFile, db: Session) -> PdfFileResponse:
        pdf_data = await PDFController.get_txt_from_pdf(file)
        pdffile = PdfFileBase(
                              user_id=user.id,
                              filename=pdf_data.get('filename'),
                              context=pdf_data.get('text'),
                              )
        return await BasicCRUD.create_item(PDFfile, pdffile, db)

    @staticmethod
    async def get_pdf_text(user: User, file_id: int, db: Session) -> PdfFileResponse:
        pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
        if not pdf_text:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
        if user.id != pdf_text.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
        return pdf_text

    @staticmethod
    async def del_pdf_text(user: User, file_id: int, db: Session) -> None:
        pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
        if not pdf_text:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
        if user.id != pdf_text.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
        await BasicCRUD.delete_by_id(id_=file_id, model=PDFfile, db=db)

    @staticmethod
    async def get_all_user_pdf_text(user: User, skip: int, limit: int, db: Session) -> List[PdfFileResponse]:
        result = await PDFCRUD.get_by_user(user_id=user.id, skip=skip, limit=limit, db=db)
        for file in result:
            file.context = f'{file.context[:30]}...'
        return result

    @staticmethod
    async def get_txt_from_pdf(file: UploadFile) -> dict:
        # creating a pdf reader object
        # https://pypdf2.readthedocs.io/en/3.0.0/search.html?q=async&check_keywords=yes&area=default
        file_name, extension = file.filename.split('.')
        if extension != 'pdf':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_not_pdf.value)
        file_content = await file.read()
        pdf_file = BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        text = ''

        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()

        return {'filename': file_name, 'text': text}
