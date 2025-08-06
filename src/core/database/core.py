import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.configuration import conf

from .base import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(conf.db.build_connection_str(), echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def getDBSession():
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
