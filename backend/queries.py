"""Queries that go beyond simple 'get all rows' — written as real SQL, not
ORM default methods, per the assignment brief.
"""


def task_count_per_column(conn, board_id):
    """Count of tasks in every column of a board (including empty columns)."""
    sql = """
        SELECT c.id AS column_id, c.name AS column_name, COUNT(t.id) AS task_count
        FROM columns c
        LEFT JOIN tasks t ON t.column_id = c.id
        WHERE c.board_id = ?
        GROUP BY c.id, c.name
        ORDER BY c.position
    """
    return conn.execute(sql, (board_id,)).fetchall()


def tasks_by_priority(conn, board_id, priority):
    """All tasks on a board with a given priority, newest first."""
    sql = """
        SELECT t.id, t.title, t.description, t.priority, t.created_at,
               c.name AS column_name
        FROM tasks t
        JOIN columns c ON c.id = t.column_id
        WHERE c.board_id = ? AND t.priority = ?
        ORDER BY t.created_at DESC, t.id DESC
    """
    return conn.execute(sql, (board_id, priority)).fetchall()
