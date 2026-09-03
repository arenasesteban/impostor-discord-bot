import re
from collections.abc import Mapping


REDACTED = "[REDACTED]"

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "token",
        "discord_token",
        "authorization",
        "database_url",
        "secret",
        "secret_word",
        "impostor_id",
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret"
    }
)


_URI_CREDENTIALS_PATTERN  = re.compile(
    r"([a-zA-Z][a-zA-Z0-9+.-]*://"
    r"[^:/\s]+:)"
    r"[^@\s]+"
    r"(@)"
)


_BEARER_PATTERN  = re.compile(
    r"(?i)\bBearer\s+\S+"
)


_SECRET_ASSIGNMENT_PATTERN  = re.compile(
    r"(?i)\b"
    r"(password|token|secret|authorization|api[_-]?key)"
    r"\s*[:=]\s*"
    r"[^\s,;]+"
)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")


def redact_string(value: str, sensitive_values: tuple[str, ...] = ()) -> str:
    result = value

    for secret in sensitive_values:
        if secret:
            result = result.replace(secret, REDACTED)

    result = _URI_CREDENTIALS_PATTERN.sub(rf"\1{REDACTED}\2", result)

    result = _BEARER_PATTERN.sub(f"Bearer {REDACTED}", result)

    result = _SECRET_ASSIGNMENT_PATTERN.sub(
        lambda match: (
            f"{match.group(1)}="
            f"{REDACTED}"
        ), 
        result
    )

    return result


def sanitize_value(value: object, *, key: str | None = None, sensitive_values: tuple[str, ...] = ()) -> object:
    if (key is not None and _normalize_key(key) in SENSITIVE_KEYS):
        return REDACTED

    if value is None:
        return None

    if isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        return redact_string(value, sensitive_values)

    if isinstance(value, Mapping):
        return {
            str(child_key): sanitize_value(
                child_value,
                key=str(child_key),
                sensitive_values=sensitive_values
            )
            for child_key, child_value in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [
            sanitize_value(
                item,
                sensitive_values=sensitive_values
            )
            for item in value
        ]

    return f"<{type(value).__name__}>"
