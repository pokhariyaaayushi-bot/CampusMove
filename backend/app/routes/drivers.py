"""
Driver REST CRUD Endpoints
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)
"""

from flask import Blueprint, request
from backend.app.db import execute_query
from backend.app.models.driver import DriverModel
from backend.app.utils.response import api_response, api_error

drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/drivers")


@drivers_bp.route("", methods=["GET"])
def get_drivers():
    """Lists drivers with optional availability filter."""
    availability = request.args.get("availability_status")
    drivers = DriverModel.list_all(availability_status=availability)
    return api_response(data=drivers, message="Drivers retrieved successfully")


@drivers_bp.route("/standby", methods=["GET"])
def get_standby_drivers():
    """Lists unassigned standby drivers who are NOT driving any route/path."""
    query = """
        SELECT d.*
        FROM drivers d
        WHERE d.availability_status = 'available'
          AND d.driver_id NOT IN (
              SELECT DISTINCT driver_id FROM schedules WHERE status != 'cancelled'
          )
        ORDER BY d.name ASC
    """
    standby = execute_query(query, fetch="all") or []
    return api_response(data=standby, message="Standby unassigned drivers retrieved successfully")


@drivers_bp.route("/<int:driver_id>", methods=["GET"])
def get_driver(driver_id: int):
    """Retrieves a single driver by ID."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message=f"Driver with ID {driver_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=driver, message="Driver retrieved successfully")


@drivers_bp.route("", methods=["POST"])
def create_driver():
    """
    Creates a new driver record.
    Vehicle assignment is OPTIONAL (drivers can be kept free on reserve).
    If a vehicle is assigned, it MUST exist beforehand in the database.
    """
    data = request.get_json() or {}
    required = ["name", "phone", "license_number"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    # Validate that if vehicle is provided, it must exist beforehand
    vehicle_id = data.get("vehicle_id")
    vehicle_reg = data.get("vehicle_reg")
    if vehicle_id:
        existing_veh = execute_query(
            "SELECT vehicle_id, model, registration_number, capacity FROM vehicles WHERE vehicle_id = ?",
            (vehicle_id,),
            fetch="one"
        )
        if not existing_veh:
            return api_error(
                message=f"Vehicle with ID {vehicle_id} does not exist. The assigned vehicle must exist in the fleet database beforehand.",
                error_code="VALIDATION_ERROR",
                status_code=400
            )
    elif vehicle_reg and str(vehicle_reg).strip():
        reg_clean = str(vehicle_reg).strip().upper()
        existing_veh = execute_query(
            "SELECT vehicle_id, model, registration_number, capacity FROM vehicles WHERE UPPER(registration_number) = ? OR UPPER(registration_no) = ?",
            (reg_clean, reg_clean),
            fetch="one"
        )
        if not existing_veh:
            return api_error(
                message=f"Vehicle with registration number '{vehicle_reg}' does not exist. The assigned vehicle must exist in the fleet database beforehand.",
                error_code="VALIDATION_ERROR",
                status_code=400
            )
        vehicle_id = existing_veh["vehicle_id"]

    try:
        driver = DriverModel.create(
            name=data["name"].strip(),
            phone=data["phone"].strip(),
            license_number=data["license_number"].strip().upper(),
            availability_status=data.get("availability_status", "available")
        )

        # If an existing vehicle was assigned, create/update schedule
        if vehicle_id:
            route_id = data.get("route_id", 1)
            shift = data.get("time_window", "Morning Shift (06:30 - 12:00)")
            execute_query(
                """INSERT INTO schedules (route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, status)
                   VALUES (?, ?, ?, '06:30:00', '12:00:00', ?, 'scheduled')""",
                (route_id, vehicle_id, driver["driver_id"], shift),
                fetch="insert"
            )

        driver_full = DriverModel.get_by_id(driver["driver_id"])
        return api_response(data=driver_full, message="Driver registered successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "DUPLICATE" in str(e).upper():
            return api_error(message="A driver with this phone or license number already exists.", error_code="DUPLICATE_RESOURCE", status_code=409)
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@drivers_bp.route("/<int:driver_id>", methods=["PUT"])
def update_driver(driver_id: int):
    """Updates driver attributes."""
    data = request.get_json() or {}
    try:
        driver = DriverModel.update(driver_id, **data)
        if not driver:
            return api_error(message=f"Driver with ID {driver_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=driver, message="Driver updated successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@drivers_bp.route("/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id: int):
    """Deletes a driver."""
    try:
        success = DriverModel.delete(driver_id)
        if not success:
            return api_error(message=f"Driver with ID {driver_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(message="Driver deleted successfully")
    except Exception as e:
        if "FOREIGN KEY" in str(e).upper() or "CONSTRAINT" in str(e).upper():
            return api_error(message="Cannot delete driver: active schedules reference this driver.", error_code="INTEGRITY_VIOLATION", status_code=409)
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@drivers_bp.route("/<int:driver_id>/duty", methods=["GET"])
def get_driver_duty(driver_id: int):
    """Retrieves driver's assigned vehicle, route details, and assigned students manifest."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message=f"Driver with ID {driver_id} not found", error_code="NOT_FOUND", status_code=404)

    # Find schedule for driver
    schedule = execute_query(
        """SELECT s.*, r.route_name, r.origin, r.destination, r.distance_km, r.estimated_duration_mins,
                  v.model AS vehicle_model, v.registration_number AS vehicle_reg, v.capacity AS vehicle_capacity,
                  v.vehicle_type, v.maintenance_status
           FROM schedules s
           JOIN routes r ON s.route_id = r.route_id
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.driver_id = ?
           ORDER BY CASE WHEN s.status = 'in_progress' THEN 1 WHEN s.status = 'scheduled' THEN 2 ELSE 3 END, s.schedule_id ASC
           LIMIT 1""",
        (driver_id,),
        fetch="one"
    )

    # Fallback if no specific schedule: select default route & vehicle
    if not schedule:
        schedule = execute_query(
            """SELECT s.*, r.route_name, r.origin, r.destination, r.distance_km, r.estimated_duration_mins,
                      v.model AS vehicle_model, v.registration_number AS vehicle_reg, v.capacity AS vehicle_capacity,
                      v.vehicle_type, v.maintenance_status
               FROM schedules s
               JOIN routes r ON s.route_id = r.route_id
               JOIN vehicles v ON s.vehicle_id = v.vehicle_id
               ORDER BY s.schedule_id ASC
               LIMIT 1""",
            fetch="one"
        )

    # Stops along route
    stops = []
    if schedule and schedule.get("route_id"):
        stops = execute_query(
            "SELECT stop_id, stop_name, sequence_no FROM stops WHERE route_id = ? ORDER BY sequence_no ASC",
            (schedule["route_id"],),
            fetch="all"
        )

    # Assigned students on this schedule / vehicle (strictly uncompleted journeys)
    students = []
    if schedule:
        sched_id = schedule.get("schedule_id")
        veh_id = schedule.get("vehicle_id")
        driver_avail = driver.get("availability_status", "available")
        sched_status = schedule.get("status", "scheduled")
        students = execute_query(
            """SELECT b.booking_id, b.seat_no, b.purpose, b.priority_level, b.requested_date, b.status,
                      u.name AS student_name, u.email AS student_email, u.phone AS student_phone,
                      u.student_id AS student_roll, u.department AS student_department,
                      CASE
                          WHEN b.status = 'completed' THEN 'completed'
                          WHEN b.status = 'cancelled' THEN 'cancelled'
                          WHEN b.status = 'in_route' OR ? = 'on_trip' OR ? = 'in_progress' THEN 'in_route'
                          ELSE 'not_started'
                      END AS ride_status
               FROM bookings b
               JOIN users u ON b.student_id = u.user_id
               WHERE (b.schedule_id = ? OR b.vehicle_id = ?) 
                 AND b.status NOT IN ('cancelled', 'aborted_requeued', 'completed')
               ORDER BY b.seat_no ASC""",
            (driver_avail, sched_status, sched_id, veh_id),
            fetch="all"
        ) or []

    # Calculate capacity telemetry
    veh_cap = schedule.get("vehicle_capacity", 40) if schedule else 40
    active_passengers = [s for s in students if s.get("status") in ("confirmed", "pending", "in_route")]
    full_seats = len(active_passengers)
    avail_seats = max(0, veh_cap - full_seats)
    occupancy_percent = round((full_seats / veh_cap) * 100, 1) if veh_cap > 0 else 0.0

    # 3 Operational Shifts Breakdown (Morning 06:30-12:00, Afternoon 13:00-16:00, Evening 16:00-19:00)
    morning_students = []
    afternoon_students = []
    evening_students = []
    for s in students:
        p_str = (s.get("purpose") or "").lower()
        if "afternoon" in p_str:
            afternoon_students.append(s)
        elif "evening" in p_str:
            evening_students.append(s)
        else:
            morning_students.append(s)

    shifts_telemetry = {
        "morning": {
            "shift_name": "Morning Shift",
            "time_window": "06:30 - 12:00",
            "booked_seats": len(morning_students),
            "capacity": veh_cap,
            "available_seats": max(0, veh_cap - len(morning_students))
        },
        "afternoon": {
            "shift_name": "Afternoon Shift",
            "time_window": "13:00 - 16:00",
            "booked_seats": len(afternoon_students),
            "capacity": veh_cap,
            "available_seats": max(0, veh_cap - len(afternoon_students))
        },
        "evening": {
            "shift_name": "Evening Shift",
            "time_window": "16:00 - 19:00",
            "booked_seats": len(evening_students),
            "capacity": veh_cap,
            "available_seats": max(0, veh_cap - len(evening_students))
        }
    }

    # Check pending or approved dispatch request for this driver
    dispatch_req = execute_query(
        "SELECT * FROM dispatch_requests WHERE driver_id = ? ORDER BY dispatch_id DESC LIMIT 1",
        (driver_id,),
        fetch="one"
    )

    # Compute overall ride status for this driver
    trip_ride_status = "not_started"
    if driver.get("availability_status") == "on_trip" or (schedule and schedule.get("status") == "in_progress"):
        trip_ride_status = "in_route"
    elif schedule and schedule.get("status") == "completed":
        trip_ride_status = "completed"

    return api_response(
        data={
            "driver": driver,
            "schedule": schedule,
            "stops": stops,
            "assigned_students": students,
            "passenger_count": len(students),
            "capacity": veh_cap,
            "full_seats": full_seats,
            "available_seats": avail_seats,
            "occupancy_percent": occupancy_percent,
            "can_request_dispatch": occupancy_percent >= 50.0,
            "dispatch_request": dispatch_req,
            "ride_status": trip_ride_status,
            "shifts": shifts_telemetry
        },
        message="Driver duty profile retrieved successfully"
    )


