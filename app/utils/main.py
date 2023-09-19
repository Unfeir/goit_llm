import sys
import os
cwd = os.getcwd()
sys.path.append(f'{cwd}/app')
from typing import List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

from conf.config import get_settings
from db.db import get_db
from routes import auth, users, pdffile, chat
from services.loggs.loger import logger
import templates

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(pdffile.router)
app.include_router(chat.router)
# app.mount(f'/templates', StaticFiles(directory=f'templates'), name='templates')
app.mount(f'/app/templates', StaticFiles(directory=f'{cwd}/app/templates'), name='templates')

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


@app.get("/")
async def healthchecker() -> dict:
    logger.warning('App started')
    logger.debug('Everything is Ok')
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working",
    }


@app.get('/db_checker')
async def db_checker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text('SELECT 1')).fetchone()
        if result is None:
            logger.error('Database is not configured correctly.')
            raise HTTPException(status_code=500, detail='Database is not configured correctly.')

        return {'message': 'Welcome'}
    
    except Exception:
        logger.error('Error connecting to the database.')
        raise HTTPException(status_code=500, detail='Error connecting to the database.')


# ----- alternative simplest CHAT --ok------------------------

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    # def disconnect(self, websocket: WebSocket, user: str):
    #     self.connections.remove((websocket, user))

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(f"Client {client_id}: {data}")
        

if __name__ == '__main__':
    credentials = get_settings()
    uvicorn.run('main:app', host=credentials.uvicorn_host, port=credentials.uvicorn_port, reload=True)

# http://127.0.0.1:8000/docs
