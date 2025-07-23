import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.configuration import getSettings
from src.database.base import Base

settings = getSettings()

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


async def getSession():
    async with async_session() as session:
        yield session


async def createTables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Created tables")


async def dropTables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped tables")