@drivers_bp.route("/<int:driver_id>/enroute", methods=["POST"])
def set_driver_enroute(driver_id: int):
    """Driver action: Starts trip and marks status as 'on_trip' / Enroute."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message="Driver not found", error_code="NOT_FOUND", status_code=404)

    execute_query("UPDATE drivers SET availability_status = 'on_trip' WHERE driver_id = ?", (driver_id,), fetch="none")
    active_sched = execute_query(
        "SELECT schedule_id FROM schedules WHERE driver_id = ? AND status != 'completed' ORDER BY departure_time ASC LIMIT 1",
        (driver_id,),
        fetch="one"
    ) or execute_query(
        "SELECT schedule_id FROM schedules WHERE driver_id = ? ORDER BY schedule_id ASC LIMIT 1",
        (driver_id,),
        fetch="one"
    )
    if active_sched:
        execute_query("UPDATE schedules SET status = 'in_progress' WHERE schedule_id = ?", (active_sched["schedule_id"],), fetch="none")
    else:
        execute_query("UPDATE schedules SET status = 'in_progress' WHERE driver_id = ?", (driver_id,), fetch="none")
    execute_query(
        """UPDATE bookings SET status = 'in_route'
           WHERE status IN ('confirmed', 'pending') AND (
               schedule_id IN (SELECT schedule_id FROM schedules WHERE driver_id = ?)
               OR vehicle_id IN (SELECT vehicle_id FROM schedules WHERE driver_id = ?)
               OR route_id IN (SELECT route_id FROM schedules WHERE driver_id = ?)
           )""",
        (driver_id, driver_id, driver_id),
        fetch="none"
    )
    updated = DriverModel.get_by_id(driver_id)
    return api_response(data=updated, message="Trip started! Bus is now Enroute.")


@drivers_bp.route("/<int:driver_id>/complete-ride", methods=["POST"])
def complete_driver_ride(driver_id: int):
    """Driver action: Single trip-level action that completes the current ride for all students on the bus."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message="Driver not found", error_code="NOT_FOUND", status_code=404)

    execute_query("UPDATE drivers SET availability_status = 'available' WHERE driver_id = ?", (driver_id,), fetch="none")
    in_prog_sched = execute_query(
        "SELECT schedule_id FROM schedules WHERE driver_id = ? AND status = 'in_progress' ORDER BY departure_time ASC LIMIT 1",
        (driver_id,),
        fetch="one"
    )
    if in_prog_sched:
        execute_query("UPDATE schedules SET status = 'completed' WHERE schedule_id = ?", (in_prog_sched["schedule_id"],), fetch="none")
    else:
        execute_query("UPDATE schedules SET status = 'completed' WHERE driver_id = ?", (driver_id,), fetch="none")

    # Mark active bookings for this driver's schedules/vehicles as completed
    execute_query(
        """UPDATE bookings SET status = 'completed'
           WHERE status IN ('confirmed', 'pending', 'in_route') AND (
               schedule_id IN (SELECT schedule_id FROM schedules WHERE driver_id = ?)
               OR vehicle_id IN (SELECT vehicle_id FROM schedules WHERE driver_id = ?)
           )""",
        (driver_id, driver_id),
        fetch="none"
    )

    updated = DriverModel.get_by_id(driver_id)
    return api_response(data=updated, message="Ride marked as completed! All passenger trips finalized.")


