import subprocess

from ruff import find_ruff_bin
from ty import find_ty_bin


def version(command: str) -> str:
    result = subprocess.run(
        (command, "--version"),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run(name: str, command: tuple[str, ...]) -> None:
    print(f"Running {name} ({version(command[0])})...", flush=True)
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> None:
    run("Ruff", (find_ruff_bin(), "check"))
    run("ty", (find_ty_bin(), "check"))
    run("Bun lint", ("bun", "run", "--cwd", "ui", "lint"))
    print("lint ok")
