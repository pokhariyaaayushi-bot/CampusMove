"""
Schedule Domain Model & Relational Queries

Handles transit schedules, directions (inbound/outbound), multiple time-slot departures,
and multi-table SQL JOINs linking Routes, Vehicles, and Drivers.
"""

from backend.app.db import execute_query

VALID_SCHEDULE_STATUS = {"scheduled", "in_progress", "completed", "cancelled"}
VALID_DIRECTIONS = {"inbound", "outbound"}


class ScheduleModel:
    @staticmethod
    def validate_status(status: str):
        if status not in VALID_SCHEDULE_STATUS:
            raise ValueError(f"Invalid schedule status '{status}'. Allowed: {VALID_SCHEDULE_STATUS}")

    @staticmethod
    def validate_direction(direction: str):
        if direction not in VALID_DIRECTIONS:
            raise ValueError(f"Invalid direction '{direction}'. Allowed: {VALID_DIRECTIONS}")

    @classmethod
    def create(cls, route_id: int, vehicle_id: int, driver_id: int,
               departure_time: str, arrival_time: str, time_window: str,
               status: str = "scheduled", direction: str = "inbound"):
        """Creates a schedule linking route, vehicle, driver, and direction."""
        cls.validate_status(status)
        cls.validate_direction(direction)
        if not departure_time or not arrival_time or not time_window:
            raise ValueError("departure_time, arrival_time, and time_window are required.")

        sql = """
            INSERT INTO schedules (route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, status, direction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        schedule_id = execute_query(
            sql,
            (route_id, vehicle_id, driver_id, departure_time.strip(), arrival_time.strip(), time_window.strip(), status, direction.strip()),
            fetch="insert"
        )
        return cls.get_by_id(schedule_id, detailed=True)

    @classmethod
    def get_by_id(cls, schedule_id: int, detailed: bool = True):
        """Retrieves a schedule by primary key, optionally joining Route, Vehicle, and Driver."""
        if not detailed:
            sql = "SELECT *, COALESCE(direction, 'inbound') AS direction FROM schedules WHERE schedule_id = ?"
            return execute_query(sql, (schedule_id,), fetch="one")

        sql = """
            SELECT 
                s.schedule_id,
                s.route_id,
                s.vehicle_id,
                s.driver_id,
                s.departure_time,
                s.arrival_time,
                s.time_window,
                COALESCE(s.direction, 'inbound') AS direction,
                s.status,
                s.created_at,
                r.route_name,
                r.origin,
                r.destination,
                r.distance_km,
                r.estimated_duration_mins,
                v.registration_number,
                v.model AS vehicle_model,
                v.capacity AS vehicle_capacity,
                v.availability_status AS vehicle_availability,
                d.name AS driver_name,
                d.phone AS driver_phone,
                d.license_number AS driver_license
            FROM schedules s
            JOIN routes r ON s.route_id = r.route_id
            JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            JOIN drivers d ON s.driver_id = d.driver_id
            WHERE s.schedule_id = ?
        """
        return execute_query(sql, (schedule_id,), fetch="one")

    @classmethod
    def list_all(cls, route_id: int = None, status: str = None, direction: str = None, detailed: bool = True):
        """Lists schedules with optional filters and relational join data."""
        if not detailed:
            query = "SELECT *, COALESCE(direction, 'inbound') AS direction FROM schedules WHERE 1=1"
            params = []
            if route_id:
                query += " AND route_id = ?"
                params.append(route_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            if direction:
                query += " AND direction = ?"
                params.append(direction)
            query += " ORDER BY schedule_id ASC"
            return execute_query(query, tuple(params), fetch="all")

        query = """
            SELECT 
                s.schedule_id,
                s.route_id,
                s.vehicle_id,
                s.driver_id,
                s.departure_time,
                s.arrival_time,
                s.time_window,
                COALESCE(s.direction, 'inbound') AS direction,
                s.status,
                s.created_at,
                r.route_name,
                r.origin,
                r.destination,
                r.distance_km,
                r.estimated_duration_mins,
                v.registration_number,
                v.model AS vehicle_model,
                v.capacity AS vehicle_capacity,
                d.name AS driver_name,
                d.phone AS driver_phone
            FROM schedules s
            JOIN routes r ON s.route_id = r.route_id
            JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            JOIN drivers d ON s.driver_id = d.driver_id
            WHERE 1=1
        """
        params = []
        if route_id:
            query += " AND s.route_id = ?"
            params.append(route_id)
        if status:
            query += " AND s.status = ?"
            params.append(status)
        if direction:
            query += " AND s.direction = ?"
            params.append(direction)
        query += " ORDER BY s.schedule_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def update(cls, schedule_id: int, **kwargs):
        """Updates schedule status, direction, or assignments."""
        existing = cls.get_by_id(schedule_id, detailed=False)
        if not existing:
            return None

        if "status" in kwargs:
            cls.validate_status(kwargs["status"])
        if "direction" in kwargs:
            cls.validate_direction(kwargs["direction"])

        allowed = ["route_id", "vehicle_id", "driver_id", "departure_time", "arrival_time", "time_window", "status", "direction"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                params.append(value)

        if not updates:
            return cls.get_by_id(schedule_id, detailed=True)

        params.append(schedule_id)
        sql = f"UPDATE schedules SET {', '.join(updates)} WHERE schedule_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(schedule_id, detailed=True)

    @classmethod
    def delete(cls, schedule_id: int):
        """Deletes a schedule record."""
        sql = "DELETE FROM schedules WHERE schedule_id = ?"
        rows_affected = execute_query(sql, (schedule_id,), fetch="none")
        return rows_affected > 0
