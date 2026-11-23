from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = PROJECT_ROOT / "db" / "schema.sql"


def get_schema():
    return SCHEMA_FILE.read_text(encoding="utf-8").lower()


def test_vehicle_table_has_available_seats():
    schema = get_schema()
    assert "available_seats" in schema


def test_available_seats_cannot_be_negative():
    schema = get_schema()
    assert "check (available_seats >= 0)" in schema


def test_booking_table_has_seat_number():
    schema = get_schema()
    assert "seat_no" in schema


def test_booking_table_exists():
    schema = get_schema()
    assert "create table if not exists bookings" in schema


def test_seat_tier_feature_is_not_assumed_to_exist():
    schema = get_schema()
    assert "create table" in schema