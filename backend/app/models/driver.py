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
        """Retrieves a single driver by primary key with assigned vehicle details."""
        sql = """
            SELECT d.*,
                   v.vehicle_id, v.model AS assigned_vehicle, v.registration_number AS assigned_reg,
                   v.vehicle_type, COALESCE(v.capacity, 40) AS capacity,
                   r.route_id, r.route_name,
                   COALESCE(bk.booked_count, 0) AS full_seats,
                   MAX(0, COALESCE(v.capacity, 40) - COALESCE(bk.booked_count, 0)) AS available_seats
            FROM drivers d
            LEFT JOIN schedules s ON d.driver_id = s.driver_id
            LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            LEFT JOIN routes r ON s.route_id = r.route_id
            LEFT JOIN (
                SELECT schedule_id, COUNT(*) AS booked_count
                FROM bookings
                WHERE status IN ('confirmed', 'pending')
                GROUP BY schedule_id
            ) bk ON s.schedule_id = bk.schedule_id
            WHERE d.driver_id = ?
        """
        return execute_query(sql, (driver_id,), fetch="one")

    @classmethod
    def get_by_license(cls, license_number: str):
        """Retrieves a driver by unique license number."""
        sql = "SELECT * FROM drivers WHERE license_number = ?"
        return execute_query(sql, (license_number.strip().upper(),), fetch="one")

    @classmethod
    def list_all(cls, availability_status: str = None):
        """Lists drivers with joined assigned vehicle and seat availability."""
        query = """
            SELECT d.*,
                   v.vehicle_id, v.model AS assigned_vehicle, v.registration_number AS assigned_reg,
                   v.vehicle_type, COALESCE(v.capacity, 40) AS capacity,
                   r.route_id, r.route_name,
                   COALESCE(bk.booked_count, 0) AS full_seats,
                   MAX(0, COALESCE(v.capacity, 40) - COALESCE(bk.booked_count, 0)) AS available_seats
            FROM drivers d
            LEFT JOIN schedules s ON d.driver_id = s.driver_id
            LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            LEFT JOIN routes r ON s.route_id = r.route_id
            LEFT JOIN (
                SELECT schedule_id, COUNT(*) AS booked_count
                FROM bookings
                WHERE status IN ('confirmed', 'pending')
                GROUP BY schedule_id
            ) bk ON s.schedule_id = bk.schedule_id
            WHERE 1=1
        """
        params = []
        if availability_status:
            query += " AND d.availability_status = ?"
            params.append(availability_status)
        query += " ORDER BY d.driver_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def update(cls, driver_id: int, **kwargs):
        """Updates driver attributes."""
        existing = cls.get_by_id(driver_id)
        if not existing:
            return None

        availability = kwargs.get("availability_status", existing["availability_status"])
        cls.validate_attributes(availability)

        allowed = ["name", "phone", "license_number", "availability_status"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                if key == "license_number":
                    params.append(value.strip().upper())
                else:
                    params.append(value.strip() if isinstance(value, str) else value)

        if not updates:
            return existing

        params.append(driver_id)
        sql = f"UPDATE drivers SET {', '.join(updates)} WHERE driver_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(driver_id)

    @classmethod
    def delete(cls, driver_id: int):
        """Deletes a driver record."""
        sql = "DELETE FROM drivers WHERE driver_id = ?"
        rows_affected = execute_query(sql, (driver_id,), fetch="none")
        return rows_affected > 0
