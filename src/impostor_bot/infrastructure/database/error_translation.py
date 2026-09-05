from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError, SQLAlchemyError

from impostor_bot.errors.infrastructure import DatabaseError, DatabaseUnavailableError


def translate_database_error(error: SQLAlchemyError) -> DatabaseError:
    if isinstance(error, (OperationalError, InterfaceError, OSError)):
        return DatabaseUnavailableError(
            "Database is unavailable."
        )

    if isinstance(error, DBAPIError) and error.connection_invalidated:
        return DatabaseUnavailableError(
            "Database connection was invalidated."
        )

    return DatabaseError(
        "Database operation failed."
    )
