"""
Route REST CRUD Endpoints
"""

from flask import Blueprint, request
from backend.app.models.route import RouteModel
from backend.app.utils.response import api_response, api_error

routes_bp = Blueprint("routes", __name__, url_prefix="/api/routes")


@routes_bp.route("", methods=["GET"])
def get_routes():
    """Lists all transit routes."""
    routes = RouteModel.list_all()
    return api_response(data=routes, message="Routes retrieved successfully")


@routes_bp.route("/<int:route_id>", methods=["GET"])
def get_route(route_id: int):
    """Retrieves a single route by ID."""
    route = RouteModel.get_by_id(route_id)
    if not route:
        return api_error(message=f"Route with ID {route_id} not found", error_code="NOT_FOUND", status_code=404)
    return api_response(data=route, message="Route retrieved successfully")


@routes_bp.route("", methods=["POST"])
def create_route():
    """Creates a new transit route."""
    data = request.get_json() or {}
    required = ["route_name", "origin", "destination", "distance_km", "estimated_duration_mins"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(message=f"Missing required fields: {', '.join(missing)}", error_code="VALIDATION_ERROR", status_code=400)

    try:
        route = RouteModel.create(
            route_name=data["route_name"],
            origin=data["origin"],
            destination=data["destination"],
            distance_km=data["distance_km"],
            estimated_duration_mins=data["estimated_duration_mins"]
        )
        return api_response(data=route, message="Route created successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "DUPLICATE" in str(e).upper():
            return api_error(message="A route with this name already exists.", error_code="DUPLICATE_RESOURCE", status_code=409)
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@routes_bp.route("/<int:route_id>", methods=["PUT"])
def update_route(route_id: int):
    """Updates route attributes."""
    data = request.get_json() or {}
    try:
        route = RouteModel.update(route_id, **data)
        if not route:
            return api_error(message=f"Route with ID {route_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(data=route, message="Route updated successfully")
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@routes_bp.route("/<int:route_id>", methods=["DELETE"])
def delete_route(route_id: int):
    """Deletes a route."""
    try:
        success = RouteModel.delete(route_id)
        if not success:
            return api_error(message=f"Route with ID {route_id} not found", error_code="NOT_FOUND", status_code=404)
        return api_response(message="Route deleted successfully")
    except Exception as e:
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)
