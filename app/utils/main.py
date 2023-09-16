from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import uvicorn
from sqlalchemy.orm import Session

from conf.config import get_settings
from db.db import get_db
from services.loggs.loger import logger
from routes import users, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


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


if __name__ == '__main__':
    credentials = get_settings()
    uvicorn.run('main:app', host=credentials.uvicorn_host, port=credentials.uvicorn_port, reload=True)
