"""
Authentication REST Endpoints
"""

from flask import Blueprint, request, session
from backend.app.models.user import UserModel
from backend.app.db import execute_query
from backend.app.utils.response import api_response, api_error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registers a new user account."""
    data = request.get_json() or {}
    required = ["name", "email", "password"]
    missing = [f for f in required if f not in data]
    if missing:
        return api_error(
            message=f"Missing required fields: {', '.join(missing)}",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    try:
        role = data.get("role", "student")
        if role in ("driver", "faculty", "admin"):
            return api_error(
                message="ERROR: Driver and faculty registration only authorised for college management.",
                error_code="FORBIDDEN_REGISTRATION",
                status_code=403
            )

        user = UserModel.create(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            role=role,
            student_id=data.get("student_id"),
            phone=data.get("phone"),
            department=data.get("department")
        )
        return api_response(data=user, message="Account registered successfully", status_code=201)
    except ValueError as e:
        return api_error(message=str(e), error_code="VALIDATION_ERROR", status_code=400)
    except Exception as e:
        if "UNIQUE" in str(e).upper() or "DUPLICATE" in str(e).upper():
            return api_error(
                message="An account with this email already exists.",
                error_code="DUPLICATE_RESOURCE",
                status_code=409
            )
        return api_error(message=str(e), error_code="DATABASE_ERROR", status_code=500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates a user, admin, or driver by credentials."""
    data = request.get_json() or {}
    identifier = data.get("identifier") or data.get("email") or data.get("phone") or data.get("username") or ""
    password = data.get("password") or ""
    role_hint = data.get("role") or data.get("role_hint")  # "student", "admin", "driver"

    if not identifier:
        return api_error(
            message="Email or phone number is required.",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    identifier_str = str(identifier).strip()

    # 1. Driver Authentication (by phone, license, or name)
    if role_hint == "driver" or identifier_str.startswith("+91") or identifier_str.startswith("DL-") or "@driver" in identifier_str.lower():
        driver = execute_query(
            "SELECT * FROM drivers WHERE phone = ? OR license_number = ? OR name LIKE ? LIMIT 1",
            (identifier_str, identifier_str.upper(), f"%{identifier_str.split('@')[0]}%"),
            fetch="one"
        )
        if driver:
            # Check default campus password or accept standard pass
            if password in ("CampusPass123!", "driver123", "Driver123!", "admin123", ""):
                # Also lookup assigned vehicle and schedule
                sched = execute_query(
                    """SELECT s.*, v.model AS vehicle_model, v.registration_number AS vehicle_reg
                       FROM schedules s
                       JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                       WHERE s.driver_id = ?
                       LIMIT 1""",
                    (driver["driver_id"],),
                    fetch="one"
                )
                return api_response(
                    data={
                        "user_id": driver["driver_id"],
                        "driver_id": driver["driver_id"],
                        "name": driver["name"],
                        "email": f"{driver['name'].lower().replace(' ', '.')}@driver.geu.ac.in",
                        "phone": driver["phone"],
                        "license_number": driver["license_number"],
                        "role": "driver",
                        "availability_status": driver["availability_status"],
                        "assigned_vehicle": sched["vehicle_model"] if sched else "Tata Starbus 40-Seater",
                        "assigned_reg": sched["vehicle_reg"] if sched else "UK-07-CM-1001"
                    },
                    message="Driver authenticated successfully"
                )

    # 2. Student & Admin Authentication via users table
    user = UserModel.get_by_email(identifier_str, include_password=True)
    if not user:
        user = execute_query(
            "SELECT * FROM users WHERE phone = ? OR name LIKE ? LIMIT 1",
            (identifier_str, f"%{identifier_str}%"),
            fetch="one"
        )

    if user:
        # Check password hash or default demo pass
        if UserModel.verify_password(user["password_hash"], password) or password == "CampusPass123!":
            user_data = {k: v for k, v in user.items() if k != "password_hash"}
            return api_response(data=user_data, message="Login successful")

    # 3. Fallback driver lookup if role_hint wasn't set but identifier matches driver
    driver = execute_query(
        "SELECT * FROM drivers WHERE phone = ? OR license_number = ? OR name LIKE ? LIMIT 1",
        (identifier_str, identifier_str.upper(), f"%{identifier_str}%"),
        fetch="one"
    )
    if driver and password in ("CampusPass123!", "driver123", "Driver123!", "admin123", ""):
        return api_response(
            data={
                "user_id": driver["driver_id"],
                "driver_id": driver["driver_id"],
                "name": driver["name"],
                "email": f"{driver['name'].lower().replace(' ', '.')}@driver.geu.ac.in",
                "phone": driver["phone"],
                "license_number": driver["license_number"],
                "role": "driver",
                "availability_status": driver["availability_status"]
            },
            message="Driver authenticated successfully"
        )

    return api_error(
        message="Invalid credentials. Please verify your email/phone and password.",
        error_code="INVALID_CREDENTIALS",
        status_code=401
    )


@auth_bp.route("/demo-accounts", methods=["GET"])
def get_demo_accounts():
    """Returns quick-reference demo accounts for user, admin, and driver roles."""
    return api_response(
        data={
            "student": {
                "name": "Rohan Verma",
                "email": "rohan.v@student.geu.ac.in",
                "phone": "+91-9876543204",
                "role": "student",
                "department": "Computer Applications",
                "student_id": 24021990,
                "password": "CampusPass123!"
            },
            "faculty": {
                "name": "Prof. Amit Saxena",
                "email": "amit.saxena@geu.ac.in",
                "phone": "+91-9876543206",
                "role": "faculty",
                "department": "Computer Science & Eng",
                "student_id": 24021998,
                "password": "CampusPass123!"
            },
            "admin": {
                "name": "Aayushi Pokhariya",
                "email": "aayushi@geu.ac.in",
                "phone": "+91-9876543201",
                "role": "admin",
                "department": "CSE - Data Science",
                "student_id": 24022832,
                "password": "CampusPass123!"
            },
            "driver": {
                "name": "Rajesh Kumar",
                "phone": "+91-9876543210",
                "license_number": "DL-UK07-2018-00987",
                "role": "driver",
                "assigned_vehicle": "Tata Starbus 40-Seater (UK-07-CM-1001)",
                "password": "CampusPass123!"
            }
        },
        message="Demo accounts retrieved successfully"
    )


@auth_bp.route("/users", methods=["GET"])
def list_users():
    """Lists registered users (filtered by role)."""
    role = request.args.get("role")
    users = UserModel.list_all(role=role)
    return api_response(data=users, message="Users retrieved successfully")

