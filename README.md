# TaskFlow

A lightweight task board (Trello-style) for small teams — built as a take-home
assignment. React frontend, Flask + SQLite backend.

## Tech stack

- **Frontend:** React (Vite)
- **Backend:** Python (Flask)
- **Database:** SQLite (see `backend/schema.sql`)

## Project structure

```
taskflow/
├── backend/
│   ├── app.py          # Flask app & all API routes
│   ├── database.py      # DB connection + init helper
│   ├── schema.sql        # Table definitions (boards, columns, tasks)
│   ├── queries.py        # The two "non-trivial" SQL queries
│   ├── seed.py            # Seeds a demo board with sample data
│   ├── requirements.txt
│   └── tests/
│       └── test_app.py    # pytest suite
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── TaskCard.jsx
    │   ├── NewTaskForm.jsx
    │   ├── api.js
    │   └── styles.css
    └── package.json
```

## Setup — from a fresh clone

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                   # creates taskflow.db with sample data
python app.py                    # runs on http://127.0.0.1:5000
```

### 2. Frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev                      # runs on http://localhost:5173
```

Open `http://localhost:5173` in your browser. The frontend talks to the
backend at `http://127.0.0.1:5000` — both need to be running.

### 3. Running tests

```bash
cd backend
python -m pytest
```

## Database schema

```sql
boards(id, name, created_at)
columns(id, board_id -> boards.id, name, position)
tasks(id, column_id -> columns.id, title NOT NULL, description, priority CHECK IN (Low, Medium, High), created_at)
```

Foreign keys: `columns.board_id → boards.id`, `tasks.column_id → columns.id`
(both `ON DELETE CASCADE`). See `backend/schema.sql` for the full DDL.

The two required non-trivial queries live in `backend/queries.py`:
- `task_count_per_column` — count of tasks per column on a board (LEFT JOIN + GROUP BY, so empty columns still show).
- `tasks_by_priority` — tasks of a given priority on a board, newest first (JOIN + WHERE + ORDER BY).

## Decisions & assumptions

- Single hardcoded board (`board_id = 1`, created by `seed.py`) — the brief
  scopes out multi-board/multi-user support, so the frontend doesn't build a
  board picker.
- Moving a task between columns uses a dropdown per the brief's guidance that
  "a working dropdown beats a broken drag-and-drop" within the time budget.
- Priority filtering is done via a backend query parameter (`?priority=High`)
  rather than filtering already-fetched data client-side, so it's a real
  filtered query.
- Title validation is enforced both in the React form and in the Flask route
  (empty/whitespace-only titles are rejected with a 400 and a clear message).
- Failed requests surface a dismissible error banner with a retry button
  instead of a blank screen or console-only error.

## What I'd add with more time

- Drag-and-drop as a stretch goal on top of the dropdown.
- Text search by task title.
- Deployment to a live host (Render/Railway) so the reviewer can open a link
  directly.

## Time spent

Roughly [FILL IN — e.g. "5-6 hours across backend, frontend, and tests"].

## Something I found interesting

[FILL IN — one line about anything that caught your attention while building
this, e.g. why `LEFT JOIN` was needed instead of a plain `JOIN` to make empty
columns still show up in the count query, or something about SQLite foreign
key enforcement.]
