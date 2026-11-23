"""
Daily Attendance & Seat Recycling REST Endpoints (Three-Tier Seating Model)
Handles Tier 1 absence reporting, dynamic seat recycling into Tier 2 Open Pool,
absence revocation, QR check-in, and emergency buffer releases.
"""

from flask import Blueprint, request
from backend.app.models.daily_attendance import DailyAttendanceModel
from backend.app.models.seat_allocation import SeatAllocationModel
from backend.app.db import execute_query
from backend.app.utils.response import api_response, api_error

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")


@attendance_bp.route("/mark-absent", methods=["POST"])
def mark_absent():
    """
    Tier 1 Fixed Seat holder marks themselves absent for a date.
    Releases their seat to the Tier 2 Open Pool for other commuters.
    """
    data = request.get_json() or {}
    allocation_id = data.get("allocation_id")
    student_id = data.get("student_id")
    query_date = data.get("date")
    reason = data.get("reason")

    # If student_id is provided instead of allocation_id, look up active pass
    if not allocation_id and student_id:
        passes = SeatAllocationModel.get_by_student(int(student_id), status="active")
        if passes:
            allocation_id = passes[0]["allocation_id"]
        else:
            return api_error(
                message=f"No active Tier 1 seat allocation found for user #{student_id}",
                error_code="ALLOCATION_NOT_FOUND",
                status_code=404
            )

    if not allocation_id:
        return api_error(message="allocation_id or student_id is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        res = DailyAttendanceModel.mark_absent(
            allocation_id=int(allocation_id),
            query_date=query_date,
            reason=reason
        )
        return api_response(data=res, message=res["message"])
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=f"Failed to mark absence: {e}", error_code="SERVER_ERROR", status_code=500)


@attendance_bp.route("/undo-absent", methods=["POST"])
def undo_absent():
    """
    Tier 1 Fixed Seat holder reclaims their seat if it has not yet been booked by a peer.
    """
    data = request.get_json() or {}
    allocation_id = data.get("allocation_id")
    student_id = data.get("student_id")
    query_date = data.get("date")

    if not allocation_id and student_id:
        passes = SeatAllocationModel.get_by_student(int(student_id), status="active")
        if passes:
            allocation_id = passes[0]["allocation_id"]

    if not allocation_id:
        return api_error(message="allocation_id or student_id is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        res = DailyAttendanceModel.undo_absent(
            allocation_id=int(allocation_id),
            query_date=query_date
        )
        return api_response(data=res, message=res["message"])
    except ValueError as e:
        return api_error(message=str(e), error_code="RECLAIM_DENIED", status_code=400)
    except Exception as e:
        return api_error(message=f"Failed to undo absence: {e}", error_code="SERVER_ERROR", status_code=500)


@attendance_bp.route("/check-in", methods=["POST"])
def check_in():
    """Records digital commuter boarding pass QR check-in."""
    data = request.get_json() or {}
    allocation_id = data.get("allocation_id")
    student_id = data.get("student_id")
    query_date = data.get("date")

    if not allocation_id and student_id:
        passes = SeatAllocationModel.get_by_student(int(student_id), status="active")
        if passes:
            allocation_id = passes[0]["allocation_id"]

    if not allocation_id:
        return api_error(message="allocation_id or student_id is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        res = DailyAttendanceModel.check_in(
            allocation_id=int(allocation_id),
            query_date=query_date
        )
        return api_response(data=res, message=res["message"])
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)


@attendance_bp.route("/today/<int:schedule_id>", methods=["GET"])
def get_today_schedule_attendance(schedule_id: int):
    """Lists today's attendance roster and seat recycling status for a schedule."""
    query_date = request.args.get("date")
    records = DailyAttendanceModel.get_schedule_attendance(schedule_id, query_date)
    return api_response(data=records, message="Schedule attendance roster retrieved successfully")


@attendance_bp.route("/auto-release", methods=["POST"])
def auto_release():
    """Auto-releases un-checked-in Tier 1 seats 15 minutes before bus departure."""
    data = request.get_json() or {}
    schedule_id = data.get("schedule_id")
    query_date = data.get("date")

    if not schedule_id:
        return api_error(message="schedule_id is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        res = DailyAttendanceModel.auto_release_unclaimed(int(schedule_id), query_date)
        return api_response(data=res, message=res["message"])
    except Exception as e:
        return api_error(message=f"Auto-release failed: {e}", error_code="SERVER_ERROR", status_code=500)


@attendance_bp.route("/auto-grab", methods=["POST"])
def auto_grab():
    """Auto-assigns newly released Tier 1 seats to waitlisted requests using enhanced priority."""
    data = request.get_json() or {}
    schedule_id = data.get("schedule_id")
    query_date = data.get("date")

    if not schedule_id:
        return api_error(message="schedule_id is required", error_code="VALIDATION_ERROR", status_code=400)

    try:
        res = DailyAttendanceModel.auto_grab_released_seat(int(schedule_id), query_date)
        return api_response(data=res, message=res["message"])
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=f"Auto-grab failed: {e}", error_code="SERVER_ERROR", status_code=500)
