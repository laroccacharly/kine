import subprocess
import sys

import typer
import uvicorn

from kine.server import create_app
from kine.ui import UI

app = typer.Typer(add_completion=False)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    ui = UI()
    ui.build()
    uvicorn.run(create_app(ui), host=host, port=port)


def deploy() -> None:
    result = subprocess.run(("modal", "deploy", "app.py", *sys.argv[1:]), check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
