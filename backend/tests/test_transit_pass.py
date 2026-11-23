from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = PROJECT_ROOT / "db" / "schema.sql"


def get_schema():
    return SCHEMA_FILE.read_text(encoding="utf-8").lower()


def test_transport_requests_table_exists():
    schema = get_schema()
    assert "create table if not exists transport_requests" in schema


def test_bookings_table_exists():
    schema = get_schema()
    assert "create table if not exists bookings" in schema


def test_booking_has_student_id():
    schema = get_schema()
    assert "student_id integer not null" in schema


def test_booking_has_status():
    schema = get_schema()
    assert "status varchar(25)" in schema


def test_transport_request_has_priority():
    schema = get_schema()
    assert "priority" in schema