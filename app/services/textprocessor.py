# from PyPDF2 import PdfReader
from conf.messages import Msg
from db.models import Question, PDFfile, User
from fastapi import HTTPException, status
from repository.basic import BasicCRUD
from sqlalchemy.orm import Session
from transformers import pipeline

from schemas.chat import ChatResponse, ChatRequest


# # moved to PDFController in pdf_controller ?:
# # https://pypdf2.readthedocs.io/en/3.0.0/search.html?q=async&check_keywords=yes&area=default
# def get_txt_from_pdf(file: str) -> str:
#     """Creating a pdf reader object."""
#     reader = PdfReader(file)
#     text = ''

#     for page in range(len(reader.pages)):
#         text += reader.pages[page].extract_text()

#     return text
    

qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')


class RequestAnalyzer:

    @staticmethod
    async def get_the_answer(
                             qa_model: pipeline = qa_model, 
                             question: str = 'Is there a question?', 
                             context: str = 'I don\'t see the request.'
                             ) -> dict:
        """Returns an answer by model."""
        # question = "Where do we live?"
        # context = "We are the Fast Rabbit team and we live in Kyiv."
        return qa_model(question = question, context = context)
        ## {'answer': 'Kyiv', 'end': 39, 'score': 0.953, 'start': 31}

    # user=current_user, pdffile_id=pdffile_id, question=question, db=db
    @staticmethod
    async def return_answer(user: User, file_id: int, question_id: int, db: Session) -> ChatResponse:
        # get txt from db
        pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
        question = await BasicCRUD.get_by_id(id_=question_id, model=Question, db=db) # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if not pdf_text:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
        if user.id != pdf_text.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
        # throw question and text to model
        return await RequestAnalyzer.get_the_answer(qa_model=qa_model, question=question, context=pdf_text)

    @staticmethod
    async def save_question(user: User, file_id: int, question: str, db: Session) -> ChatRequest:
        # get txt from db
        pdf_text = await BasicCRUD.get_by_id(id_=file_id, model=PDFfile, db=db)
        if not pdf_text:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Msg.m_404_file_not_found.value)
        if user.id != pdf_text.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Msg.m_403_foreign_file.value)
        # save question ? history ? to db!
        question = ChatRequest(
                               user_id=user.id,
                               pdffile_id=file_id,
                               question=question,
                               # created_at: datetime
                               )
        return await BasicCRUD.create_item(Question, question, db)

    # @staticmethod
    # another functions ? compare? generate? correcting? ....
