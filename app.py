import subprocess

import modal

REMOTE_UI_DIST = "/ui/dist"

image = modal.Image.debian_slim(python_version="3.12").uv_sync().add_local_python_source("kine")
if modal.is_local():
    from kine.ui import UI

    ui = UI()
    ui.build()
    image = image.add_local_dir(ui.dist_dir, remote_path=REMOTE_UI_DIST)

app = modal.App("kine", image=image)


def serve_command(*, host: str = "0.0.0.0", port: int = 8000) -> list[str]:
    return [
        "uvicorn",
        "kine.server:create_ui_app",
        "--factory",
        "--host",
        host,
        "--port",
        str(port),
    ]


@app.server(unauthenticated=True)
class Frontend:
    @modal.enter()
    def start(self) -> None:
        subprocess.Popen(serve_command())
