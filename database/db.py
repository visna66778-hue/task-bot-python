import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Путь к базе данных
DB_PATH = Path(__file__).resolve().parent.parent / "tasks.db"


def get_connection():
    """Создаёт соединение с базой данных."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Создаёт таблицу и добавляет новые колонки при необходимости."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                "user" TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Новая',
                category TEXT NOT NULL DEFAULT 'Общее'
            )
        """)

        # Проверяем существующие колонки, чтобы не затронуть старые задачи
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tasks)"
            ).fetchall()
        }

        if "status" not in columns:
            connection.execute("""
                ALTER TABLE tasks
                ADD COLUMN status TEXT NOT NULL DEFAULT 'Новая'
            """)

        if "category" not in columns:
            connection.execute("""
                ALTER TABLE tasks
                ADD COLUMN category TEXT NOT NULL DEFAULT 'Общее'
            """)


def add_task(
    text: str,
    username: str,
    category: str = "Общее",
    status: str = "Новая",
):
    """Сохраняет задачу с категорией и статусом."""
    created_at = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tasks
                (text, "user", created_at, status, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, username, created_at, status, category),
        )


def get_all_tasks():
    """Возвращает все задачи вместе с категорией и статусом."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, text, "user", created_at, status, category
            FROM tasks
            ORDER BY id
        """).fetchall()

        return [dict(row) for row in rows]
        
def update_task_status(task_id: int, status: str) -> bool:
    """Изменяет статус задачи по её ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id),
        )
        return cursor.rowcount > 0
