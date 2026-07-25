from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Generator


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "homeguardian.db"


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Create and safely close a SQLite connection."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database() -> None:
    """Create the database tables and apply missing columns."""

    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS appliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance_name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT NOT NULL,
                model_number TEXT NOT NULL,
                serial_number TEXT,
                purchase_date TEXT,
                warranty_expiry TEXT,
                location TEXT,
                notes TEXT,
                manual_filename TEXT,
                manual_path TEXT,
                manual_processed INTEGER NOT NULL DEFAULT 0,
                manual_chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS maintenance_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                description TEXT,
                frequency_days INTEGER,
                last_completed_date TEXT,
                next_due_date TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (appliance_id)
                    REFERENCES appliances(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS repair_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appliance_id INTEGER NOT NULL,
                repair_date TEXT NOT NULL,
                problem_description TEXT NOT NULL,
                solution TEXT,
                technician_name TEXT,
                repair_cost REAL,
                replaced_parts TEXT,
                repair_warranty_expiry TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (appliance_id)
                    REFERENCES appliances(id)
                    ON DELETE CASCADE
            );
            """
        )

        appliance_columns = connection.execute(
            "PRAGMA table_info(appliances)"
        ).fetchall()

        existing_columns = {
            column["name"]
            for column in appliance_columns
        }

        if "manual_processed" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE appliances
                ADD COLUMN manual_processed
                INTEGER NOT NULL DEFAULT 0
                """
            )

        if "manual_chunk_count" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE appliances
                ADD COLUMN manual_chunk_count
                INTEGER NOT NULL DEFAULT 0
                """
            )


def add_appliance(
    appliance_name: str,
    category: str,
    brand: str,
    model_number: str,
    serial_number: str | None = None,
    purchase_date: date | None = None,
    warranty_expiry: date | None = None,
    location: str | None = None,
    notes: str | None = None,
    manual_filename: str | None = None,
    manual_path: str | None = None,
) -> int:
    """Add a new appliance and return its database ID."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appliances (
                appliance_name,
                category,
                brand,
                model_number,
                serial_number,
                purchase_date,
                warranty_expiry,
                location,
                notes,
                manual_filename,
                manual_path,
                manual_processed,
                manual_chunk_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            """,
            (
                appliance_name.strip(),
                category.strip(),
                brand.strip(),
                model_number.strip(),
                serial_number.strip() if serial_number else None,
                purchase_date.isoformat() if purchase_date else None,
                warranty_expiry.isoformat() if warranty_expiry else None,
                location.strip() if location else None,
                notes.strip() if notes else None,
                manual_filename,
                manual_path,
            ),
        )

        return int(cursor.lastrowid)


def get_all_appliances() -> list[dict]:
    """Return all saved appliances."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                appliance_name,
                category,
                brand,
                model_number,
                serial_number,
                purchase_date,
                warranty_expiry,
                location,
                notes,
                manual_filename,
                manual_path,
                manual_processed,
                manual_chunk_count,
                created_at,
                updated_at
            FROM appliances
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_appliance_by_id(appliance_id: int) -> dict | None:
    """Return one appliance using its ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM appliances
            WHERE id = ?
            """,
            (appliance_id,),
        ).fetchone()

    return dict(row) if row else None


def get_appliances_with_manuals() -> list[dict]:
    """Return appliances that have uploaded manuals."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                appliance_name,
                category,
                brand,
                model_number,
                manual_filename,
                manual_path,
                manual_processed,
                manual_chunk_count
            FROM appliances
            WHERE manual_path IS NOT NULL
              AND TRIM(manual_path) != ''
            ORDER BY appliance_name ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def update_manual_processing_status(
    appliance_id: int,
    processed: bool,
    chunk_count: int = 0,
) -> None:
    """Update the manual-processing status of an appliance."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE appliances
            SET
                manual_processed = ?,
                manual_chunk_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                1 if processed else 0,
                max(chunk_count, 0),
                appliance_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No appliance was found with ID {appliance_id}."
            )


