import typer
import uvicorn

app = typer.Typer(add_completion=False)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run("kine.server:app", host=host, port=port)
