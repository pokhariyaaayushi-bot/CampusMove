"""
Pytest Test Fixtures and Application Setup
"""

import os
import pytest
from pathlib import Path
from backend.app import create_app
from backend.app.db import init_db, seed_db, close_db, get_db

TEST_DB_FILE = Path(__file__).resolve().parent.parent.parent / "test_campusmove.db"


@pytest.fixture
def app():
    """Creates a fresh test Flask application with an isolated test SQLite database."""
    # Ensure any previous test database file is removed
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except OSError:
            pass

    app = create_app("testing")
    app.config["SQLITE_DB_PATH"] = str(TEST_DB_FILE)

    with app.app_context():
        init_db()
        yield app
        close_db()

    # Clean up test database file
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except OSError:
            pass


@pytest.fixture
def client(app):
    """Provides a test client for simulating HTTP requests."""
    return app.test_client()


@pytest.fixture
def seeded_app():
    """Provides an app initialized with full seed dataset."""
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except OSError:
            pass

    app = create_app("testing")
    app.config["SQLITE_DB_PATH"] = str(TEST_DB_FILE)

    with app.app_context():
        init_db()
        seed_db()
        yield app
        close_db()

    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except OSError:
            pass


@pytest.fixture
def seeded_client(seeded_app):
    return seeded_app.test_client()

