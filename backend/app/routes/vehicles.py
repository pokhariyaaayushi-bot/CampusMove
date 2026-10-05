"""
Vehicle REST CRUD Endpoints
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)
"""

from flask import Blueprint, request
from backend.app.models.vehicle import VehicleModel
from backend.app.utils.response import api_response, api_error

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/api/vehicles")


@vehicles_bp.route("", methods=["GET"])
def get_vehicles():
    """Lists vehicles with optional status query parameters."""
    availability = request.args.get("availability_status")
    maintenance = request.args.get("maintenance_status")
    vehicles = VehicleModel.list_all(availability_status=availability, maintenance_status=maintenance)
    return api_response(data=vehicles, message="Vehicles retrieved successfully")


@vehicles_bp.route("/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id: int):
    """Retrieves a single vehicle by ID."""
    vehicle = VehicleModel.get_by_id(vehicle_id)
    if not vehicle:
        return api_error(message=f"Vehicle with ID {vehicle_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=vehicle, message="Vehicle retrieved successfully")


@vehicles_bp.route("", methods=["POST"])
def create_vehicle():
    """Creates a new vehicle record."""
    data = request.get_json() or {}
    required = ["registration_number", "model", "capacity"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    try:
        vehicle = VehicleModel.create(
            registration_number=data["registration_number"],
            model=data["model"],
            capacity=data["capacity"],
            availability_status=data.get("availability_status", "available"),
            maintenance_status=data.get("maintenance_status", "good")
        )
        return api_response(data=vehicle, message="Vehicle created successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "DUPLICATE" in str(e).upper():
            return api_error(message="A vehicle with this registration number already exists.", error_code="DUPLICATE_RESOURCE", status_code=409)
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@vehicles_bp.route("/<int:vehicle_id>", methods=["PUT"])
def update_vehicle(vehicle_id: int):
    """Updates vehicle attributes."""
    data = request.get_json() or {}
    try:
        vehicle = VehicleModel.update(vehicle_id, **data)
        if not vehicle:
            return api_error(message=f"Vehicle with ID {vehicle_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=vehicle, message="Vehicle updated successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@vehicles_bp.route("/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicle(vehicle_id: int):
    """Deletes a vehicle."""
    try:
        success = VehicleModel.delete(vehicle_id)
        if not success:
            return api_error(message=f"Vehicle with ID {vehicle_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(message="Vehicle deleted successfully")
    except Exception as e:
        if "FOREIGN KEY" in str(e).upper() or "CONSTRAINT" in str(e).upper():
            return api_error(message="Cannot delete vehicle: active schedules reference this vehicle.", error_code="INTEGRITY_VIOLATION", status_code=409)
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)
