"""
Booking and Transport Request REST Endpoints
Handles student transport requests, priority-based booking allocations, and seat assignments.
"""

from flask import Blueprint, request
from backend.app.models.booking import BookingModel
from backend.app.db import execute_query, transaction
from backend.app.utils.response import api_response, api_error


def _send_vehicle_full_notification(vehicle_id: int, booked_count: int, capacity: int):
    """Send a notification to admin when a vehicle reaches full capacity."""
    try:
        # Prevent duplicate notifications if an unread alert for this vehicle already exists
        existing = execute_query(
            "SELECT notification_id FROM notifications WHERE vehicle_id = ? AND type = 'vehicle_full' AND is_read = 0",
            (vehicle_id,),
            fetch="one"
        )
        if existing:
            return

        vehicle = execute_query(
            "SELECT registration_number, model FROM vehicles WHERE vehicle_id = ?",
            (vehicle_id,),
            fetch="one"
        )
        reg = vehicle["registration_number"] if vehicle else f"Vehicle #{vehicle_id}"
        model = vehicle["model"] if vehicle else "Bus"
        execute_query(
            """INSERT INTO notifications (type, title, message, vehicle_id, is_read)
               VALUES (?, ?, ?, ?, 0)""",
            (
                "vehicle_full",
                f"🚌 Vehicle Full: {reg}",
                f"{model} ({reg}) has reached full capacity: {booked_count}/{capacity} seats booked. "
                f"Please assign a new vehicle and available driver for incoming booking requests.",
                vehicle_id
            ),
            fetch="none"
        )
    except Exception as e:
        print(f"[Notification Error] Could not create vehicle_full notification: {e}")

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api")


def validate_operational_shift(time_str: str, priority: str) -> tuple:
    """
    Validates that P2 and P3 routine transit requests fall strictly into one of the 3 designated shift windows:
    1. Morning Shift: after 06:30 till 12:00
    2. Afternoon Shift: 13:00 to 16:00
    3. Evening Shift: 16:00 to 19:00
    P1 (Emergency) is 24x7 exempt.
    """
    if priority == "P1":
        return True, "24x7 Emergency Link"

    if not time_str:
        return True, "Morning Shift (06:30 - 12:00)"

    try:
        parts = time_str.strip().split(":")
        hh = int(parts[0])
        mm = int(parts[1]) if len(parts) > 1 else 0
        total_mins = hh * 60 + mm

        # 06:30 (390 mins) to 12:00 (720 mins)
        if 390 <= total_mins <= 720:
            return True, "Morning Shift (06:30 - 12:00)"
        # 13:00 (780 mins) to 16:00 (960 mins)
        elif 780 <= total_mins <= 960:
            return True, "Afternoon Shift (13:00 - 16:00)"
        # 16:00 (960 mins) to 19:00 (1140 mins)
        elif 960 < total_mins <= 1140:
            return True, "Evening Shift (16:00 - 19:00)"
        else:
            return False, "Requested time is outside operational shift windows. P2 and P3 transit operates in 3 shifts: Morning (06:30 - 12:00), Afternoon (13:00 - 16:00), and Evening (16:00 - 19:00)."
    except Exception:
        return True, "Standard Shift"


