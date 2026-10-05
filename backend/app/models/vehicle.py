"""
Vehicle Domain Model & Data Access
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)

Enforces relational constraints and raw SQL interactions for fleet resources.
"""

from backend.app.db import execute_query

VALID_AVAILABILITY = {"available", "in_use", "maintenance"}
VALID_MAINTENANCE = {"good", "due", "under_repair"}
VALID_OWNER_TYPES = {"college", "private"}


class VehicleModel:
    @staticmethod
    def validate_attributes(capacity: int, availability: str = "available", maintenance: str = "good", owner_type: str = "college"):
        """Validates vehicle domain constraints before SQL execution."""
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("Vehicle capacity must be a positive integer.")
        if availability not in VALID_AVAILABILITY:
            raise ValueError(f"Invalid availability status '{availability}'. Allowed: {VALID_AVAILABILITY}")
        if maintenance not in VALID_MAINTENANCE:
            raise ValueError(f"Invalid maintenance status '{maintenance}'. Allowed: {VALID_MAINTENANCE}")
        if owner_type not in VALID_OWNER_TYPES:
            raise ValueError(f"Invalid owner type '{owner_type}'. Allowed: {VALID_OWNER_TYPES}")

    @classmethod
    def create(cls, registration_number: str, model: str, capacity: int,
               availability_status: str = "available", maintenance_status: str = "good",
               owner_type: str = "college"):
        """Inserts a new vehicle record into the database."""
        cls.validate_attributes(capacity, availability_status, maintenance_status, owner_type)
        reg_clean = registration_number.strip().upper()
        model_clean = model.strip()
        sql = """
            INSERT INTO vehicles (registration_number, registration_no, model, vehicle_type, capacity, availability_status, maintenance_status, owner_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        vehicle_id = execute_query(
            sql,
            (reg_clean, reg_clean, model_clean, model_clean, capacity, availability_status, maintenance_status, owner_type),
            fetch="insert"
        )
        return cls.get_by_id(vehicle_id)

    @classmethod
    def get_by_id(cls, vehicle_id: int):
        """Retrieves a single vehicle by primary key."""
        sql = "SELECT * FROM vehicles WHERE vehicle_id = ?"
        return execute_query(sql, (vehicle_id,), fetch="one")

    @classmethod
    def get_by_registration(cls, registration_number: str):
        """Retrieves a vehicle by unique registration number."""
        sql = "SELECT * FROM vehicles WHERE registration_number = ?"
        return execute_query(sql, (registration_number.strip().upper(),), fetch="one")

    @classmethod
    def list_all(cls, availability_status: str = None, maintenance_status: str = None):
        """Lists vehicles with optional filtering by status."""
        query = "SELECT * FROM vehicles WHERE 1=1"
        params = []
        if availability_status:
            query += " AND availability_status = ?"
            params.append(availability_status)
        if maintenance_status:
            query += " AND maintenance_status = ?"
            params.append(maintenance_status)
        query += " ORDER BY vehicle_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def update(cls, vehicle_id: int, **kwargs):
        """Updates specific fields of an existing vehicle."""
        existing = cls.get_by_id(vehicle_id)
        if not existing:
            return None

        capacity = kwargs.get("capacity", existing["capacity"])
        availability = kwargs.get("availability_status", existing["availability_status"])
        maintenance = kwargs.get("maintenance_status", existing["maintenance_status"])
        cls.validate_attributes(capacity, availability, maintenance)

        allowed_fields = ["registration_number", "model", "capacity", "availability_status", "maintenance_status"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                if key == "registration_number":
                    params.append(value.strip().upper())
                else:
                    params.append(value)

        if not updates:
            return existing

        params.append(vehicle_id)
        sql = f"UPDATE vehicles SET {', '.join(updates)} WHERE vehicle_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(vehicle_id)

    @classmethod
    def delete(cls, vehicle_id: int):
        """Deletes a vehicle by ID. Relational constraints protect active schedules."""
        sql = "DELETE FROM vehicles WHERE vehicle_id = ?"
        rows_affected = execute_query(sql, (vehicle_id,), fetch="none")
        return rows_affected > 0
