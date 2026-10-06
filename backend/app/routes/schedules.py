"""
Schedule REST CRUD Endpoints (Relational Joins)
"""

from flask import Blueprint, request
from backend.app.models.schedule import ScheduleModel
from backend.app.utils.response import api_response, api_error

schedules_bp = Blueprint("schedules", __name__, url_prefix="/api/schedules")


@schedules_bp.route("", methods=["GET"])
def get_schedules():
    """Lists schedules with joined route, vehicle, and driver details."""
    route_id = request.args.get("route_id", type=int)
    status = request.args.get("status")
    schedules = ScheduleModel.list_all(route_id=route_id, status=status, detailed=True)
    return api_response(data=schedules, message="Schedules retrieved successfully")


@schedules_bp.route("/<int:schedule_id>", methods=["GET"])
def get_schedule(schedule_id: int):
    """Retrieves schedule details with joined entities."""
    schedule = ScheduleModel.get_by_id(schedule_id, detailed=True)
    if not schedule:
        return api_error(message=f"Schedule with ID {schedule_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=schedule, message="Schedule retrieved successfully")


@schedules_bp.route("", methods=["POST"])
def create_schedule():
    """Creates a new transit schedule."""
    data = request.get_json() or {}
    required = ["route_id", "vehicle_id", "driver_id", "departure_time", "arrival_time", "time_window"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    try:
        schedule = ScheduleModel.create(
            route_id=data["route_id"],
            vehicle_id=data["vehicle_id"],
            driver_id=data["driver_id"],
            departure_time=data["departure_time"],
            arrival_time=data["arrival_time"],
            time_window=data["time_window"],
            status=data.get("status", "scheduled")
        )
        return api_response(data=schedule, message="Schedule created successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        if "FOREIGN KEY" in str(e).upper() or "CONSTRAINT" in str(e).upper():
            return api_error(
                message="Invalid foreign key: specified route, vehicle, or driver does not exist.",
                error_code="FOREIGN_KEY_VIOLATION",
                status_code=400
            )
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@schedules_bp.route("/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id: int):
    """Updates schedule details or status."""
    data = request.get_json() or {}
    try:
        schedule = ScheduleModel.update(schedule_id, **data)
        if not schedule:
            return api_error(message=f"Schedule with ID {schedule_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=schedule, message="Schedule updated successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@schedules_bp.route("/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id: int):
    """Deletes a schedule."""
    try:
        success = ScheduleModel.delete(schedule_id)
        if not success:
            return api_error(message=f"Schedule with ID {schedule_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(message="Schedule deleted successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)