def delete_appliance(appliance_id: int) -> None:
    """Delete one appliance and all linked records."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM appliances
            WHERE id = ?
            """,
            (appliance_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No appliance was found with ID {appliance_id}."
            )


def get_dashboard_statistics() -> dict:
    """Return statistics used by the dashboard."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_appliances,

                SUM(
                    CASE
                        WHEN manual_path IS NOT NULL
                             AND TRIM(manual_path) != ''
                        THEN 1
                        ELSE 0
                    END
                ) AS appliances_with_manuals,

                SUM(
                    CASE
                        WHEN manual_path IS NULL
                             OR TRIM(manual_path) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS appliances_without_manuals,

                SUM(
                    CASE
                        WHEN warranty_expiry IS NOT NULL
                             AND DATE(warranty_expiry) >= DATE('now')
                        THEN 1
                        ELSE 0
                    END
                ) AS active_warranties,

                SUM(
                    CASE
                        WHEN manual_processed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS processed_manuals
            FROM appliances
            """
        ).fetchone()

    return {
        "total_appliances": row["total_appliances"] or 0,
        "appliances_with_manuals": row["appliances_with_manuals"] or 0,
        "appliances_without_manuals": (
            row["appliances_without_manuals"] or 0
        ),
        "active_warranties": row["active_warranties"] or 0,
        "processed_manuals": row["processed_manuals"] or 0,
    }


def get_category_statistics() -> list[dict]:
    """Return the number of appliances in every category."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                category,
                COUNT(*) AS appliance_count
            FROM appliances
            GROUP BY category
            ORDER BY appliance_count DESC, category ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_recent_appliances(limit: int = 5) -> list[dict]:
    """Return recently added appliances."""

    if limit <= 0:
        return []

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                appliance_name,
                category,
                brand,
                model_number,
                location,
                warranty_expiry,
                manual_filename,
                manual_processed,
                manual_chunk_count,
                created_at
            FROM appliances
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]



def add_maintenance_task(
    appliance_id: int,
    task_name: str,
    description: str | None = None,
    frequency_days: int | None = None,
    last_completed_date: date | None = None,
    next_due_date: date | None = None,
    status: str = "Pending",
) -> int:
    """Add a maintenance task and return its ID."""

    cleaned_task_name = task_name.strip()

    if not cleaned_task_name:
        raise ValueError("Task name cannot be empty.")

    allowed_statuses = {
        "Pending",
        "Overdue",
        "Completed",
    }

    if status not in allowed_statuses:
        status = "Pending"

    with get_connection() as connection:
        appliance_exists = connection.execute(
            """
            SELECT id
            FROM appliances
            WHERE id = ?
            """,
            (appliance_id,),
        ).fetchone()

        if appliance_exists is None:
            raise ValueError(
                f"No appliance was found with ID {appliance_id}."
            )

        cursor = connection.execute(
            """
            INSERT INTO maintenance_tasks (
                appliance_id,
                task_name,
                description,
                frequency_days,
                last_completed_date,
                next_due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appliance_id,
                cleaned_task_name,
                description.strip() if description else None,
                frequency_days if frequency_days else None,
                (
                    last_completed_date.isoformat()
                    if last_completed_date
                    else None
                ),
                (
                    next_due_date.isoformat()
                    if next_due_date
                    else None
                ),
                status,
            ),
        )

        return int(cursor.lastrowid)


