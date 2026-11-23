
"""
Tests for dispatch priority, driver availability,
and database integrity.

Note: Dedicated driver shift and privacy features are not
currently confirmed in the project implementation.
"""

import pytest

from backend.app.algorithms.priority_scheduler import (
    rank_booking_requests,
    select_next_request,
    PRIORITY_WEIGHTS,
)
from backend.app.models.driver import (
    DriverModel,
    VALID_DRIVER_AVAILABILITY,
)


# --------------------------------------------------
# DISPATCH PRIORITY TESTS
# --------------------------------------------------

def test_priority_weights_are_correct():
    assert PRIORITY_WEIGHTS == {
        "P1": 1,
        "P2": 2,
        "P3": 3,
    }


def test_emergency_requests_get_highest_priority():
    requests = [
        {"request_id": 1, "priority_level": "P3", "created_at": "2026-01-01"},
        {"request_id": 2, "priority_level": "P1", "created_at": "2026-01-02"},
        {"request_id": 3, "priority_level": "P2", "created_at": "2026-01-03"},
    ]

    ranked = rank_booking_requests(requests)

    assert [r["priority_level"] for r in ranked] == [
        "P1", "P2", "P3"
    ]


def test_same_priority_uses_creation_time():
    requests = [
        {"request_id": 1, "priority_level": "P2", "created_at": "2026-01-03"},
        {"request_id": 2, "priority_level": "P2", "created_at": "2026-01-01"},
        {"request_id": 3, "priority_level": "P2", "created_at": "2026-01-02"},
    ]

    ranked = rank_booking_requests(requests)

    assert [r["request_id"] for r in ranked] == [2, 3, 1]


def test_empty_request_list_returns_empty_list():
    assert rank_booking_requests([]) == []


def test_unknown_priority_is_ranked_after_valid_priorities():
    requests = [
        {"request_id": 1, "priority_level": "P3", "created_at": "2026-01-01"},
        {"request_id": 2, "priority_level": "UNKNOWN", "created_at": "2026-01-01"},
        {"request_id": 3, "priority_level": "P1", "created_at": "2026-01-01"},
    ]

    ranked = rank_booking_requests(requests)

    assert [r["request_id"] for r in ranked] == [3, 1, 2]


def test_missing_priority_defaults_to_p3():
    requests = [
        {"request_id": 1, "created_at": "2026-01-01"},
        {"request_id": 2, "priority_level": "P1", "created_at": "2026-01-02"},
    ]

    ranked = rank_booking_requests(requests)

    assert [r["request_id"] for r in ranked] == [2, 1]


def test_select_next_request_returns_highest_priority():
    requests = [
        {"request_id": 1, "priority_level": "P3", "created_at": "2026-01-01"},
        {"request_id": 2, "priority_level": "P1", "created_at": "2026-01-02"},
    ]

    selected = select_next_request(requests)

    assert selected["request_id"] == 2


def test_select_next_request_returns_none_for_empty_list():
    assert select_next_request([]) is None


# --------------------------------------------------
# DRIVER AVAILABILITY TESTS
# --------------------------------------------------

def test_valid_driver_availability_statuses():
    assert VALID_DRIVER_AVAILABILITY == {
        "available",
        "on_trip",
        "off_duty",
    }


@pytest.mark.parametrize(
    "availability",
    ["available", "on_trip", "off_duty"],
)
def test_driver_accepts_valid_availability(availability):
    DriverModel.validate_attributes(availability)


def test_driver_rejects_invalid_availability():
    with pytest.raises(ValueError):
        DriverModel.validate_attributes("busy")


def test_driver_rejects_empty_availability():
    with pytest.raises(ValueError):
        DriverModel.validate_attributes("")


# --------------------------------------------------
# DATABASE INTEGRITY / PRIVACY-RELATED SAFETY
# --------------------------------------------------

def test_database_foreign_keys_are_enabled(app):
    with app.app_context():
        from backend.app.db import get_db

        result = get_db().execute(
            "PRAGMA foreign_keys"
        ).fetchone()

        assert result[0] == 1


def test_driver_creation_rejects_missing_name():
    with pytest.raises(ValueError):
        DriverModel.create(
            name="",
            phone="9999999999",
            license_number="TEST123"
        )


def test_driver_creation_rejects_missing_phone():
    with pytest.raises(ValueError):
        DriverModel.create(
            name="Test Driver",
            phone="",
            license_number="TEST123"
        )


def test_driver_creation_rejects_missing_license():
    with pytest.raises(ValueError):
        DriverModel.create(
            name="Test Driver",
            phone="9999999999",
            license_number=""
        )