"""
Ride & Transport Request Cancellation Tests
Tests cancellation transitions, seat release, and cascade consistency.
"""

import pytest
from backend.app.models.user import UserModel
from backend.app.models.route import RouteModel
from backend.app.models.vehicle import VehicleModel
from backend.app.models.driver import DriverModel
from backend.app.models.schedule import ScheduleModel
from backend.app.models.booking import BookingModel
from backend.app.db import execute_query


def test_cancel_booking_via_api(client, app):
    """Verifies that POST /api/bookings/<id>/cancel transitions booking status to 'cancelled'."""
    with app.app_context():
        student = UserModel.create(name="Cancel Test Student", email="cancel.test@geu.ac.in", password="Password123!")
        route = RouteModel.create(route_name="Cancel Test Route", origin="Turner Road", destination="Clement Town", distance_km=3.2, estimated_duration_mins=12)

        booking = BookingModel.create(
            student_id=student["user_id"],
            route_id=route["route_id"],
            purpose="Daily Commute",
            requested_date="2026-09-23",
            seat_no=7,
            status="confirmed"
        )
        booking_id = booking["booking_id"]

    # Cancel via API
    res = client.post(f"/api/bookings/{booking_id}/cancel")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["status"] == "cancelled"

    # Verify directly from database
    with app.app_context():
        db_booking = BookingModel.get_by_id(booking_id)
        assert db_booking["status"] == "cancelled"


def test_cancel_booking_cascades_to_transport_request(client, app):
    """Verifies that cancelling a booking cascades status = 'cancelled' to the parent transport request."""
    with app.app_context():
        student = UserModel.create(name="Cascade Student", email="cascade@geu.ac.in", password="Password123!")
        route = RouteModel.create(route_name="Cascade Route", origin="Clock Tower", destination="Clement Town", distance_km=8.5, estimated_duration_mins=28)

        # Create request
        req_id = execute_query(
            "INSERT INTO transport_requests (student_id, route_id, requested_time, priority, purpose, status) VALUES (?, ?, ?, ?, ?, 'allocated')",
            (student["user_id"], route["route_id"], "08:00:00", "P2", "Official Duty"),
            fetch="insert"
        )

        # Create linked booking
        booking = BookingModel.create(
            student_id=student["user_id"],
            route_id=route["route_id"],
            request_id=req_id,
            purpose="Official Duty",
            requested_date="2026-09-23",
            seat_no=3,
            status="confirmed"
        )
        booking_id = booking["booking_id"]

    # Cancel booking
    res = client.post(f"/api/bookings/{booking_id}/cancel")
    assert res.status_code == 200

    # Verify request is also marked cancelled
    with app.app_context():
        req = execute_query("SELECT * FROM transport_requests WHERE request_id = ?", (req_id,), fetch="one")
        assert req["status"] == "cancelled"


def test_cancel_transport_request_removes_from_priority_queue(client, app):
    """Verifies that cancelling a pending transport request removes it from the OS priority scheduling queue."""
    with app.app_context():
        student = UserModel.create(name="Queue Student", email="queue.cancel@geu.ac.in", password="Password123!")
        route = RouteModel.create(route_name="Queue Route", origin="Subhash Nagar", destination="GEHU Hill", distance_km=4.5, estimated_duration_mins=20)

        req_id = execute_query(
            "INSERT INTO transport_requests (student_id, route_id, requested_time, priority, purpose, status) VALUES (?, ?, ?, ?, ?, 'pending')",
            (student["user_id"], route["route_id"], "09:00:00", "P1", "Lab Exam Commute"),
            fetch="insert"
        )

    # Verify present in priority queue
    q_res = client.get("/api/algorithms/priority-queue")
    assert q_res.status_code == 200
    queue_ids = [r["request_id"] for r in q_res.get_json()["data"]["queue"]]
    assert req_id in queue_ids

    # Cancel request via API
    cancel_res = client.post(f"/api/requests/{req_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["data"]["status"] == "cancelled"

    # Verify removed from priority queue
    q_res2 = client.get("/api/algorithms/priority-queue")
    queue_ids2 = [r["request_id"] for r in q_res2.get_json()["data"]["queue"]]
    assert req_id not in queue_ids2

