from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


AsyncSessionFactory = async_sessionmaker[AsyncSession]


def create_database_engine(
    database_url: str,
) -> AsyncEngine:
    return create_async_engine(
        database_url,
        pool_pre_ping=True,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> AsyncSessionFactory:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )