"""
Driver Domain Model & Data Access
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)

Enforces relational constraints and raw SQL interactions for driver resources.
"""

from backend.app.db import execute_query

VALID_DRIVER_AVAILABILITY = {"available", "on_trip", "off_duty"}


class DriverModel:
    @staticmethod
    def validate_attributes(availability: str = "available"):
        """Validates driver availability status."""
        if availability not in VALID_DRIVER_AVAILABILITY:
            raise ValueError(f"Invalid driver availability status '{availability}'. Allowed: {VALID_DRIVER_AVAILABILITY}")

    @classmethod
    def create(cls, name: str, phone: str, license_number: str, availability_status: str = "available"):
        """Inserts a new driver record into the database."""
        cls.validate_attributes(availability_status)
        if not name or not phone or not license_number:
            raise ValueError("Driver name, phone, and license_number are required fields.")

        sql = """
            INSERT INTO drivers (name, phone, license_number, availability_status)
            VALUES (?, ?, ?, ?)
        """
        driver_id = execute_query(
            sql,
            (name.strip(), phone.strip(), license_number.strip().upper(), availability_status),
            fetch="insert"
        )
        return cls.get_by_id(driver_id)

    @classmethod
    def get_by_id(cls, driver_id: int):
        """Retrieves a single driver by primary key."""
        sql = "SELECT * FROM drivers WHERE driver_id = ?"
        return execute_query(sql, (driver_id,), fetch="one")

    @classmethod
    def get_by_license(cls, license_number: str):
        """Retrieves a driver by unique license number."""
        sql = "SELECT * FROM drivers WHERE license_number = ?"
        return execute_query(sql, (license_number.strip().upper(),), fetch="one")

    @classmethod
    def list_all(cls, availability_status: str = None):
        """Lists drivers with optional status filtering."""
        query = "SELECT * FROM drivers WHERE 1=1"
        params = []
        if availability_status:
            query += " AND availability_status = ?"
            params.append(availability_status)
        query += " ORDER BY driver_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def update(cls, driver_id: int, **kwargs):
        """Updates driver attributes."""
        existing = cls.get_by_id(driver_id)
        if not existing:
            return None

        availability = kwargs.get("availability_status", existing["availability_status"])
        cls.validate_attributes(availability)

        allowed_fields = ["name", "phone", "license_number", "availability_status"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                if key == "license_number":
                    params.append(value.strip().upper())
                elif isinstance(value, str):
                    params.append(value.strip())
                else:
                    params.append(value)

        if not updates:
            return existing

        params.append(driver_id)
        sql = f"UPDATE drivers SET {', '.join(updates)} WHERE driver_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(driver_id)

    @classmethod
    def delete(cls, driver_id: int):
        """Deletes a driver record by ID."""
        sql = "DELETE FROM drivers WHERE driver_id = ?"
        rows_affected = execute_query(sql, (driver_id,), fetch="none")
        return rows_affected > 0
