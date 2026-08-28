import re
import subprocess
import sys
from pathlib import Path

import modal
import typer
import uvicorn

from kine.server import create_app
from kine.ui import UI

app = typer.Typer(add_completion=False)

REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
DEMO_URL_RE = re.compile(
    r"(?P<prefix>\[Demo app\]\()(?P<url>[^)]*)(?P<suffix>\) <!-- demo-app-url -->)"
)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    ui = UI()
    ui.build()
    uvicorn.run(create_app(ui), host=host, port=port)


def frontend_url() -> str:
    url = modal.Server.from_name("kine", "Frontend").get_url()
    if url is None:
        raise SystemExit("deployed kine Frontend has no URL")
    return url


def update_readme_demo_url(url: str) -> None:
    text = README_PATH.read_text()
    if not DEMO_URL_RE.search(text):
        raise SystemExit("README.md is missing the [Demo app](...) <!-- demo-app-url --> placeholder")
    README_PATH.write_text(
        DEMO_URL_RE.sub(lambda match: f"{match['prefix']}{url}{match['suffix']}", text, count=1)
    )


def deploy() -> None:
    result = subprocess.run(("modal", "deploy", "app.py", *sys.argv[1:]), check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
    url = frontend_url()
    update_readme_demo_url(url)
    print(url)
