from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, DateTime, select
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f'postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
engine = create_async_engine(db_url)
async_session = async_sessionmaker(engine, class_=AsyncSession,expire_on_commit=False)
Base = declarative_base()


class Stats(Base):
    __tablename__ = 'stats'
    id = Column(Integer, primary_key=True)
    listeners_yam = Column(Integer)
    listeners_spotify = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


async def delete_oldest(session: AsyncSession):
    count_result = await session.execute(select(Stats.id))
    count = len(count_result.scalars().all())

    if count > 10:
        oldest_result = await session.execute(
            select(Stats).order_by(Stats.created_at.asc()).limit(1)
        )
        oldest = oldest_result.scalars().first()

        if oldest:
            await session.delete(oldest)
            await session.commit()


async def init_db():
    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()


async def main():
    await init_db()


if __name__ == '__main__':
    asyncio.run(main())


