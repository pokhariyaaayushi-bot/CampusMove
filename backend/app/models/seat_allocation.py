
"""
Seat Allocation Domain Model (Three-Tier Seating Architecture)
Manages Tier 1 fixed season-pass allocations, validation rules, and tier availability telemetry.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from backend.app.db import execute_query

VALID_ALLOCATION_STATUS = {"active", "suspended", "expired"}


class SeatAllocationModel:

    @staticmethod
    def validate_attributes(status: str = "active", seat_no: Optional[int] = None):
        """Validates allocation status and seat number bounds."""
        if status not in VALID_ALLOCATION_STATUS:
            raise ValueError(f"Invalid allocation status '{status}'. Allowed: {VALID_ALLOCATION_STATUS}")
        if seat_no is not None and seat_no < 1:
            raise ValueError("seat_no must be a positive integer.")

    @classmethod
    def create(
        cls,
        student_id: int,
        route_id: int,
        schedule_id: int,
        vehicle_id: int,
        seat_no: int,
        semester: str,
        valid_from: str,
        valid_until: str,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Creates a new Tier 1 fixed season-pass allocation."""
        cls.validate_attributes(status=status, seat_no=seat_no)
        if not semester or not valid_from or not valid_until:
            raise ValueError("semester, valid_from, and valid_until are required.")

        # Check vehicle capacity bounds
        v_row = execute_query("SELECT capacity, model, registration_number FROM vehicles WHERE vehicle_id = ?", (vehicle_id,), fetch="one")
        if not v_row:
            raise ValueError(f"Vehicle with id {vehicle_id} does not exist.")
        if seat_no > v_row["capacity"]:
            raise ValueError(f"Seat number {seat_no} exceeds vehicle capacity of {v_row['capacity']}.")

        # Check for seat conflict in this vehicle for this semester
        existing = execute_query(
            """SELECT allocation_id, student_id FROM seat_allocations 
               WHERE vehicle_id = ? AND seat_no = ? AND semester = ? AND status = 'active'""",
            (vehicle_id, seat_no, semester),
            fetch="one"
        )
        if existing:
            raise ValueError(f"Seat {seat_no} on this vehicle is already allocated for semester '{semester}'.")

        sql = """
            INSERT INTO seat_allocations (student_id, route_id, schedule_id, vehicle_id, seat_no, semester, status, valid_from, valid_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        allocation_id = execute_query(
            sql,
            (student_id, route_id, schedule_id, vehicle_id, seat_no, semester, status, valid_from, valid_until),
            fetch="insert"
        )
        return cls.get_by_id(allocation_id)

    @classmethod
    def get_by_id(cls, allocation_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves an allocation with joined student, route, schedule, and vehicle info."""
        sql = """
            SELECT 
                sa.allocation_id,
                sa.student_id,
                sa.route_id,
                sa.schedule_id,
                sa.vehicle_id,
                sa.seat_no,
                sa.semester,
                sa.status,
                sa.valid_from,
                sa.valid_until,
                sa.created_at,
                u.name AS student_name,
                u.email AS student_email,
                u.student_id AS student_roll,
                u.department AS student_department,
                r.route_name,
                r.origin,
                r.destination,
                s.departure_time,
                s.arrival_time,
                s.time_window,
                v.model AS vehicle_model,
                v.registration_number AS vehicle_reg,
                v.capacity AS vehicle_capacity
            FROM seat_allocations sa
            JOIN users u ON sa.student_id = u.user_id
            JOIN routes r ON sa.route_id = r.route_id
            JOIN schedules s ON sa.schedule_id = s.schedule_id
            JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
            WHERE sa.allocation_id = ?
        """
        return execute_query(sql, (allocation_id,), fetch="one")

    @classmethod
    def get_all(
        cls,
        semester: Optional[str] = None,
        status: Optional[str] = None,
        route_id: Optional[int] = None,
        schedule_id: Optional[int] = None,
        vehicle_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves all allocations matching optional filters."""
        sql = """
            SELECT 
                sa.allocation_id,
                sa.student_id,
                sa.route_id,
                sa.schedule_id,
                sa.vehicle_id,
                sa.seat_no,
                sa.semester,
                sa.status,
                sa.valid_from,
                sa.valid_until,
                sa.created_at,
                u.name AS student_name,
                u.email AS student_email,
                u.student_id AS student_roll,
                u.department AS student_department,
                r.route_name,
                r.origin,
                r.destination,
                s.departure_time,
                s.arrival_time,
                s.time_window,
                v.model AS vehicle_model,
                v.registration_number AS vehicle_reg,
                v.capacity AS vehicle_capacity
            FROM seat_allocations sa
            JOIN users u ON sa.student_id = u.user_id
            JOIN routes r ON sa.route_id = r.route_id
            JOIN schedules s ON sa.schedule_id = s.schedule_id
            JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
            WHERE 1=1
        """
        params = []
        if semester:
            sql += " AND sa.semester = ?"
            params.append(semester)
        if status:
            sql += " AND sa.status = ?"
            params.append(status)
        if route_id:
            sql += " AND sa.route_id = ?"
            params.append(route_id)
        if schedule_id:
            sql += " AND sa.schedule_id = ?"
            params.append(schedule_id)
        if vehicle_id:
            sql += " AND sa.vehicle_id = ?"
            params.append(vehicle_id)

        sql += " ORDER BY sa.allocation_id DESC"
        return execute_query(sql, tuple(params), fetch="all") or []

    @classmethod
    def get_by_student(cls, student_id: int, status: str = "active") -> List[Dict[str, Any]]:
        """Retrieves active season passes for a given student."""
        sql = """
            SELECT 
                sa.allocation_id,
                sa.student_id,
                sa.route_id,
                sa.schedule_id,
                sa.vehicle_id,
                sa.seat_no,
                sa.semester,
                sa.status,
                sa.valid_from,
                sa.valid_until,
                sa.created_at,
                u.name AS student_name,
                u.email AS student_email,
                u.student_id AS student_roll,
                u.department AS student_department,
                r.route_name,
                r.origin,
                r.destination,
                s.departure_time,
                s.arrival_time,
                s.time_window,
                v.model AS vehicle_model,
                v.registration_number AS vehicle_reg,
                v.capacity AS vehicle_capacity
            FROM seat_allocations sa
            JOIN users u ON sa.student_id = u.user_id
            JOIN routes r ON sa.route_id = r.route_id
            JOIN schedules s ON sa.schedule_id = s.schedule_id
            JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
            WHERE sa.student_id = ?
        """
        params = [student_id]
        if status:
            sql += " AND sa.status = ?"
            params.append(status)
        sql += " ORDER BY sa.allocation_id DESC"
        return execute_query(sql, tuple(params), fetch="all") or []

    @classmethod
    def update_status(cls, allocation_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Updates allocation status (e.g., active, suspended, expired)."""
        cls.validate_attributes(status=status)
        execute_query("UPDATE seat_allocations SET status = ? WHERE allocation_id = ?", (status, allocation_id), fetch="none")
        return cls.get_by_id(allocation_id)

    @classmethod
    def delete(cls, allocation_id: int) -> bool:
        """Revokes an allocation."""
        deleted = execute_query("DELETE FROM seat_allocations WHERE allocation_id = ?", (allocation_id,), fetch="none")
        return deleted > 0

    @classmethod
    def get_tier_breakdown(cls, schedule_id: int, query_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates full three-tier capacity and real-time seat availability for a schedule:
          - Tier 1: Fixed Season-Pass Seats (~75% capacity, guaranteed daily)
          - Tier 2: Open Dynamic Pool (~19% capacity + dynamically recycled Tier 1 absent seats)
          - Tier 3: Emergency Reserve Buffer (~5 seats, admin-only release)
        """
        if not query_date:
            query_date = date.today().isoformat()

        sched = execute_query(
            """SELECT s.schedule_id, s.route_id, s.vehicle_id, s.departure_time, s.arrival_time, s.time_window,
                      r.route_name, r.origin, r.destination,
                      v.model AS vehicle_model, v.registration_number AS vehicle_reg, v.capacity
               FROM schedules s
               JOIN routes r ON s.route_id = r.route_id
               JOIN vehicles v ON s.vehicle_id = v.vehicle_id
               WHERE s.schedule_id = ?""",
            (schedule_id,),
            fetch="one"
        )
        if not sched:
            raise ValueError(f"Schedule #{schedule_id} not found.")

        capacity = sched["capacity"]
        # Standard default split for capacity:
        # Tier 3 (Emergency Reserve): 5 seats (or 2 seats if bus capacity <= 15)
        tier3_reserve_nominal = 5 if capacity >= 20 else max(1, capacity // 5)
        # Tier 1 (Fixed Seats): ~75% of remaining or capacity
        tier1_fixed_nominal = max(1, int(capacity * 0.75))
        # Tier 2 (Open Pool): balance
        tier2_pool_nominal = max(0, capacity - tier1_fixed_nominal - tier3_reserve_nominal)

        # 1. Active Tier 1 allocations
        allocations = execute_query(
            """SELECT sa.allocation_id, sa.seat_no, sa.student_id, u.name AS student_name
               FROM seat_allocations sa
               JOIN users u ON sa.student_id = u.user_id
               WHERE sa.schedule_id = ? AND sa.status = 'active'
               ORDER BY sa.seat_no ASC""",
            (schedule_id,),
            fetch="all"
        ) or []
        tier1_allocated_count = len(allocations)
        tier1_allocated_seats = [a["seat_no"] for a in allocations]

        # 2. Daily attendance for these allocations on query_date
        attendance_rows = execute_query(
            """SELECT da.attendance_id, da.allocation_id, da.status, da.released_to_pool, 
                      da.booked_by_student_id, sa.seat_no
               FROM daily_attendance da
               JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id
               WHERE sa.schedule_id = ? AND da.date = ?""",
            (schedule_id, query_date),
            fetch="all"
        ) or []

        absent_alloc_ids = {a["allocation_id"] for a in attendance_rows if a["status"] in ("absent", "auto_released") and a["released_to_pool"] == 1}
        recycled_seats = [a["seat_no"] for a in attendance_rows if a["allocation_id"] in absent_alloc_ids]
        recycled_claimed = [a["seat_no"] for a in attendance_rows if a["allocation_id"] in absent_alloc_ids and a["booked_by_student_id"] is not None]

        tier1_present_count = tier1_allocated_count - len(absent_alloc_ids)
        tier1_recycled_available_count = len(absent_alloc_ids) - len(recycled_claimed)

        # 3. Emergency seats released to pool for this schedule on this date
        # (Tracked via notifications or daily_attendance table or emergency releases)
        emergency_released_count = 0

        # 4. Bookings on this schedule for query_date
        booking_rows = execute_query(
            """SELECT booking_id, seat_no, priority_level, student_id, status 
               FROM bookings 
               WHERE (schedule_id = ? OR vehicle_id = ?) 
                 AND requested_date = ? 
                 AND status NOT IN ('cancelled', 'aborted_requeued', 'completed')""",
            (schedule_id, sched["vehicle_id"], query_date),
            fetch="all"
        ) or []
        tier2_booked_count = len(booking_rows)

        # Effective Tier 2 pool capacity = Nominal Tier 2 + recycled seats + emergency released
        tier2_effective_capacity = tier2_pool_nominal + len(absent_alloc_ids) + emergency_released_count
        tier2_available_count = max(0, tier2_effective_capacity - tier2_booked_count)

        # Locked emergency seats
        tier3_emergency_buffer = max(0, tier3_reserve_nominal - emergency_released_count)

        return {
            "schedule_id": schedule_id,
            "route_id": sched["route_id"],
            "route_name": sched["route_name"],
            "vehicle_id": sched["vehicle_id"],
            "vehicle_model": sched["vehicle_model"],
            "vehicle_reg": sched["vehicle_reg"],
            "capacity": capacity,
            "date": query_date,
            "tier1_fixed": {
                "nominal_capacity": tier1_fixed_nominal,
                "allocated_count": tier1_allocated_count,
                "present_count": tier1_present_count,
                "absent_recycled_count": len(absent_alloc_ids),
                "allocated_seats": tier1_allocated_seats,
                "recycled_seats": recycled_seats,
                "recycled_claimed_seats": recycled_claimed,
            },
            "tier2_open_pool": {
                "nominal_capacity": tier2_pool_nominal,
                "recycled_added": len(absent_alloc_ids),
                "emergency_released_added": emergency_released_count,
                "effective_capacity": tier2_effective_capacity,
                "booked_count": tier2_booked_count,
                "available_count": tier2_available_count
            },
            "tier3_emergency": {
                "nominal_capacity": tier3_reserve_nominal,
                "released_count": emergency_released_count,
                "locked_buffer": tier3_emergency_buffer
            },
            "total_available_seats": tier2_available_count
        }
