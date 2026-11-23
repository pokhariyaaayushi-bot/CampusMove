"""
Seat Allocations REST Endpoints (Three-Tier Seating Model)
Admin management of Tier 1 Fixed Season-Pass allocations and telemetry.
"""

from flask import Blueprint, request
from backend.app.models.seat_allocation import SeatAllocationModel
from backend.app.models.daily_attendance import DailyAttendanceModel
from backend.app.db import execute_query
from backend.app.utils.response import api_response, api_error

seat_allocations_bp = Blueprint("seat_allocations", __name__, url_prefix="/api/seat-allocations")


@seat_allocations_bp.route("", methods=["GET"])
def list_seat_allocations():
    """Lists seat allocations with optional filtering by student, route, schedule, or semester."""
    student_id = request.args.get("student_id", type=int)
    route_id = request.args.get("route_id", type=int)
    schedule_id = request.args.get("schedule_id", type=int)
    vehicle_id = request.args.get("vehicle_id", type=int)
    semester = request.args.get("semester")
    status = request.args.get("status")

    if student_id:
        allocations = SeatAllocationModel.get_by_student(student_id, status=status)
    else:
        allocations = SeatAllocationModel.get_all(
            semester=semester,
            status=status,
            route_id=route_id,
            schedule_id=schedule_id,
            vehicle_id=vehicle_id
        )

    return api_response(data=allocations, message="Seat allocations retrieved successfully")