@drivers_bp.route("/<int:driver_id>/reset-trip", methods=["POST"])
def reset_driver_trip(driver_id: int):
    """Driver action: Resets trip back to 'scheduled' / 'not_started' for a new run."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message="Driver not found", error_code="NOT_FOUND", status_code=404)

    execute_query("UPDATE drivers SET availability_status = 'available' WHERE driver_id = ?", (driver_id,), fetch="none")
    execute_query("UPDATE schedules SET status = 'scheduled' WHERE driver_id = ?", (driver_id,), fetch="none")
    updated = DriverModel.get_by_id(driver_id)
    return api_response(data=updated, message="Trip reset! Ready for next scheduled run.")


@drivers_bp.route("/<int:driver_id>/ride-status", methods=["POST"])
def update_driver_ride_status(driver_id: int):
    """
    Driver action: Explicitly updates the driver's ride status:
    'not_started', 'in_route', or 'completed'.
    """
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message="Driver not found", error_code="NOT_FOUND", status_code=404)

    data = request.get_json() or {}
    status = data.get("status")
    if status not in ("not_started", "in_route", "completed"):
        return api_error(
            message="Invalid ride status. Allowed: 'not_started', 'in_route', 'completed'",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    if status == "in_route":
        execute_query("UPDATE drivers SET availability_status = 'on_trip' WHERE driver_id = ?", (driver_id,), fetch="none")
        active_sched = execute_query(
            "SELECT schedule_id FROM schedules WHERE driver_id = ? AND status != 'completed' ORDER BY departure_time ASC LIMIT 1",
            (driver_id,),
            fetch="one"
        ) or execute_query(
            "SELECT schedule_id FROM schedules WHERE driver_id = ? ORDER BY schedule_id ASC LIMIT 1",
            (driver_id,),
            fetch="one"
        )
        if active_sched:
            execute_query("UPDATE schedules SET status = 'in_progress' WHERE schedule_id = ?", (active_sched["schedule_id"],), fetch="none")
        else:
            execute_query("UPDATE schedules SET status = 'in_progress' WHERE driver_id = ?", (driver_id,), fetch="none")
        execute_query(
            """UPDATE bookings SET status = 'in_route'
               WHERE status IN ('confirmed', 'pending') AND (
                   schedule_id IN (SELECT schedule_id FROM schedules WHERE driver_id = ?)
                   OR vehicle_id IN (SELECT vehicle_id FROM schedules WHERE driver_id = ?)
                   OR route_id IN (SELECT route_id FROM schedules WHERE driver_id = ?)
               )""",
            (driver_id, driver_id, driver_id),
            fetch="none"
        )
        msg = "Ride status updated to In Route."
    elif status == "completed":
        execute_query("UPDATE drivers SET availability_status = 'available' WHERE driver_id = ?", (driver_id,), fetch="none")
        in_prog_sched = execute_query(
            "SELECT schedule_id FROM schedules WHERE driver_id = ? AND status = 'in_progress' ORDER BY departure_time ASC LIMIT 1",
            (driver_id,),
            fetch="one"
        )
        if in_prog_sched:
            execute_query("UPDATE schedules SET status = 'completed' WHERE schedule_id = ?", (in_prog_sched["schedule_id"],), fetch="none")
        else:
            execute_query("UPDATE schedules SET status = 'completed' WHERE driver_id = ?", (driver_id,), fetch="none")
        execute_query(
            """UPDATE bookings SET status = 'completed'
               WHERE status IN ('confirmed', 'pending', 'in_route') AND (
                   schedule_id IN (SELECT schedule_id FROM schedules WHERE driver_id = ?)
                   OR vehicle_id IN (SELECT vehicle_id FROM schedules WHERE driver_id = ?)
               )""",
            (driver_id, driver_id),
            fetch="none"
        )
        msg = "Ride marked as completed! Bus returned to depot."
    else:  # not_started
        execute_query("UPDATE drivers SET availability_status = 'available' WHERE driver_id = ?", (driver_id,), fetch="none")
        execute_query("UPDATE schedules SET status = 'scheduled' WHERE driver_id = ?", (driver_id,), fetch="none")
        msg = "Ride status reset to Not Yet Started."

    return api_response(data={"driver_id": driver_id, "ride_status": status}, message=msg)


# ==========================================
# 50% CAPACITY EARLY DISPATCH WORKFLOW
# ==========================================

@drivers_bp.route("/<int:driver_id>/request-dispatch", methods=["POST"])
def request_early_dispatch(driver_id: int):
    """
    Driver submits an early departure request to admin when vehicle is >= 50% booked.
    Admin will then review and approve before vehicle can depart.
    """
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message="Driver not found", error_code="NOT_FOUND", status_code=404)

    sched = execute_query(
        """SELECT s.schedule_id, s.route_id, s.vehicle_id, s.time_window, v.capacity
           FROM schedules s
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.driver_id = ? LIMIT 1""",
        (driver_id,),
        fetch="one"
    )
    if not sched:
        return api_error(message="No schedule found for this driver", error_code="NOT_FOUND", status_code=404)

    # Count confirmed passengers
    pass_cnt = execute_query(
        "SELECT COUNT(*) AS cnt FROM bookings WHERE (schedule_id = ? OR vehicle_id = ?) AND status NOT IN ('cancelled', 'completed')",
        (sched["schedule_id"], sched["vehicle_id"]),
        fetch="one"
    )["cnt"]

    cap = sched["capacity"] or 40
    pct = round((pass_cnt / cap) * 100, 1)

    data = request.get_json() or {}
    force = data.get("force", False)
    if pct < 50.0 and not force:
        return api_error(
            message=f"Vehicle has not reached the 50% booking threshold (currently {pct}% booked). Dispatch requests can only be sent once at least 50% capacity is booked.",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    msg = data.get("message", f"Bus is {pct}% full ({pass_cnt}/{cap} seats occupied). Requesting admin approval for departure.")

    req_id = execute_query(
        """INSERT INTO dispatch_requests (schedule_id, driver_id, vehicle_id, occupancy_percent, passenger_count, capacity, shift_window, message, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (sched["schedule_id"], driver_id, sched["vehicle_id"], pct, pass_cnt, cap, sched.get("time_window", "Morning Shift"), msg),
        fetch="insert"
    )

    req = execute_query("SELECT * FROM dispatch_requests WHERE dispatch_id = ?", (req_id,), fetch="one")
    return api_response(data=req, message="Early dispatch request submitted to Admin! Waiting for approval.", status_code=201)


