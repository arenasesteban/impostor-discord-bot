from sqlalchemy.exc import (
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)

from impostor_bot.errors.infrastructure import (
    DatabaseError,
    DatabaseUnavailableError,
)
from impostor_bot.infrastructure.database.error_translation import (
    translate_database_error,
)


def test_operational_error_becomes_database_unavailable():
    source = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception(
            "connection refused"
        ),
    )

    translated = translate_database_error(
        source
    )

    assert isinstance(
        translated,
        DatabaseUnavailableError,
    )


def test_interface_error_becomes_database_unavailable():
    source = InterfaceError(
        statement="SELECT 1",
        params={},
        orig=Exception(
            "connection unavailable"
        ),
    )

    translated = translate_database_error(
        source
    )

    assert isinstance(
        translated,
        DatabaseUnavailableError,
    )


def test_generic_sqlalchemy_error_becomes_database_error():
    translated = translate_database_error(
        SQLAlchemyError(
            "unexpected database error"
        )
    )

    assert type(translated) is DatabaseError


def test_connection_refused_error_becomes_database_unavailable():
    source = ConnectionRefusedError(
        1225,
        "Connection refused",
    )

    translated = (
        translate_database_error(
            source
        )
    )

    assert isinstance(
        translated,
        DatabaseUnavailableError,
    )