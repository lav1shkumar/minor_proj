# FastAPI backend

Run from this directory:

```bash
uv sync
uv run uvicorn main:app --reload
```

SQLite stores data in `backend/database.db`, created automatically when the app
starts. No database server, Docker, or credentials are needed. The database file
is ignored by Git.

Visit <http://localhost:8000/db-check> to verify the connection. It should return
`{"connected": true}`. Interactive API docs are at <http://localhost:8000/docs>.

`database.py` manages the connection and provides `get_session` for routes:

```python
from fastapi import Depends
from sqlmodel import Session
from database import get_session

@router.get("/example")
def example(session: Session = Depends(get_session)):
    # Use this session to read or save data.
    return {"message": "Session ready"}
```

No application tables are defined yet. When adding SQLModel table models, import
them before `create_db_and_tables()` runs so their tables are created at startup.
This creates missing tables; it does not migrate existing table definitions.
The auth routes are currently placeholders and do not store users yet.
