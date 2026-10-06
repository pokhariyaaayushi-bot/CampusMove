"""
ER Diagram Parity Verification Tests
Joint contribution: Aayushi, Sharanya, Pushpesh

Validates that all 11 entities and relationships from the mentor-approved ER diagram
are fully functional in the database schema:
1. Student -> Places -> Transport_request
2. Transport_request -> Generates -> Booking
3. Route -> Contains -> Stops
4. Vehicle -> Specialises at -> Private_vehicle
5. Vehicle -> Undergoes -> Maintenance
6. Student -> Hosts -> Carpool -> Used by -> Route
"""

import pytest
from backend.app.db import execute_query
from backend.app.models.user import UserModel
from backend.app.models.vehicle import VehicleModel
from backend.app.models.driver import DriverModel
from backend.app.models.route import RouteModel
from backend.app.models.schedule import ScheduleModel


def test_er_student_places_transport_request_generates_booking(app):
    """
    Validates ER Relationship:
    Student (places 1:N) -> Transport_request (generates 1:N) -> Booking (fulfills Schedule)
    """
    with app.app_context():
        # 1. Student places request
        student = UserModel.create(name="ER Test Student", email="er.student@geu.ac.in", password="Password123!")
        route = RouteModel.create(route_name="ER Route", origin="Station A", destination="Station B", distance_km=3.0, estimated_duration_mins=12)

        req_id = execute_query(
            "INSERT INTO transport_requests (student_id, route_id, requested_time, priority, purpose) VALUES (?, ?, ?, ?, ?)",
            (student["user_id"], route["route_id"], "09:00:00", "P1", "Emergency Transfer"),
            fetch="insert"
        )
        assert req_id is not None

        # 2. Vehicle & Driver allocated on Schedule
        vehicle = VehicleModel.create(registration_number="ER-AMB-01", model="Ambulance Van", capacity=4)
        driver = DriverModel.create(name="Driver Dev", phone="+91-9988771122", license_number="LIC-ER-01")
        schedule = ScheduleModel.create(
            route_id=route["route_id"],
            vehicle_id=vehicle["vehicle_id"],
            driver_id=driver["driver_id"],
            departure_time="09:00:00",
            arrival_time="09:12:00",
            time_window="Immediate"
        )

        # 3. Transport_request generates Booking
        booking_id = execute_query(
            """INSERT INTO bookings (request_id, student_id, route_id, schedule_id, vehicle_id, seat_no, priority_level, purpose, requested_date, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (req_id, student["user_id"], route["route_id"], schedule["schedule_id"], vehicle["vehicle_id"], 1, "P1", "Emergency Transfer", "2026-09-23", "confirmed"),
            fetch="insert"
        )

        # Update request status to 'allocated'
        execute_query("UPDATE transport_requests SET status = 'allocated' WHERE request_id = ?", (req_id,), fetch="none")

        # Verify joined lookup
        booking_row = execute_query(
            """SELECT b.booking_id, b.request_id, tr.priority, u.name as student_name, r.route_name, s.departure_time, v.model as vehicle_model
               FROM bookings b
               JOIN transport_requests tr ON b.request_id = tr.request_id
               JOIN users u ON b.student_id = u.user_id
               JOIN routes r ON b.route_id = r.route_id
               JOIN schedules s ON b.schedule_id = s.schedule_id
               JOIN vehicles v ON b.vehicle_id = v.vehicle_id
               WHERE b.booking_id = ?""",
            (booking_id,),
            fetch="one"
        )

        assert booking_row["request_id"] == req_id
        assert booking_row["priority"] == "P1"
        assert booking_row["vehicle_model"] == "Ambulance Van"


def test_er_route_contains_stops(app):
    """Validates ER Relationship: Route (contains 1:N) -> Stop"""
    with app.app_context():
        route = RouteModel.create(route_name="Express Line 10", origin="Gate 1", destination="Sports Complex", distance_km=4.2, estimated_duration_mins=16)

        stop1_id = execute_query(
            "INSERT INTO stops (route_id, stop_name, sequence_no) VALUES (?, ?, ?)",
            (route["route_id"], "Administration Block Stop", 1),
            fetch="insert"
        )
        stop2_id = execute_query(
            "INSERT INTO stops (route_id, stop_name, sequence_no) VALUES (?, ?, ?)",
            (route["route_id"], "Computer Science Block Stop", 2),
            fetch="insert"
        )

        stops = execute_query(
            "SELECT * FROM stops WHERE route_id = ? ORDER BY sequence_no ASC",
            (route["route_id"],),
            fetch="all"
        )
        assert len(stops) == 2
        assert stops[0]["sequence_no"] == 1
        assert stops[1]["sequence_no"] == 2


def test_er_vehicle_undergoes_maintenance(app):
    """Validates ER Relationship: Vehicle (undergoes 1:N) -> Maintenance"""
    with app.app_context():
        vehicle = VehicleModel.create(registration_number="ER-MAINT-01", model="Standard Bus", capacity=40)

        maint_id = execute_query(
            "INSERT INTO maintenance (vehicle_id, issue, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
            (vehicle["vehicle_id"], "Clutch replacement", "2026-09-22", "2026-09-24", "in_progress"),
            fetch="insert"
        )

        maint_record = execute_query("SELECT * FROM maintenance WHERE maintenance_id = ?", (maint_id,), fetch="one")
        assert maint_record["issue"] == "Clutch replacement"
        assert maint_record["status"] == "in_progress"


def test_er_private_vehicle_and_carpool_schema(app):
    """Validates ER Entities: Private_vehicle (specialization) and Carpool (hosted by student)"""
    with app.app_context():
        student = UserModel.create(name="Pvt Driver Student", email="pvt.driver@geu.ac.in", password="Password123!")
        route = RouteModel.create(route_name="Carpool Route 1", origin="Subhash Nagar", destination="Campus", distance_km=5.0, estimated_duration_mins=20)

        # Vehicle with owner_type = 'private'
        vehicle = VehicleModel.create(registration_number="UK-07-PVT-999", model="Hyundai i20", capacity=4, owner_type="private")

        # Private vehicle registration
        pvt_id = execute_query(
            "INSERT INTO private_vehicles (student_id, vehicle_id, available_seats) VALUES (?, ?, ?)",
            (student["user_id"], vehicle["vehicle_id"], 3),
            fetch="insert"
        )
        assert pvt_id is not None

        # Carpool hosting
        carpool_id = execute_query(
            "INSERT INTO carpools (driver_student_id, route_id, capacity, departure_time) VALUES (?, ?, ?, ?)",
            (student["user_id"], route["route_id"], 3, "08:15:00"),
            fetch="insert"
        )
        assert carpool_id is not None

        carpool = execute_query("SELECT * FROM carpools WHERE carpool_id = ?", (carpool_id,), fetch="one")
        assert carpool["driver_student_id"] == student["user_id"]
        assert carpool["capacity"] == 3
