# Stage 1 Task

A FastAPI backend that accepts a name, calls three external APIs (Genderize, Agify, Nationalize), applies classification logic, stores the result in a SQLite database, and exposes endpoints to manage the data.

## Requirements

- Python 3.10+
- `uv` (Fast Python package installer and resolver)

## Setup and Installation

1. Create a virtual environment and install dependencies using `uv`:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

Alternatively, `uv` will just install from `pyproject.toml`.

2. Run the server:

```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, navigate to `http://127.0.0.1:8000/docs` to view the interactive API documentation (Swagger UI).
