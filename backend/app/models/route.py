"""
Route Domain Model & Data Access

Manages campus transit routes, distances, and travel estimates.
"""

from backend.app.db import execute_query


class RouteModel:
    @staticmethod
    def validate_attributes(distance_km: float, estimated_duration_mins: int):
        if not isinstance(distance_km, (int, float)) or distance_km <= 0:
            raise ValueError("Distance must be a positive number.")
        if not isinstance(estimated_duration_mins, int) or estimated_duration_mins <= 0:
            raise ValueError("Estimated duration must be a positive integer in minutes.")

    @classmethod
    def create(cls, route_name: str, origin: str, destination: str,
               distance_km: float, estimated_duration_mins: int):
        """Creates a new campus route."""
        cls.validate_attributes(distance_km, estimated_duration_mins)
        if not route_name or not origin or not destination:
            raise ValueError("route_name, origin, and destination are required.")

        sql = """
            INSERT INTO routes (route_name, origin, destination, distance_km, estimated_duration_mins)
            VALUES (?, ?, ?, ?, ?)
        """
        route_id = execute_query(
            sql,
            (route_name.strip(), origin.strip(), destination.strip(), float(distance_km), int(estimated_duration_mins)),
            fetch="insert"
        )
        return cls.get_by_id(route_id)

    @classmethod
    def get_by_id(cls, route_id: int):
        """Retrieves a route by primary key."""
        sql = "SELECT * FROM routes WHERE route_id = ?"
        return execute_query(sql, (route_id,), fetch="one")

    @classmethod
    def get_by_name(cls, route_name: str):
        """Retrieves a route by unique route name."""
        sql = "SELECT * FROM routes WHERE route_name = ?"
        return execute_query(sql, (route_name.strip(),), fetch="one")

    @classmethod
    def list_all(cls):
        """Lists all campus transit routes with schedule, driver, and real-time seat availability."""
        sql = """
            SELECT 
                r.*,
                s.schedule_id,
                COALESCE(s.departure_time, '08:30:00') AS departure_time,
                COALESCE(s.arrival_time, '09:00:00') AS arrival_time,
                COALESCE(s.time_window, 'Standard Shift') AS time_window,
                COALESCE(s.status, 'scheduled') AS schedule_status,
                d.driver_id,
                COALESCE(d.name, 'Assigned Route Driver') AS driver_name,
                COALESCE(d.phone, '+91-9876543210') AS driver_phone,
                COALESCE(d.availability_status, 'available') AS driver_availability,
                v.vehicle_id,
                COALESCE(v.model, 'Campus Transit Shuttle') AS vehicle_model,
                COALESCE(v.registration_number, 'UK-07-CM-1001') AS vehicle_reg,
                COALESCE(v.vehicle_type, 'Bus') AS vehicle_type,
                COALESCE(v.capacity, 40) AS capacity,
                COALESCE(bk.booked_count, 0) AS full_seats,
                MAX(0, COALESCE(v.capacity, 40) - COALESCE(bk.booked_count, 0)) AS available_seats
            FROM routes r
            LEFT JOIN schedules s ON s.schedule_id = (SELECT schedule_id FROM schedules WHERE route_id = r.route_id ORDER BY schedule_id ASC LIMIT 1)
            LEFT JOIN drivers d ON s.driver_id = d.driver_id
            LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            LEFT JOIN (
                SELECT route_id, COUNT(*) AS booked_count
                FROM bookings
                WHERE status IN ('confirmed', 'pending', 'in_route')
                GROUP BY route_id
            ) bk ON r.route_id = bk.route_id
            ORDER BY r.route_id ASC
        """
        return execute_query(sql, fetch="all")

    @classmethod
    def update(cls, route_id: int, **kwargs):
        """Updates route attributes."""
        existing = cls.get_by_id(route_id)
        if not existing:
            return None

        distance = kwargs.get("distance_km", existing["distance_km"])
        duration = kwargs.get("estimated_duration_mins", existing["estimated_duration_mins"])
        cls.validate_attributes(distance, duration)

        allowed = ["route_name", "origin", "destination", "distance_km", "estimated_duration_mins"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                if key == "distance_km":
                    params.append(float(value))
                elif key == "estimated_duration_mins":
                    params.append(int(value))
                else:
                    params.append(value.strip())

        if not updates:
            return existing

        params.append(route_id)
        sql = f"UPDATE routes SET {', '.join(updates)} WHERE route_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(route_id)

    @classmethod
    def delete(cls, route_id: int):
        """Deletes a route. Cascades to associated schedules if configured."""
        sql = "DELETE FROM routes WHERE route_id = ?"
        rows_affected = execute_query(sql, (route_id,), fetch="none")
        return rows_affected > 0
