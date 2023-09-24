import sys
import os
cwd = os.getcwd()
# sys.path.append(f'{cwd}/app')
sys.path.append(f'{cwd}\\app')

import uvicorn
from fastapi.templating import Jinja2Templates

from conf.config import get_settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import auth, chat, history, pdffile, users, pages
from services.loggs.loger import logger

credentials = get_settings()

app = FastAPI()
app.mount("/static", StaticFiles(directory=credentials.path_static), name="static")
templates = Jinja2Templates(directory=credentials.path_templates)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(pdffile.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(pages.router)
# app.mount('/templates', StaticFiles(directory='templates'), name='templates')
# app.mount('/services/chat/templates', StaticFiles(directory='services/chat/templates'), name='templates')
# app.mount(f'/app/templates', StaticFiles(directory=f'/app/templates'), name='templates')

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def get_index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/healthchecker')
async def healthchecker() -> dict:
    logger.warning('App started')
    logger.debug('Everything is Ok')
    return {
        'status_code': 200,
        'detail': 'ok',
        'result': 'working',
    }


if __name__ == '__main__':
    # credentials = get_settings()
    uvicorn.run('main:app', host=credentials.uvicorn_host, port=credentials.uvicorn_port, reload=True)


# http://127.0.0.1:8000
# http://127.0.0.1:8000/docs
