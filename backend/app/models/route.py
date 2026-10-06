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
        """Lists all campus transit routes."""
        sql = "SELECT * FROM routes ORDER BY route_id ASC"
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
