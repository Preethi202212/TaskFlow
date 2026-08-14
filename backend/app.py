"""TaskFlow backend — Flask + SQLite.

Run: python app.py  (serves on http://localhost:5000)
"""
import os
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import get_db_connection, init_db, DB_PATH
from queries import task_count_per_column, tasks_by_priority

app = Flask(__name__)
CORS(app)

VALID_PRIORITIES = {"Low", "Medium", "High"}


# ---------- helpers ----------

def row_to_task(row):
    return {
        "id": row["id"],
        "column_id": row["column_id"],
        "title": row["title"],
        "description": row["description"],
        "priority": row["priority"],
        "created_at": row["created_at"],
    }


def error_response(message, status=400):
    return jsonify({"error": message}), status


@app.errorhandler(404)
def not_found(e):
    return error_response("Not found", 404)


@app.errorhandler(500)
def server_error(e):
    return error_response("Something went wrong on our end. Please try again.", 500)


# ---------- board ----------

@app.route("/api/boards/<int:board_id>", methods=["GET"])
def get_board(board_id):
    conn = get_db_connection()
    board = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
    if not board:
        conn.close()
        return error_response("Board not found", 404)

    columns = conn.execute(
        "SELECT * FROM columns WHERE board_id = ? ORDER BY position", (board_id,)
    ).fetchall()

    priority_filter = request.args.get("priority")
    result_columns = []
    for col in columns:
        if priority_filter and priority_filter in VALID_PRIORITIES:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE column_id = ? AND priority = ? ORDER BY created_at DESC",
                (col["id"], priority_filter),
            ).fetchall()
        else:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE column_id = ? ORDER BY created_at DESC",
                (col["id"],),
            ).fetchall()
        result_columns.append({
            "id": col["id"],
            "name": col["name"],
            "position": col["position"],
            "tasks": [row_to_task(t) for t in tasks],
        })

    conn.close()
    return jsonify({
        "id": board["id"],
        "name": board["name"],
        "columns": result_columns,
    })


# ---------- tasks: create / edit / delete / move ----------

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    column_id = data.get("column_id")
    priority = data.get("priority", "Medium")
    description = data.get("description")

    if not title:
        return error_response("Title is required.")
    if not column_id:
        return error_response("column_id is required.")
    if priority not in VALID_PRIORITIES:
        return error_response("Priority must be Low, Medium, or High.")

    conn = get_db_connection()
    col = conn.execute("SELECT id FROM columns WHERE id = ?", (column_id,)).fetchone()
    if not col:
        conn.close()
        return error_response("Column not found.", 404)

    cur = conn.execute(
        "INSERT INTO tasks (column_id, title, description, priority) VALUES (?, ?, ?, ?)",
        (column_id, title, description, priority),
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return jsonify(row_to_task(task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        return error_response("Task not found.", 404)

    title = data.get("title", existing["title"])
    title = (title or "").strip()
    if not title:
        conn.close()
        return error_response("Title is required.")

    description = data.get("description", existing["description"])
    priority = data.get("priority", existing["priority"])
    if priority not in VALID_PRIORITIES:
        conn.close()
        return error_response("Priority must be Low, Medium, or High.")

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, priority = ? WHERE id = ?",
        (title, description, priority, task_id),
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_task(task))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not existing:
        conn.close()
        return error_response("Task not found.", 404)
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": task_id})


@app.route("/api/tasks/<int:task_id>/move", methods=["PATCH"])
def move_task(task_id):
    data = request.get_json(silent=True) or {}
    new_column_id = data.get("column_id")
    if not new_column_id:
        return error_response("column_id is required.")

    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        conn.close()
        return error_response("Task not found.", 404)
    col = conn.execute("SELECT id FROM columns WHERE id = ?", (new_column_id,)).fetchone()
    if not col:
        conn.close()
        return error_response("Target column not found.", 404)

    conn.execute("UPDATE tasks SET column_id = ? WHERE id = ?", (new_column_id, task_id))
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(row_to_task(task))


# ---------- stats (demonstrate the two required non-trivial queries) ----------

@app.route("/api/boards/<int:board_id>/stats/column-counts", methods=["GET"])
def column_counts(board_id):
    conn = get_db_connection()
    rows = task_count_per_column(conn, board_id)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/boards/<int:board_id>/stats/by-priority", methods=["GET"])
def by_priority(board_id):
    priority = request.args.get("priority", "High")
    if priority not in VALID_PRIORITIES:
        return error_response("Priority must be Low, Medium, or High.")
    conn = get_db_connection()
    rows = tasks_by_priority(conn, board_id, priority)
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
