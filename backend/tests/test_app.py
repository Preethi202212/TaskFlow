"""Backend tests for TaskFlow.

Run from the backend/ directory: python -m pytest
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
from database import get_db_connection, init_db
from queries import task_count_per_column, tasks_by_priority


@pytest.fixture
def client():
    """Fresh temp DB per test, wired into both the Flask app and database module."""
    db_fd, db_path = tempfile.mkstemp()
    original_path = database.DB_PATH
    database.DB_PATH = db_path
    init_db(db_path)

    import app as flask_app_module
    flask_app_module.DB_PATH = db_path
    flask_app_module.app.config["TESTING"] = True

    with flask_app_module.app.test_client() as test_client:
        yield test_client

    database.DB_PATH = original_path
    os.close(db_fd)
    os.unlink(db_path)


def _seed_board():
    """Minimal board/column setup, used directly against the DB (not the API)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO boards (name) VALUES (?)", ("Test Board",))
    board_id = cur.lastrowid
    cur.execute(
        "INSERT INTO columns (board_id, name, position) VALUES (?, 'To Do', 0)",
        (board_id,),
    )
    todo_id = cur.lastrowid
    cur.execute(
        "INSERT INTO columns (board_id, name, position) VALUES (?, 'Done', 1)",
        (board_id,),
    )
    done_id = cur.lastrowid
    conn.commit()
    conn.close()
    return board_id, todo_id, done_id


# ---------- (1) creating a task with no title fails ----------

def test_create_task_without_title_fails(client):
    _, todo_id, _ = _seed_board()
    res = client.post("/api/tasks", json={"title": "   ", "column_id": todo_id})
    assert res.status_code == 400
    assert "title" in res.get_json()["error"].lower()


def test_create_task_with_title_succeeds(client):
    _, todo_id, _ = _seed_board()
    res = client.post(
        "/api/tasks",
        json={"title": "Write tests", "column_id": todo_id, "priority": "High"},
    )
    assert res.status_code == 201
    assert res.get_json()["title"] == "Write tests"


# ---------- (2) moving a task updates its status/column correctly ----------

def test_move_task_updates_column(client):
    _, todo_id, done_id = _seed_board()
    create_res = client.post(
        "/api/tasks", json={"title": "Ship feature", "column_id": todo_id}
    )
    task_id = create_res.get_json()["id"]

    move_res = client.patch(f"/api/tasks/{task_id}/move", json={"column_id": done_id})
    assert move_res.status_code == 200
    assert move_res.get_json()["column_id"] == done_id


# ---------- (3) a test that hits the database/query layer directly ----------

def test_task_count_per_column_query():
    db_fd, db_path = tempfile.mkstemp()
    try:
        init_db(db_path)
        conn = get_db_connection(db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO boards (name) VALUES ('B')")
        board_id = cur.lastrowid
        cur.execute(
            "INSERT INTO columns (board_id, name, position) VALUES (?, 'To Do', 0)",
            (board_id,),
        )
        col_id = cur.lastrowid
        cur.execute(
            "INSERT INTO tasks (column_id, title, priority) VALUES (?, 'A', 'High')",
            (col_id,),
        )
        cur.execute(
            "INSERT INTO tasks (column_id, title, priority) VALUES (?, 'B', 'Low')",
            (col_id,),
        )
        conn.commit()

        rows = task_count_per_column(conn, board_id)
        assert len(rows) == 1
        assert rows[0]["task_count"] == 2

        high_rows = tasks_by_priority(conn, board_id, "High")
        assert len(high_rows) == 1
        assert high_rows[0]["title"] == "A"
        conn.close()
    finally:
        os.close(db_fd)
        os.unlink(db_path)
