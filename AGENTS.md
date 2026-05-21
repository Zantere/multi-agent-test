# AGENTS.md

## Project

This is a Python browser app called AI Dungeon Map Explorer.

The app uses:
- FastAPI for the backend
- Vanilla HTML/CSS/JavaScript for the browser UI
- pytest for tests
- optional SQLite only if persistence is needed

## Goal

Create a fun browser-based dungeon explorer where the user can:
- generate a dungeon map
- click rooms
- see room descriptions
- encounter monsters, NPCs, traps, and loot
- keep simple player stats in browser state
- reset or regenerate the dungeon

## Engineering rules

- Keep the app simple and local-first.
- Do not require paid APIs.
- Do not add unnecessary frameworks.
- Prefer readable Python and plain JavaScript.
- Keep files small and easy to review.
- Add comments where logic is non-obvious.
- Do not modify unrelated files.

## Validation

Before saying the work is done, run:

```bash
python -m pytest
python -m compileall app