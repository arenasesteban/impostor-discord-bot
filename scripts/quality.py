from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence


def run_check(name: str, command: Sequence[str]) -> int:
    print(f"\n==> {name}")

    result = subprocess.run(
        command,
        check=False,
    )

    if result.returncode != 0:
        print(
            f"\n{name} failed "
            f"with exit code "
            f"{result.returncode}."
        )

    return result.returncode


def main() -> int:
    ruff = shutil.which("ruff")

    if ruff is None:
        print("Ruff is not installed or is not available in PATH.")
        return 1

    checks = (
        ("Ruff", (ruff, "check", ".")),
        ("mypy", (sys.executable, "-m", "mypy","src/")),
        ("pytest", (sys.executable, "-m", "pytest")),
    )

    for name, command in checks:
        return_code = run_check(name, command)

        if return_code != 0:
            return return_code

    print("\nAll quality checks passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())