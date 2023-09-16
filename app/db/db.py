from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def get_db():
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