@drivers_bp.route("/dispatch-requests", methods=["GET"])
def get_dispatch_requests():
    """Lists all driver early departure dispatch requests for Admin oversight."""
    requests_list = execute_query(
        """SELECT dr.*, d.name AS driver_name, d.phone AS driver_phone,
                  v.model AS vehicle_model, v.registration_number AS vehicle_reg,
                  r.route_name
           FROM dispatch_requests dr
           JOIN drivers d ON dr.driver_id = d.driver_id
           JOIN vehicles v ON dr.vehicle_id = v.vehicle_id
           LEFT JOIN schedules s ON dr.schedule_id = s.schedule_id
           LEFT JOIN routes r ON s.route_id = r.route_id
           ORDER BY dr.dispatch_id DESC""",
        fetch="all"
    )
    return api_response(data=requests_list, message="Dispatch requests retrieved successfully")


@drivers_bp.route("/dispatch-requests/<int:dispatch_id>/approve", methods=["POST"])
def approve_dispatch_request(dispatch_id: int):
    """Admin approves driver's early departure request and marks trip In Route."""
    execute_query("UPDATE dispatch_requests SET status = 'approved' WHERE dispatch_id = ?", (dispatch_id,), fetch="none")
    req = execute_query("SELECT * FROM dispatch_requests WHERE dispatch_id = ?", (dispatch_id,), fetch="one")
    if not req:
        return api_error(message="Dispatch request not found", error_code="NOT_FOUND", status_code=404)

    # When approved, set schedule to in_progress, driver to on_trip, and bookings to in_route
    driver_id = req["driver_id"]
    schedule_id = req["schedule_id"]
    vehicle_id = req["vehicle_id"]
    execute_query("UPDATE drivers SET availability_status = 'on_trip' WHERE driver_id = ?", (driver_id,), fetch="none")
    if schedule_id:
        execute_query("UPDATE schedules SET status = 'in_progress' WHERE schedule_id = ?", (schedule_id,), fetch="none")
    execute_query(
        """UPDATE bookings SET status = 'in_route'
           WHERE status IN ('confirmed', 'pending') AND (
               schedule_id = ? OR vehicle_id = ?
               OR route_id IN (SELECT route_id FROM schedules WHERE schedule_id = ?)
           )""",
        (schedule_id, vehicle_id, schedule_id),
        fetch="none"
    )

    return api_response(data=req, message="Dispatch request approved! Vehicle dispatched and ride marked In Route.")


