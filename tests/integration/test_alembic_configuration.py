import os
import subprocess
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.integration


def test_alembic_upgrade_does_not_require_discord_token() -> None:
    repo_root = (
        Path(__file__).resolve().parents[2]
    )

    environ = os.environ.copy()

    environ.pop(
        "DISCORD_TOKEN",
        None,
    )

    environ["DATABASE_URL"] = (
        "postgresql+asyncpg://"
        "user:password@localhost:5432/test_db"
    )

    environ["PYTHON_DOTENV_DISABLED"] = "1"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "upgrade",
            "head",
            "--sql",
        ],
        cwd=repo_root,
        env=environ,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        result.stderr
    )

    assert "DISCORD_TOKEN" not in (
        result.stderr
    )