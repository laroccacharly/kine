# Agent rules

- Use **uv** for Python environments, dependency management, and running commands (`uv add`, `uv run`, `uv sync`)
- Use **Pydantic** for data models, validation, and settings. 
- Use **pytest** for tests. Put tests under `tests/`. Run them with `uv run pytest`.
- Deploy with `uv run deploy` (`modal deploy app.py`) 