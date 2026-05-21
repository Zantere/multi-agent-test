# AI Dungeon Map Explorer

A local-first FastAPI browser app for exploring generated dungeon maps.

## Run

```bash
python -m uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/`.

## Validate

```bash
python -m pytest
python -m compileall app
```
