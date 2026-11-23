"""One-time importer for moving an existing CampusMove SQLite database to MySQL."""

import argparse
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.app.db import get_db, init_db


# Parent tables must be imported before tables holding their foreign keys.
TABLE_ORDER = (
    "users", "vehicles", "drivers", "routes", "private_vehicles", "maintenance",
    "stops", "carpools", "schedules", "transport_requests", "bookings",
    "driver_leaves", "dispatch_requests", "notifications", "seat_allocations",
    "daily_attendance",
)


def import_database(source: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"SQLite database not found: {source}")

    source_db = sqlite3.connect(source)
    source_db.row_factory = sqlite3.Row
    app = create_app("development")

    with app.app_context():
        init_db()
        target_db = get_db()
        cursor = target_db.cursor()
        try:
            for table in TABLE_ORDER:
                exists = source_db.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
                ).fetchone()
                if not exists:
                    continue

                columns = [row["name"] for row in source_db.execute(f"PRAGMA table_info(`{table}`)")]
                rows = source_db.execute(f"SELECT * FROM `{table}`").fetchall()
                if not rows:
                    continue

                column_sql = ", ".join(f"`{column}`" for column in columns)
                placeholders = ", ".join(["%s"] * len(columns))
                statement = f"INSERT IGNORE INTO `{table}` ({column_sql}) VALUES ({placeholders})"
                cursor.executemany(statement, [tuple(row[column] for column in columns) for row in rows])
                print(f"{table}: imported {cursor.rowcount} of {len(rows)} rows")
            target_db.commit()
        except Exception:
            target_db.rollback()
            raise
        finally:
            cursor.close()
            source_db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import CampusMove SQLite data into MySQL.")
    parser.add_argument("--source", type=Path, default=BASE_DIR / "legacysqllitedb")
    args = parser.parse_args()
    import_database(args.source.resolve())
    print("SQLite to MySQL migration completed successfully.")


if __name__ == "__main__":
    main()