@drivers_bp.route("/dispatch-requests/<int:dispatch_id>/reject", methods=["POST"])
def reject_dispatch_request(dispatch_id: int):
    """Admin rejects driver's early departure request."""
    execute_query("UPDATE dispatch_requests SET status = 'rejected' WHERE dispatch_id = ?", (dispatch_id,), fetch="none")
    req = execute_query("SELECT * FROM dispatch_requests WHERE dispatch_id = ?", (dispatch_id,), fetch="one")
    if not req:
        return api_error(message="Dispatch request not found", error_code="NOT_FOUND", status_code=404)

    return api_response(data=req, message="Dispatch request rejected. Driver should wait for additional bookings.")


# ==========================================
# DRIVER STATUS & LEAVES
# ==========================================

@drivers_bp.route("/<int:driver_id>/status", methods=["POST"])
def toggle_driver_status(driver_id: int):
    """Toggles driver status (available, on_trip, off_duty)."""
    data = request.get_json() or {}
    new_status = data.get("availability_status")
    if new_status not in ("available", "on_trip", "off_duty"):
        return api_error(message="Invalid status. Allowed: available, on_trip, off_duty", error_code="VALIDATION_ERROR", status_code=400)

    execute_query("UPDATE drivers SET availability_status = ? WHERE driver_id = ?", (new_status, driver_id), fetch="none")
    updated = DriverModel.get_by_id(driver_id)
    return api_response(data=updated, message=f"Driver status updated to {new_status}")


