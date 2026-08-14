"""Seeds a fresh database with one board, three columns, and a handful of tasks.

Run: python seed.py
"""
from database import init_db, get_db_connection


def seed():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO boards (name) VALUES (?)", ("TaskFlow Demo Board",))
    board_id = cur.lastrowid

    column_names = ["To Do", "In Progress", "Done"]
    column_ids = {}
    for i, name in enumerate(column_names):
        cur.execute(
            "INSERT INTO columns (board_id, name, position) VALUES (?, ?, ?)",
            (board_id, name, i),
        )
        column_ids[name] = cur.lastrowid

    tasks = [
        ("Set up project repo", "Init frontend + backend scaffolding", "Medium", "To Do"),
        ("Design DB schema", "Boards, columns, tasks with FKs", "High", "To Do"),
        ("Write seed script", None, "Low", "To Do"),
        ("Build task API", "CRUD endpoints for tasks", "High", "In Progress"),
        ("Add drag-and-drop", "Move tasks between columns", "Medium", "In Progress"),
        ("Write backend tests", "Cover validation + query layer", "High", "Done"),
    ]
    for title, description, priority, column_name in tasks:
        cur.execute(
            "INSERT INTO tasks (column_id, title, description, priority) VALUES (?, ?, ?, ?)",
            (column_ids[column_name], title, description, priority),
        )

    conn.commit()
    conn.close()
    print(f"Seeded board_id={board_id} with {len(tasks)} tasks.")


if __name__ == "__main__":
    seed()