def get_maintenance_tasks(
    appliance_id: int | None = None,
) -> list[dict]:
    """Return maintenance tasks with appliance information."""

    query = """
        SELECT
            maintenance_tasks.id,
            maintenance_tasks.appliance_id,
            appliances.appliance_name,
            appliances.category,
            appliances.brand,
            appliances.model_number,
            maintenance_tasks.task_name,
            maintenance_tasks.description,
            maintenance_tasks.frequency_days,
            maintenance_tasks.last_completed_date,
            maintenance_tasks.next_due_date,

            CASE
                WHEN maintenance_tasks.status != 'Completed'
                     AND maintenance_tasks.next_due_date IS NOT NULL
                     AND DATE(maintenance_tasks.next_due_date) < DATE('now')
                THEN 'Overdue'
                ELSE maintenance_tasks.status
            END AS status,

            maintenance_tasks.created_at

        FROM maintenance_tasks

        INNER JOIN appliances
            ON appliances.id = maintenance_tasks.appliance_id
    """

    parameters: tuple = ()

    if appliance_id is not None:
        query += """
            WHERE maintenance_tasks.appliance_id = ?
        """

        parameters = (appliance_id,)

    query += """
        ORDER BY
            CASE
                WHEN maintenance_tasks.status != 'Completed'
                     AND maintenance_tasks.next_due_date IS NOT NULL
                     AND DATE(maintenance_tasks.next_due_date) < DATE('now')
                THEN 0
                WHEN maintenance_tasks.status = 'Pending'
                THEN 1
                ELSE 2
            END,
            maintenance_tasks.next_due_date ASC,
            maintenance_tasks.id DESC
    """

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [dict(row) for row in rows]


def get_maintenance_task_by_id(
    task_id: int,
) -> dict | None:
    """Return one maintenance task."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM maintenance_tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    return dict(row) if row else None


def complete_maintenance_task(
    task_id: int,
    completed_date: date,
) -> None:
    """
    Mark a task as completed.

    Recurring tasks receive a new next-due date and return to Pending.
    One-time tasks remain Completed.
    """

    from datetime import timedelta

    task = get_maintenance_task_by_id(task_id)

    if task is None:
        raise ValueError(
            f"No maintenance task was found with ID {task_id}."
        )

    frequency_days = task.get("frequency_days")

    if frequency_days and int(frequency_days) > 0:
        next_due = completed_date + timedelta(
            days=int(frequency_days)
        )

        new_status = "Pending"

    else:
        next_due = None
        new_status = "Completed"

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE maintenance_tasks
            SET
                last_completed_date = ?,
                next_due_date = ?,
                status = ?
            WHERE id = ?
            """,
            (
                completed_date.isoformat(),
                next_due.isoformat() if next_due else None,
                new_status,
                task_id,
            ),
        )


def update_maintenance_task_status(
    task_id: int,
    status: str,
) -> None:
    """Update the status of a maintenance task."""

    allowed_statuses = {
        "Pending",
        "Overdue",
        "Completed",
    }

    if status not in allowed_statuses:
        raise ValueError(
            "Status must be Pending, Overdue, or Completed."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE maintenance_tasks
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                task_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No maintenance task was found with ID {task_id}."
            )