@drivers_bp.route("/<int:driver_id>/leaves", methods=["GET"])
def get_driver_leaves(driver_id: int):
    """Lists leave applications for a specific driver."""
    leaves = execute_query(
        "SELECT * FROM driver_leaves WHERE driver_id = ? ORDER BY leave_id DESC",
        (driver_id,),
        fetch="all"
    )
    return api_response(data=leaves, message="Driver leaves retrieved successfully")


@drivers_bp.route("/<int:driver_id>/leaves", methods=["POST"])
def apply_driver_leave(driver_id: int):
    """Submits a new leave application for a driver."""
    data = request.get_json() or {}
    required = ["start_date", "end_date", "leave_type", "reason"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    leave_id = execute_query(
        """INSERT INTO driver_leaves (driver_id, start_date, end_date, leave_type, reason, status)
           VALUES (?, ?, ?, ?, ?, 'Pending')""",
        (driver_id, data["start_date"], data["end_date"], data["leave_type"], data["reason"].strip()),
        fetch="insert"
    )
    execute_query("UPDATE drivers SET availability_status = 'off_duty' WHERE driver_id = ?", (driver_id,), fetch="none")

    created = execute_query("SELECT * FROM driver_leaves WHERE leave_id = ?", (leave_id,), fetch="one")

    # Notify admin about the leave
    try:
        driver_obj = DriverModel.get_by_id(driver_id)
        driver_name = driver_obj["name"] if driver_obj else f"Driver #{driver_id}"
        leave_type = data.get("leave_type", "Leave")
        reason = data.get("reason", "")
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        execute_query(
            """INSERT INTO notifications (type, title, message, driver_id, is_read)
               VALUES (?, ?, ?, ?, 0)""",
            (
                "driver_leave",
                f"📅 Driver Leave: {driver_name}",
                f"{driver_name} has submitted a {leave_type} request from {start_date} to {end_date}. "
                f"Reason: {str(reason)[:100]}. Please assign a relief driver to their route.",
                driver_id
            ),
            fetch="none"
        )
    except Exception as e:
        print(f"[Notification Error] Could not create driver_leave notification: {e}")

    return api_response(data=created, message="Leave application submitted successfully", status_code=201)


@drivers_bp.route("/leaves", methods=["GET"])
def get_all_leaves():
    """Admin endpoint: lists all driver leave applications with driver contact info."""
    leaves = execute_query(
        """SELECT l.leave_id, l.driver_id, l.start_date, l.end_date,
                  l.leave_type, l.reason, l.status, l.created_at,
                  d.name AS driver_name, d.phone AS driver_phone, d.license_number,
                  s.schedule_id, s.vehicle_id,
                  v.model AS vehicle_model, v.registration_number AS vehicle_reg
           FROM driver_leaves l
           JOIN drivers d ON l.driver_id = d.driver_id
           LEFT JOIN (
               SELECT driver_id,
                      MIN(schedule_id) AS schedule_id,
                      MIN(vehicle_id) AS vehicle_id
               FROM schedules
               WHERE status != 'cancelled'
               GROUP BY driver_id
           ) s ON d.driver_id = s.driver_id
           LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           ORDER BY l.leave_id DESC""",
        fetch="all"
    )
    return api_response(data=leaves, message="All driver leaves retrieved successfully")


@drivers_bp.route("/leaves/<int:leave_id>", methods=["PUT"])
def update_leave_status(leave_id: int):
    """Admin endpoint: approves or rejects a driver leave application."""
    data = request.get_json() or {}
    status = data.get("status")
    if status not in ("Approved", "Rejected", "Pending"):
        return api_error(message="Invalid status. Allowed: Approved, Rejected, Pending", error_code="VALIDATION_ERROR", status_code=400)

    execute_query("UPDATE driver_leaves SET status = ? WHERE leave_id = ?", (status, leave_id), fetch="none")
    leave = execute_query("SELECT * FROM driver_leaves WHERE leave_id = ?", (leave_id,), fetch="one")

    if leave and status == "Approved":
        execute_query("UPDATE drivers SET availability_status = 'off_duty' WHERE driver_id = ?", (leave["driver_id"],), fetch="none")

    return api_response(data=leave, message=f"Leave application marked as {status}")


@drivers_bp.route("/schedules/<int:schedule_id>/reassign", methods=["POST"])
def reassign_schedule_driver(schedule_id: int):
    """Admin endpoint: Reassigns an available driver to a schedule when the original driver is on leave."""
    data = request.get_json() or {}
    new_driver_id = data.get("driver_id")
    if not new_driver_id:
        return api_error(message="Missing required field: driver_id", error_code="VALIDATION_ERROR", status_code=400)

    driver = execute_query("SELECT driver_id, name, availability_status FROM drivers WHERE driver_id = ?", (new_driver_id,), fetch="one")
    if not driver:
        return api_error(message="Selected driver not found", error_code="NOT_FOUND", status_code=404)

    execute_query("UPDATE schedules SET driver_id = ? WHERE schedule_id = ?", (new_driver_id, schedule_id), fetch="none")
    execute_query("UPDATE drivers SET availability_status = 'available' WHERE driver_id = ?", (new_driver_id,), fetch="none")

    return api_response(
        data={"schedule_id": schedule_id, "driver_id": new_driver_id, "driver_name": driver["name"]},
        message=f"Vehicle schedule reassigned to Driver {driver['name']} successfully."
    )
