"""
Driver REST CRUD Endpoints
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)
"""

from flask import Blueprint, request
from backend.app.models.driver import DriverModel
from backend.app.utils.response import api_response, api_error

drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/drivers")


@drivers_bp.route("", methods=["GET"])
def get_drivers():
    """Lists drivers with optional availability filter."""
    availability = request.args.get("availability_status")
    drivers = DriverModel.list_all(availability_status=availability)
    return api_response(data=drivers, message="Drivers retrieved successfully")


@drivers_bp.route("/<int:driver_id>", methods=["GET"])
def get_driver(driver_id: int):
    """Retrieves a single driver by ID."""
    driver = DriverModel.get_by_id(driver_id)
    if not driver:
        return api_error(message=f"Driver with ID {driver_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=driver, message="Driver retrieved successfully")


@drivers_bp.route("", methods=["POST"])
def create_driver():
    """Creates a new driver record."""
    data = request.get_json() or {}
    required = ["name", "phone", "license_number"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    try:
        driver = DriverModel.create(
            name=data["name"],
            phone=data["phone"],
            license_number=data["license_number"],
            availability_status=data.get("availability_status", "available")
        )
        return api_response(data=driver, message="Driver created successfully", status_code=201)
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
