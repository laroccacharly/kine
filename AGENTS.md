# Agent rules

The main goal of this project is to solve the inverse kinematics problem.

- Use **uv** for Python environments, dependency management, and running commands (`uv add`, `uv run`, `uv sync`). Do not use pip, poetry, or conda.
- Use **Pydantic** for data models, validation, and settings. Prefer `BaseModel` over dataclasses, TypedDict, or ad-hoc dicts.
- Use **pytest** for tests. Put tests under `tests/`. Run them with `uv run pytest`.

- Deploy with uv run modal deploy app.py 