def delete_maintenance_task(
    task_id: int,
) -> None:
    """Delete a maintenance task."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM maintenance_tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No maintenance task was found with ID {task_id}."
            )


def get_maintenance_statistics(
    appliance_id: int | None = None,
) -> dict:
    """Return maintenance statistics."""

    query = """
        SELECT
            COUNT(*) AS total_tasks,

            SUM(
                CASE
                    WHEN status = 'Pending'
                         AND (
                            next_due_date IS NULL
                            OR DATE(next_due_date) >= DATE('now')
                         )
                    THEN 1
                    ELSE 0
                END
            ) AS pending_tasks,

            SUM(
                CASE
                    WHEN status != 'Completed'
                         AND next_due_date IS NOT NULL
                         AND DATE(next_due_date) < DATE('now')
                    THEN 1
                    ELSE 0
                END
            ) AS overdue_tasks,

            SUM(
                CASE
                    WHEN status = 'Completed'
                    THEN 1
                    ELSE 0
                END
            ) AS completed_tasks

        FROM maintenance_tasks
    """

    parameters: tuple = ()

    if appliance_id is not None:
        query += """
            WHERE appliance_id = ?
        """

        parameters = (appliance_id,)

    with get_connection() as connection:
        row = connection.execute(
            query,
            parameters,
        ).fetchone()

    return {
        "total_tasks": row["total_tasks"] or 0,
        "pending_tasks": row["pending_tasks"] or 0,
        "overdue_tasks": row["overdue_tasks"] or 0,
        "completed_tasks": row["completed_tasks"] or 0,
    }


def add_repair_record(
    appliance_id: int,
    repair_date: date,
    problem_description: str,
    solution: str | None = None,
    technician_name: str | None = None,
    repair_cost: float | None = None,
    replaced_parts: str | None = None,
    repair_warranty_expiry: date | None = None,
    notes: str | None = None,
) -> int:
    """Add a repair record and return its ID."""

    cleaned_problem = problem_description.strip()

    if not cleaned_problem:
        raise ValueError(
            "Problem description cannot be empty."
        )

    if repair_cost is not None and repair_cost < 0:
        raise ValueError(
            "Repair cost cannot be negative."
        )

    with get_connection() as connection:
        appliance_exists = connection.execute(
            """
            SELECT id
            FROM appliances
            WHERE id = ?
            """,
            (appliance_id,),
        ).fetchone()

        if appliance_exists is None:
            raise ValueError(
                f"No appliance was found with ID {appliance_id}."
            )

        cursor = connection.execute(
            """
            INSERT INTO repair_records (
                appliance_id,
                repair_date,
                problem_description,
                solution,
                technician_name,
                repair_cost,
                replaced_parts,
                repair_warranty_expiry,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appliance_id,
                repair_date.isoformat(),
                cleaned_problem,
                solution.strip() if solution else None,
                (
                    technician_name.strip()
                    if technician_name
                    else None
                ),
                repair_cost,
                (
                    replaced_parts.strip()
                    if replaced_parts
                    else None
                ),
                (
                    repair_warranty_expiry.isoformat()
                    if repair_warranty_expiry
                    else None
                ),
                notes.strip() if notes else None,
            ),
        )

        return int(cursor.lastrowid)


def get_repair_records(
    appliance_id: int | None = None,
) -> list[dict]:
    """Return repair records with appliance information."""

    query = """
        SELECT
            repair_records.id,
            repair_records.appliance_id,
            appliances.appliance_name,
            appliances.category,
            appliances.brand,
            appliances.model_number,
            repair_records.repair_date,
            repair_records.problem_description,
            repair_records.solution,
            repair_records.technician_name,
            repair_records.repair_cost,
            repair_records.replaced_parts,
            repair_records.repair_warranty_expiry,
            repair_records.notes,
            repair_records.created_at

        FROM repair_records

        INNER JOIN appliances
            ON appliances.id = repair_records.appliance_id
    """

    parameters: tuple = ()

    if appliance_id is not None:
        query += """
            WHERE repair_records.appliance_id = ?
        """

        parameters = (appliance_id,)

    query += """
        ORDER BY
            repair_records.repair_date DESC,
            repair_records.id DESC
    """

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [dict(row) for row in rows]


def delete_repair_record(
    repair_id: int,
) -> None:
    """Delete a repair record."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM repair_records
            WHERE id = ?
            """,
            (repair_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"No repair record was found with ID {repair_id}."
            )


def get_repair_statistics(
    appliance_id: int | None = None,
) -> dict:
    """Return repair-history statistics."""

    query = """
        SELECT
            COUNT(*) AS total_repairs,
            COALESCE(SUM(repair_cost), 0) AS total_cost,
            COALESCE(AVG(repair_cost), 0) AS average_cost,
            MAX(repair_date) AS last_repair_date
        FROM repair_records
    """

    parameters: tuple = ()

    if appliance_id is not None:
        query += """
            WHERE appliance_id = ?
        """

        parameters = (appliance_id,)

    with get_connection() as connection:
        row = connection.execute(
            query,
            parameters,
        ).fetchone()

    return {
        "total_repairs": row["total_repairs"] or 0,
        "total_cost": float(row["total_cost"] or 0),
        "average_cost": float(row["average_cost"] or 0),
        "last_repair_date": row["last_repair_date"],
    }