"""
Provides a lightweight, shared database abstraction layer for raw SQL execution,
parameterized queries, explicit transaction management, and dual SQLite/MySQL support.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from flask import g, current_app

from backend.app.config import Config, DevelopmentConfig

try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False


def _dict_factory(cursor, row):
    """Factory to return SQLite rows as standard dictionaries."""
    fields = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_db(custom_config=None):
    """
    Retrieves or creates a database connection for the current application context.
    Ensures foreign keys are strictly enforced in SQLite.
    """
    if "db" not in g:
        cfg = custom_config
        if cfg is None:
            if current_app:
                cfg = current_app.config
            else:
                cfg = DevelopmentConfig

        db_type = cfg.get("DB_TYPE", "sqlite") if isinstance(cfg, dict) else getattr(cfg, "DB_TYPE", "sqlite")

        if db_type == "mysql" and HAS_PYMYSQL:
            host = cfg.get("MYSQL_HOST") if isinstance(cfg, dict) else getattr(cfg, "MYSQL_HOST", "localhost")
            port = cfg.get("MYSQL_PORT") if isinstance(cfg, dict) else getattr(cfg, "MYSQL_PORT", 3306)
            user = cfg.get("MYSQL_USER") if isinstance(cfg, dict) else getattr(cfg, "MYSQL_USER", "root")
            password = cfg.get("MYSQL_PASSWORD") if isinstance(cfg, dict) else getattr(cfg, "MYSQL_PASSWORD", "")
            db_name = cfg.get("MYSQL_DB") if isinstance(cfg, dict) else getattr(cfg, "MYSQL_DB", "campusmove")

            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            g.db = conn
            g.db_type = "mysql"
        else:
            db_path = cfg.get("SQLITE_DB_PATH") if isinstance(cfg, dict) else getattr(cfg, "SQLITE_DB_PATH", "campusmove.db")
            conn = sqlite3.connect(db_path)
            conn.row_factory = _dict_factory
            # Critical DBMS integrity requirement: enforce foreign keys in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            g.db = conn
            g.db_type = "sqlite"

    return g.db


def close_db(e=None):
    """Closes the current database connection if open."""
    db = g.pop("db", None)
    g.pop("db_type", None)
    if db is not None:
        db.close()


def _adapt_sql(sql: str, db_type: str) -> str:
    """
    Translates parameter placeholders between SQLite ('?') and MySQL ('%s')
    to ensure SQL statements remain portable across both engines.
    """
    if db_type == "mysql":
        # SQLite's two-argument MAX is a scalar function. MySQL's MAX is an
        # aggregate, so use its scalar equivalent for seat calculations.
        return sql.replace("?", "%s").replace("MAX(0,", "GREATEST(0,")
    else:
        return sql.replace("%s", "?")


def _adapt_schema_sql(sql: str, db_type: str) -> str:
    """Keep the canonical schema MySQL-first while allowing SQLite test runs."""
    if db_type == "sqlite":
        return (
            sql.replace("INTEGER AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            .replace("INSERT IGNORE", "INSERT OR IGNORE")
        )
    # MySQL supports IF NOT EXISTS for tables but not indexes. Duplicate-index
    # errors are handled explicitly by init_db below.
    return sql.replace("CREATE INDEX IF NOT EXISTS", "CREATE INDEX")


def _sql_statements(sql: str):
    """Return executable statements from our schema/seed files.

    MySQL execution is statement-by-statement. Remove full-line SQL comments
    first, because comments may contain a semicolon that must not be treated
    as a statement boundary.
    """
    uncommented = "\n".join(
        line for line in sql.splitlines() if not line.lstrip().startswith("--")
    )
    return (statement.strip() for statement in uncommented.split(";") if statement.strip())


def execute_query(sql: str, params=None, fetch: str = "all", db_conn=None):
    """
    Executes a parameterized SQL query safely against SQLite or MySQL.

    Parameters:
        sql (str): SQL statement with '?' or '%s' placeholders.
        params (tuple/list): Query parameters to prevent SQL injection.
        fetch (str): 'all' (return all rows), 'one' (single row), 'none' (for updates),
                     or 'insert' (returns last inserted row ID).
        db_conn: Optional existing connection (for active transactions).

    Returns:
        list[dict], dict, int, or None based on fetch mode.
    """
    conn = db_conn if db_conn is not None else get_db()
    db_type = getattr(g, "db_type", "sqlite")
    if db_conn is not None and hasattr(db_conn, "row_factory"):
        db_type = "sqlite"
    elif db_conn is not None and hasattr(db_conn, "cursorclass"):
        db_type = "mysql"

    adapted_sql = _adapt_sql(sql, db_type)
    query_params = params if params is not None else ()

    cursor = conn.cursor()
    try:
        cursor.execute(adapted_sql, query_params)

        if fetch == "all":
            return cursor.fetchall()
        elif fetch == "one":
            return cursor.fetchone()
        elif fetch == "insert":
            if db_conn is None:
                conn.commit()
            return cursor.lastrowid
        elif fetch == "none":
            if db_conn is None:
                conn.commit()
            return cursor.rowcount
        else:
            raise ValueError(f"Unsupported fetch type: {fetch}")
    finally:
        cursor.close()


@contextmanager
def transaction(db_conn=None):
    """
    Context manager for atomic transaction management (ACID properties).
    Automatically commits on success or issues a rollback on exception.
    """
    conn = db_conn if db_conn is not None else get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db(schema_path: str = None, db_conn=None):
    """Executes the master 3NF DDL schema file to initialize all tables and constraints."""
    if schema_path is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        schema_path = str(base_dir / "db" / "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = db_conn if db_conn is not None else get_db()
    db_type = getattr(g, "db_type", "sqlite")
    schema_sql = _adapt_schema_sql(schema_sql, db_type)
    if db_type == "sqlite" or hasattr(conn, "row_factory"):
        conn.executescript(schema_sql)
        conn.commit()
    else:
        cursor = conn.cursor()
        for stmt in _sql_statements(schema_sql):
            try:
                cursor.execute(stmt)
            except Exception as exc:
                # MySQL error 1061 is a duplicate index on subsequent
                # application starts; the schema is otherwise unchanged.
                if getattr(exc, "args", [None])[0] != 1061:
                    raise
        # Tables created by older CampusMove releases predate these columns.
        # MySQL does not support ADD COLUMN IF NOT EXISTS, so ignore its
        # duplicate-column error (1060) while applying the small upgrades.
        for statement in (
            "ALTER TABLE schedules ADD COLUMN direction VARCHAR(10) NOT NULL DEFAULT 'inbound'",
            "ALTER TABLE notifications ADD COLUMN route_id INTEGER",
        ):
            try:
                cursor.execute(statement)
            except Exception as exc:
                if getattr(exc, "args", [None])[0] != 1060:
                    raise
        conn.commit()
        cursor.close()


def seed_db(seed_path: str = None, db_conn=None):
    """Executes the seed dataset file to populate sample testing data."""
    if seed_path is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        seed_path = str(base_dir / "db" / "seed.sql")

    with open(seed_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    conn = db_conn if db_conn is not None else get_db()
    db_type = getattr(g, "db_type", "sqlite")
    seed_sql = _adapt_schema_sql(seed_sql, db_type)
    if db_type == "sqlite" or hasattr(conn, "row_factory"):
        conn.executescript(seed_sql)
        conn.commit()
    else:
        cursor = conn.cursor()
        for stmt in _sql_statements(seed_sql):
            cursor.execute(stmt)
        conn.commit()
        cursor.close()