@bookings_bp.route("/requests", methods=["GET"])
def get_transport_requests():
    """Lists transport requests with student and route details."""
    status = request.args.get("status")
    priority = request.args.get("priority")
    student_id = request.args.get("student_id", type=int)

    query = """
        SELECT 
            tr.request_id,
            tr.student_id,
            tr.route_id,
            tr.requested_time,
            tr.priority,
            tr.purpose,
            tr.status,
            tr.created_at,
            u.name AS student_name,
            u.email AS student_email,
            r.route_name,
            r.origin,
            r.destination
        FROM transport_requests tr
        JOIN users u ON tr.student_id = u.user_id
        JOIN routes r ON tr.route_id = r.route_id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND tr.status = ?"
        params.append(status)
    if priority:
        query += " AND tr.priority = ?"
        params.append(priority)
    if student_id:
        query += " AND tr.student_id = ?"
        params.append(student_id)

    query += " ORDER BY tr.request_id DESC"
    requests = execute_query(query, tuple(params), fetch="all")
    return api_response(data=requests, message="Transport requests retrieved successfully")


@bookings_bp.route("/requests", methods=["POST"])
def create_transport_request():
    """Submits a new transport request with priority level."""
    data = request.get_json() or {}
    required = ["student_id", "route_id", "requested_time", "priority", "purpose"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(
            message=f"Missing required fields: {', '.join(missing)}",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    priority = data["priority"]
    if priority not in ("P1", "P2", "P3"):
        return api_error(
            message="Priority must be 'P1' (Medical/Emergency), 'P2' (Faculty/Official), or 'P3' (Routine Student).",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    valid_shift, shift_info = validate_operational_shift(data.get("requested_time"), priority)
    if not valid_shift:
        return api_error(
            message=shift_info,
            error_code="SHIFT_VALIDATION_ERROR",
            status_code=400
        )

    try:
        sql = """
            INSERT INTO transport_requests (student_id, route_id, requested_time, priority, purpose, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """
        request_id = execute_query(
            sql,
            (
                data["student_id"],
                data["route_id"],
                data["requested_time"],
                priority,
                data["purpose"].strip()
            ),
            fetch="insert"
        )

        created = execute_query(
            """SELECT tr.*, u.name as student_name, r.route_name 
               FROM transport_requests tr 
               JOIN users u ON tr.student_id = u.user_id 
               JOIN routes r ON tr.route_id = r.route_id 
               WHERE tr.request_id = ?""",
            (request_id,),
            fetch="one"
        )
        return api_response(data=created, message="Transport request submitted successfully", status_code=201)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/bookings", methods=["GET"])
def get_bookings():
    """Lists bookings with joined student, route, schedule, and vehicle info."""
    student_id = request.args.get("student_id", type=int)
    status = request.args.get("status")
    priority = request.args.get("priority_level")
    bookings = BookingModel.list_all(student_id=student_id, status=status, priority_level=priority)
    return api_response(data=bookings, message="Bookings retrieved successfully")


@bookings_bp.route("/bookings/<int:booking_id>", methods=["GET"])
def get_booking(booking_id: int):
    """Retrieves single booking details."""
    booking = BookingModel.get_by_id(booking_id)
    if not booking:
        return api_error(message=f"Booking with ID {booking_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=booking, message="Booking retrieved successfully")


@bookings_bp.route("/bookings", methods=["POST"])
def create_booking():
    """Creates a confirmed booking with atomic transaction and concurrency locking."""
    data = request.get_json() or {}
    required = ["student_id", "route_id", "purpose", "requested_date"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(
            message=f"Missing required fields: {', '.join(missing)}",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    try:
        priority_level = data.get("priority_level", "P3")
        req_time = data.get("requested_time")
        if req_time:
            valid_shift, shift_info = validate_operational_shift(req_time, priority_level)
            if not valid_shift:
                return api_error(message=shift_info, error_code="SHIFT_VALIDATION_ERROR", status_code=400)

        request_id = data.get("request_id")
        if not request_id:
            try:
                request_id = execute_query(
                    """INSERT INTO transport_requests (student_id, route_id, requested_time, priority, purpose, status)
                       VALUES (?, ?, ?, ?, ?, 'allocated')""",
                    (
                        data["student_id"],
                        data["route_id"],
                        data.get("requested_time", "08:30:00"),
                        data.get("priority_level", "P3"),
                        data["purpose"].strip()
                    ),
                    fetch="insert"
                )
            except Exception:
                pass

        booking = BookingModel.create(
            student_id=data["student_id"],
            route_id=data["route_id"],
            purpose=data["purpose"],
            requested_date=data["requested_date"],
            request_id=request_id,
            schedule_id=data.get("schedule_id"),
            vehicle_id=data.get("vehicle_id"),
            seat_no=data.get("seat_no"),
            priority_level=data.get("priority_level", "P3"),
            status=data.get("status", "confirmed")
        )

        # If generated from a request, mark the request allocated
        if request_id:
            execute_query(
                "UPDATE transport_requests SET status = 'allocated' WHERE request_id = ?",
                (request_id,),
                fetch="none"
            )

        # Check if the assigned vehicle is now FULL — if so, notify admin
        if booking and booking.get("vehicle_id"):
            veh_id = booking["vehicle_id"]
            veh_row = execute_query(
                "SELECT capacity FROM vehicles WHERE vehicle_id = ?",
                (veh_id,),
                fetch="one"
            )
            if veh_row:
                cap = veh_row["capacity"] or 40
                booked_count_row = execute_query(
                    """SELECT COUNT(*) as cnt FROM bookings
                       WHERE vehicle_id = ? AND status NOT IN ('cancelled', 'aborted_requeued', 'completed')""",
                    (veh_id,),
                    fetch="one"
                )
                booked_count = booked_count_row["cnt"] if booked_count_row else 0
                if booked_count >= cap:
                    _send_vehicle_full_notification(veh_id, booked_count, cap)

        return api_response(data=booking, message="Booking confirmed successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/bookings/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id: int):
    """Updates booking status or seat assignment."""
    data = request.get_json() or {}
    try:
        updated = BookingModel.update(booking_id, **data)
        if not updated:
            return api_error(message=f"Booking with ID {booking_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=updated, message="Booking updated successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id: int):
    """Cancels or deletes a booking."""
    try:
        success = BookingModel.delete(booking_id)
        if not success:
            return api_error(message=f"Booking with ID {booking_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(message="Booking cancelled successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking_action(booking_id: int):
    """
    Student action: Cancel a booking by transitioning its status to 'cancelled'.
    Also cascades the cancellation to the linked transport_request (if any).
    """
    booking = BookingModel.get_by_id(booking_id)
    if not booking:
        return api_error(message=f"Booking with ID {booking_id} not found", error_code="NOT_FOUND", status_code=404)

    data = request.get_json(silent=True) or {}
    requester_id = data.get("user_id") or data.get("student_id")
    requester_role = data.get("role", "student")

    # BOLA / IDOR Authorization Check
    if requester_id and requester_role != "admin" and int(booking["student_id"]) != int(requester_id):
        return api_error(
            message="Unauthorized: You cannot cancel a booking belonging to another passenger.",
            error_code="FORBIDDEN_CANCELLATION",
            status_code=403
        )

    if booking["status"] in ("cancelled", "completed"):
        return api_error(
            message=f"Booking is already '{booking['status']}' and cannot be cancelled.",
            error_code="INVALID_STATE_TRANSITION",
            status_code=409
        )

    try:
        updated = BookingModel.update(booking_id, status="cancelled")

        # Cascade: if this booking was linked to a transport_request, cancel that too
        if booking.get("request_id"):
            execute_query(
                "UPDATE transport_requests SET status = 'cancelled' WHERE request_id = ? AND status != 'cancelled'",
                (booking["request_id"],),
                fetch="none"
            )

        return api_response(data=updated, message="Booking cancelled successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/bookings/<int:booking_id>/complete", methods=["POST"])
def complete_booking_action(booking_id: int):
    """
    Administrator action: Mark a booking as 'completed' once the ride is finished.
    Also marks the linked transport_request as 'allocated' (already fulfilled).
    """
    booking = BookingModel.get_by_id(booking_id)
    if not booking:
        return api_error(message=f"Booking with ID {booking_id} not found", error_code="NOT_FOUND", status_code=404)

    if booking["status"] == "completed":
        return api_error(
            message="Booking is already marked as completed.",
            error_code="INVALID_STATE_TRANSITION",
            status_code=409
        )

    if booking["status"] == "cancelled":
        return api_error(
            message="A cancelled booking cannot be marked as completed.",
            error_code="INVALID_STATE_TRANSITION",
            status_code=409
        )

    try:
        updated = BookingModel.update(booking_id, status="completed")
        return api_response(data=updated, message="Ride marked as completed successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@bookings_bp.route("/requests/<int:request_id>/cancel", methods=["POST"])
def cancel_transport_request(request_id: int):
    """
    Cancel a pending transport request directly (before a booking is created).
    Removes it from the OS priority scheduling queue.
    """
    req = execute_query(
        "SELECT * FROM transport_requests WHERE request_id = ?",
        (request_id,),
        fetch="one"
    )
    if not req:
        return api_error(message=f"Transport request with ID {request_id} not found", error_code="NOT_FOUND", status_code=404)

    if req["status"] == "cancelled":
        return api_error(
            message="Transport request is already cancelled.",
            error_code="INVALID_STATE_TRANSITION",
            status_code=409
        )

    try:
        execute_query(
            "UPDATE transport_requests SET status = 'cancelled' WHERE request_id = ?",
            (request_id,),
            fetch="none"
        )
        updated = execute_query(
            "SELECT * FROM transport_requests WHERE request_id = ?",
            (request_id,),
            fetch="one"
        )
        return api_response(data=updated, message="Transport request cancelled successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


