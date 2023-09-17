from datetime import datetime
import pathlib
from tempfile import SpooledTemporaryFile
from typing import Union, Optional

from fastapi import File, UploadFile
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload

from db.models import User, PDFfile
from repository.basic import BasicCRUD
from repository.users import UserCRUD
from schemas.pdffile import PdfFileRequest
from schemas.user import UserUpdate, UserFullUpdate
from services.auth.password import AuthPassword
from services.loggs.loger import logger
from services.textprocessor import get_txt_from_pdf


class PDFfiles(BasicCRUD):

    @classmethod  # model=current_user, file=file.file, db=db
    async def upload_pdffile(cls, user: User, file: UploadFile, db: Session) -> User:
        email = User.email
        user: Optional[User] = await UserCRUD.get_user_by_email(email=email, db=db)

        if user is not None:
            print('\n*' * 3)
            print(file.filename)
            # file_type = file.filename.split('.')[-1].lower()
            # https://docs.python.org/2/library/tempfile.html
            file_type = file.filename.split('.')[-1].lower()

            if file_type == 'pdf':
                pathlib.Path(f"uploads_{user.id}").mkdir(exist_ok=True)
                file_path = f"uploads_{user.id}/{file.filename}"  # file.filename
                with open(file_path, 'wb') as f:
                    f.write(await file.read())

            else:
                return {'file_text': f'Incorrect file-type. {file_type} not a PDF.'}
            # username = payload.get('username')
            # dummy_password = AuthPassword.get_hash_password(password=f'{email}{datetime.utcnow().timestamp()}')
            # password = payload.get('password', dummy_password)
            text = get_txt_from_pdf(file_path)
            print('\n*' * 3)
            print(text)
            pdffile = PdfFileRequest(
                filename=file.filename,
                context=text,  # 'example.pdf'
                user_id=user.id,
            )
            print(f'{pdffile=}')
            # pdffile = {'filename': file,
            #            'context': 'text',
            #            'user_id': user.id}
            # del file
            pathlib.Path(file_path).unlink(missing_ok=True)
            result = await cls.create_item(PDFfile, pdffile, db)
            print(f'{result=}')
            # db.add(pdffile)
            # await db.commit()
            # await db.refresh(pdffile)
            logger.warning(f'Upload PDF-file({file}) by User:  {email=}')

        return {'file_text': text}

    # @classmethod
    # async def get_or_create(cls, payload: dict, db: Session) -> User:
    #     email = payload.get("email")
    #     user: Optional[User] = await PDFfiles.get_user_by_email(email=email, db=db)

    #     if user is None:
    #         username = payload.get('username')
    #         dummy_password = AuthPassword.get_hash_password(password=f'{email}{datetime.utcnow().timestamp()}')
    #         password = payload.get('password', dummy_password)
    #         user = User(
    #                     email=email,
    #                     username=username,
    #                     password=password
    #                     )
    #         db.add(user)
    #         await db.commit()
    #         await db.refresh(user)
    #         logger.warning(f'creating User with {email=}')

    #     return user

    # # @classmethod
    # # async def get_user_by_email(cls, email: str, db: Session) -> User:
    # #     query = select(User).where(User.email == email)
    # #     result = await db.execute(query)
    # #     user = result.scalars().first()
    # #     return user

    # @classmethod
    # async def update_user_profile(cls, user: User, body: Union[UserUpdate, UserFullUpdate], db: Session) -> User:
    #     for field_name, value in body:
    #         if value not in ('string', 'user@example.com', None) and field_name in user.mapper:
    #             setattr(user, user.mapper[field_name], value)

    #     await db.commit()
    #     await db.refresh(user)
    #     changes = {el[0]: el[1] for el in body if el[1] not in ('string', 'user@example.com', None)}
    #     logger.warning(f'update user profile {user.email} with: {changes}')

    #     return user

    # @classmethod
    # async def ban_user(cls, user: User, active_status: bool,  db: Session) -> User:
    #     user.status_active = active_status
    #     await db.commit()
    #     await db.refresh(user)
    #     logger.warning(f'update user profile {user.email} was banned')
    #     return user