@seat_allocations_bp.route("", methods=["POST"])
def create_seat_allocation():
    """Creates a new Tier 1 Fixed Season-Pass allocation for a commuter."""
    data = request.get_json() or {}
    student_id = data.get("student_id")
    route_id = data.get("route_id")
    schedule_id = data.get("schedule_id")
    vehicle_id = data.get("vehicle_id")
    seat_no = data.get("seat_no")
    semester = data.get("semester", "2026-Monsoon")
    valid_from = data.get("valid_from", "2026-08-01")
    valid_until = data.get("valid_until", "2026-12-31")
    status = data.get("status", "active")

    if not student_id or not route_id or not seat_no:
        return api_error(message="student_id, route_id, and seat_no are required", error_code="VALIDATION_ERROR", status_code=400)

    # Auto-resolve schedule and vehicle if not provided
    if not schedule_id:
        sched = execute_query(
            "SELECT schedule_id, vehicle_id FROM schedules WHERE route_id = ? AND status != 'cancelled' ORDER BY schedule_id ASC LIMIT 1",
            (route_id,),
            fetch="one"
        )
        if sched:
            schedule_id = sched["schedule_id"]
            if not vehicle_id:
                vehicle_id = sched["vehicle_id"]
        else:
            return api_error(message=f"No active schedule found for route #{route_id}", error_code="SCHEDULE_NOT_FOUND", status_code=400)

    if not vehicle_id:
        sched = execute_query("SELECT vehicle_id FROM schedules WHERE schedule_id = ?", (schedule_id,), fetch="one")
        if sched:
            vehicle_id = sched["vehicle_id"]

    try:
        allocation = SeatAllocationModel.create(
            student_id=int(student_id),
            route_id=int(route_id),
            schedule_id=int(schedule_id),
            vehicle_id=int(vehicle_id),
            seat_no=int(seat_no),
            semester=semester,
            valid_from=valid_from,
            valid_until=valid_until,
            status=status
        )
        return api_response(data=allocation, message="Tier 1 Fixed Seat allocated successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=f"Failed to create allocation: {e}", error_code="DATABASE_ERROR", status_code=500)


@seat_allocations_bp.route("/<int:allocation_id>", methods=["GET"])
def get_allocation_by_id(allocation_id: int):
    """Retrieves an allocation by primary key ID."""
    alloc = SeatAllocationModel.get_by_id(allocation_id)
    if not alloc:
        return api_error(message=f"Allocation #{allocation_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=alloc)


@seat_allocations_bp.route("/<int:allocation_id>", methods=["PUT"])
def update_allocation(allocation_id: int):
    """Updates status of a seat allocation."""
    data = request.get_json() or {}
    status = data.get("status")
    if not status:
        return api_error(message="status is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        updated = SeatAllocationModel.update_status(allocation_id, status)
        if not updated:
            return api_error(message=f"Allocation #{allocation_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=updated, message=f"Allocation updated to {status}")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)


@seat_allocations_bp.route("/<int:allocation_id>", methods=["DELETE"])
def revoke_allocation(allocation_id: int):
    """Revokes an allocation."""
    success = SeatAllocationModel.delete(allocation_id)
    if not success:
        return api_error(message=f"Allocation #{allocation_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(message="Seat allocation revoked successfully")


@seat_allocations_bp.route("/my-seat", methods=["GET"])
def get_my_seat():
    """Returns the Tier 1 season pass and today's attendance status for a student."""
    student_id = request.args.get("student_id", type=int)
    date_str = request.args.get("date")

    if not student_id:
        return api_error(message="student_id is required", error_code="VALIDATION_ERROR", status_code=400)

    passes = SeatAllocationModel.get_by_student(student_id, status="active")
    if not passes:
        return api_response(data=None, message="No active Tier 1 season pass found for this user")

    active_pass = passes[0]
    today_att = DailyAttendanceModel.get_by_allocation(active_pass["allocation_id"], date_str)

    return api_response(data={
        "pass": active_pass,
        "today_attendance": today_att,
        "is_absent": today_att["status"] in ("absent", "auto_released") if today_att else False,
        "released_to_pool": today_att["released_to_pool"] == 1 if today_att else False,
        "reclaimed_by_peer": bool(today_att and today_att.get("booked_by_student_id"))
    })


@seat_allocations_bp.route("/schedule/<int:schedule_id>/tier-breakdown", methods=["GET"])
def get_schedule_tier_breakdown(schedule_id: int):
    """Returns full three-tier capacity breakdown for a schedule."""
    date_str = request.args.get("date")
    try:
        breakdown = SeatAllocationModel.get_tier_breakdown(schedule_id, date_str)
        return api_response(data=breakdown, message="Tier breakdown retrieved successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="NOT_FOUND", status_code=404)


@seat_allocations_bp.route("/vehicle/<int:vehicle_id>/tier-breakdown", methods=["GET"])
def get_vehicle_tier_breakdown(vehicle_id: int):
    """Returns three-tier breakdown by vehicle ID."""
    date_str = request.args.get("date")
    sched = execute_query(
        "SELECT schedule_id FROM schedules WHERE vehicle_id = ? AND status != 'cancelled' ORDER BY schedule_id ASC LIMIT 1",
        (vehicle_id,),
        fetch="one"
    )
    if not sched:
        return api_error(message=f"No active schedule for vehicle #{vehicle_id}", error_code="NOT_FOUND", status_code=404)

    try:
        breakdown = SeatAllocationModel.get_tier_breakdown(sched["schedule_id"], date_str)
        return api_response(data=breakdown, message="Tier breakdown retrieved successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="NOT_FOUND", status_code=404)


@seat_allocations_bp.route("/schedule/<int:schedule_id>/seat-map", methods=["GET"])
def get_schedule_seat_map(schedule_id: int):
    """
    Returns live interactive seat map layout for a bus schedule (§2.6):
      - 🟢 Fixed (taken by Tier 1 Season-Pass holder)
      - ⚪ Released by absentee (recycled - grab now!)
      - 🎟️ Claimed recycled (booked by peer)
      - 🟡 Open Pool (bookable Tier 2 dynamic seat)
      - 👤 Booked (Tier 2 occupant)
      - 🔴 Emergency (Tier 3 locked buffer)
    """
    from datetime import date
    query_date = request.args.get("date") or date.today().isoformat()

    sched = execute_query(
        """SELECT s.schedule_id, s.route_id, s.vehicle_id, s.departure_time, s.arrival_time, s.time_window,
                  COALESCE(s.direction, 'inbound') AS direction,
                  r.route_name, r.origin, r.destination,
                  v.model AS vehicle_model, v.registration_number AS vehicle_reg, v.capacity
           FROM schedules s
           JOIN routes r ON s.route_id = r.route_id
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.schedule_id = ?""",
        (schedule_id,),
        fetch="one"
    )
    if not sched:
        return api_error(message=f"Schedule #{schedule_id} not found", error_code="NOT_FOUND", status_code=404)

    capacity = sched["capacity"]
    tier3_reserve_nominal = 5 if capacity >= 20 else max(1, capacity // 5)
    tier3_seats = set(range(capacity - tier3_reserve_nominal + 1, capacity + 1))

    # Tier 1 allocations
    allocations = execute_query(
        """SELECT sa.allocation_id, sa.seat_no, sa.student_id, u.name AS student_name
           FROM seat_allocations sa
           JOIN users u ON sa.student_id = u.user_id
           WHERE sa.schedule_id = ? AND sa.status = 'active'""",
        (schedule_id,),
        fetch="all"
    ) or []
    t1_by_seat = {a["seat_no"]: a for a in allocations}

    # Attendance for today
    att_rows = execute_query(
        """SELECT da.attendance_id, da.allocation_id, da.status, da.released_to_pool, 
                  da.booked_by_student_id, sa.seat_no, bu.name AS booked_by_name
           FROM daily_attendance da
           JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id
           LEFT JOIN users bu ON da.booked_by_student_id = bu.user_id
           WHERE sa.schedule_id = ? AND da.date = ?""",
        (schedule_id, query_date),
        fetch="all"
    ) or []
    att_by_seat = {a["seat_no"]: a for a in att_rows}

    # Bookings on this schedule/date
    bookings = execute_query(
        """SELECT b.seat_no, b.priority_level, b.student_id, u.name AS student_name
           FROM bookings b
           JOIN users u ON b.student_id = u.user_id
           WHERE (b.schedule_id = ? OR b.vehicle_id = ?)
             AND b.requested_date = ?
             AND b.status NOT IN ('cancelled', 'aborted_requeued', 'completed')""",
        (schedule_id, sched["vehicle_id"], query_date),
        fetch="all"
    ) or []
    booking_by_seat = {b["seat_no"]: b for b in bookings if b.get("seat_no")}

    seat_list = []
    for s_no in range(1, capacity + 1):
        if s_no in t1_by_seat:
            alloc = t1_by_seat[s_no]
            att = att_by_seat.get(s_no)
            if att and att["status"] in ("absent", "auto_released") and att["released_to_pool"] == 1:
                if att.get("booked_by_student_id"):
                    state = "claimed_recycled"
                    label = f"Recycled & Claimed by {att['booked_by_name'] or 'Peer'}"
                    passenger = att["booked_by_name"]
                else:
                    state = "released_available"
                    label = "⚪ Released by Absentee — Grab Now!"
                    passenger = None
            else:
                state = "fixed_present"
                label = f"🟢 Fixed Season Pass ({alloc['student_name']})"
                passenger = alloc["student_name"]
            tier = "Tier 1: Fixed"
        elif s_no in tier3_seats:
            state = "emergency_locked"
            label = "🔴 Tier 3 Emergency Reserve (Buffer)"
            passenger = None
            tier = "Tier 3: Emergency"
        else:
            bk = booking_by_seat.get(s_no)
            if bk:
                state = "open_booked"
                label = f"👤 Booked ({bk['priority_level']}: {bk['student_name']})"
                passenger = bk["student_name"]
            else:
                state = "open_available"
                label = "🟡 Tier 2 Open Dynamic Pool (Available)"
                passenger = None
            tier = "Tier 2: Open Pool"

        seat_list.append({
            "seat_no": s_no,
            "tier": tier,
            "state": state,
            "label": label,
            "passenger": passenger
        })

    return api_response(data={
        "schedule": sched,
        "date": query_date,
        "capacity": capacity,
        "seats": seat_list,
        "summary": {
            "fixed_present": sum(1 for s in seat_list if s["state"] == "fixed_present"),
            "released_available": sum(1 for s in seat_list if s["state"] == "released_available"),
            "claimed_recycled": sum(1 for s in seat_list if s["state"] == "claimed_recycled"),
            "open_available": sum(1 for s in seat_list if s["state"] == "open_available"),
            "open_booked": sum(1 for s in seat_list if s["state"] == "open_booked"),
            "emergency_locked": sum(1 for s in seat_list if s["state"] == "emergency_locked")
        }
    }, message="Live seat map generated successfully")
