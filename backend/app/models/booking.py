"""
Booking Domain Model & Data Access
"""

from typing import Optional, List, Dict, Any
from backend.app.db import execute_query

VALID_BOOKING_STATUS = {"pending", "confirmed", "in_route", "aborted_requeued", "cancelled", "completed"}
VALID_PRIORITY = {"P1", "P2", "P3"}


class BookingModel:

    @staticmethod
    def validate_attributes(priority_level: str = "P3", status: str = "pending"):
        """Validates booking status and priority levels."""
        if priority_level not in VALID_PRIORITY:
            raise ValueError(f"Invalid priority level '{priority_level}'. Allowed: {VALID_PRIORITY}")
        if status not in VALID_BOOKING_STATUS:
            raise ValueError(f"Invalid booking status '{status}'. Allowed: {VALID_BOOKING_STATUS}")

    @classmethod
    def create(
        cls,
        student_id: int,
        route_id: int,
        purpose: str,
        requested_date: str,
        request_id: Optional[int] = None,
        schedule_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        seat_no: Optional[int] = None,
        priority_level: str = "P3",
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Creates a new booking record with intelligent seat assignment."""
        cls.validate_attributes(priority_level, status)
        if not purpose or not requested_date:
            raise ValueError("purpose and requested_date are required fields.")

        # Auto-resolve schedule and vehicle if not provided, ensuring full vehicles are not overbooked
        if not schedule_id:
            scheds = execute_query(
                "SELECT schedule_id, vehicle_id, driver_id FROM schedules WHERE route_id = ? ORDER BY schedule_id ASC",
                (route_id,),
                fetch="all"
            ) or []

            chosen_sched = None
            for s in scheds:
                v_cap_row = execute_query("SELECT capacity FROM vehicles WHERE vehicle_id = ?", (s["vehicle_id"],), fetch="one")
                v_cap = v_cap_row["capacity"] if v_cap_row else 40
                cur_occ = execute_query(
                    """SELECT COUNT(*) as cnt FROM bookings 
                       WHERE (schedule_id = ? OR vehicle_id = ?) 
                         AND status NOT IN ('cancelled', 'aborted_requeued', 'completed')""",
                    (s["schedule_id"], s["vehicle_id"]),
                    fetch="one"
                )["cnt"]
                if cur_occ < v_cap:
                    chosen_sched = s
                    break

            if chosen_sched:
                schedule_id = chosen_sched["schedule_id"]
                if not vehicle_id:
                    vehicle_id = chosen_sched["vehicle_id"]
            else:
                # Primary vehicle on route is full! Deploy / assign secondary vehicle and alert admin
                primary_sched = scheds[0] if scheds else None
                primary_veh_id = primary_sched["vehicle_id"] if primary_sched else None

                free_veh = execute_query(
                    """SELECT * FROM vehicles 
                       WHERE availability_status = 'available' AND vehicle_id != ? 
                       ORDER BY capacity DESC LIMIT 1""",
                    (primary_veh_id or 0,),
                    fetch="one"
                )
                free_driver = execute_query(
                    "SELECT * FROM drivers WHERE availability_status = 'available' LIMIT 1",
                    fetch="one"
                )

                if free_veh and free_driver:
                    sec_sched_id = execute_query(
                        """INSERT INTO schedules (route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, status)
                           VALUES (?, ?, ?, '08:30:00', '09:00:00', 'Secondary Relief Shift', 'scheduled')""",
                        (route_id, free_veh["vehicle_id"], free_driver["driver_id"]),
                        fetch="insert"
                    )
                    schedule_id = sec_sched_id
                    vehicle_id = free_veh["vehicle_id"]
                    try:
                        # Prevent duplicate alert if unread notification exists for this vehicle
                        existing_alert = execute_query(
                            "SELECT notification_id FROM notifications WHERE type = 'vehicle_full' AND vehicle_id = ? AND is_read = 0",
                            (free_veh["vehicle_id"],),
                            fetch="one"
                        )
                        if not existing_alert:
                            r_name_row = execute_query("SELECT route_name FROM routes WHERE route_id = ?", (route_id,), fetch="one")
                            r_name = r_name_row["route_name"] if r_name_row else f"Route {route_id}"
                            execute_query(
                                """INSERT INTO notifications (type, title, message, vehicle_id, driver_id, is_read)
                                   VALUES (?, ?, ?, ?, ?, 0)""",
                                (
                                    "vehicle_full",
                                    f"🚌 Bus Full on {r_name} — Secondary Vehicle Assigned",
                                    f"Primary bus on {r_name} reached capacity. Secondary vehicle {free_veh['model']} ({free_veh['registration_number']}) with Driver {free_driver['name']} has been deployed for new bookings.",
                                    free_veh["vehicle_id"],
                                    free_driver["driver_id"]
                                ),
                                fetch="none"
                            )
                    except Exception:
                        pass
                elif free_veh:
                    vehicle_id = free_veh["vehicle_id"]
                    schedule_id = primary_sched["schedule_id"] if primary_sched else None
                    try:
                        existing_alert = execute_query(
                            "SELECT notification_id FROM notifications WHERE type = 'vehicle_full' AND vehicle_id = ? AND is_read = 0",
                            (free_veh["vehicle_id"],),
                            fetch="one"
                        )
                        if not existing_alert:
                            execute_query(
                                """INSERT INTO notifications (type, title, message, vehicle_id, is_read)
                                   VALUES (?, ?, ?, ?, 0)""",
                                (
                                    "vehicle_full",
                                    "⚠️ Bus Full — Relief Vehicle Assigned (Driver Needed)",
                                    f"Primary bus is full. Passenger assigned to secondary vehicle {free_veh['registration_number']}. Admin please assign an available driver.",
                                    free_veh["vehicle_id"]
                                ),
                                fetch="none"
                            )
                    except Exception:
                        pass
                else:
                    default_sched = execute_query(
                        "SELECT schedule_id, vehicle_id, driver_id FROM schedules LIMIT 1",
                        fetch="one"
                    )
                    if default_sched:
                        schedule_id = default_sched["schedule_id"]
                        if not vehicle_id:
                            vehicle_id = default_sched["vehicle_id"]

        if not vehicle_id and schedule_id:
            sched = execute_query(
                "SELECT vehicle_id FROM schedules WHERE schedule_id = ?",
                (schedule_id,),
                fetch="one"
            )
            if sched:
                vehicle_id = sched["vehicle_id"]

        # Three-Tier Seating Integration:
        # 1. If student already has an active Tier 1 Season Pass on this route/schedule for routine P3 commute, use their fixed seat
        recycled_attendance_id = None
        if not seat_no and priority_level == "P3":
            try:
                pass_row = execute_query(
                    """SELECT sa.seat_no, sa.allocation_id FROM seat_allocations sa
                       LEFT JOIN daily_attendance da ON sa.allocation_id = da.allocation_id AND da.date = ?
                       WHERE sa.student_id = ? AND sa.route_id = ? AND sa.status = 'active'
                         AND (da.status IS NULL OR da.status != 'absent')
                       ORDER BY sa.allocation_id DESC LIMIT 1""",
                    (requested_date.strip(), student_id, route_id),
                    fetch="one"
                )
                if pass_row and pass_row.get("seat_no"):
                    seat_no = pass_row["seat_no"]
            except Exception:
                pass

        # 2. Check for recycled Tier 1 seats released into Tier 2 dynamic pool today
        # Note: P2 priority requires front seats (1..10), so only match front recycled seats for P2
        if not seat_no and schedule_id:
            try:
                recycled_sql = """SELECT da.attendance_id, sa.seat_no
                       FROM daily_attendance da
                       JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id
                       WHERE sa.schedule_id = ? AND da.date = ? 
                         AND da.released_to_pool = 1 AND da.booked_by_student_id IS NULL"""
                if priority_level == "P2":
                    recycled_sql += " AND sa.seat_no <= 10"
                recycled_sql += " ORDER BY sa.seat_no ASC LIMIT 1"

                recycled_row = execute_query(
                    recycled_sql,
                    (schedule_id, requested_date.strip()),
                    fetch="one"
                )
                if recycled_row:
                    seat_no = recycled_row["seat_no"]
                    recycled_attendance_id = recycled_row["attendance_id"]
            except Exception:
                pass

        # 3. Priority-Based Dynamic Pool Seat Assignment
        # P2: Front priority seats 1..10 first, then upward
        # P3: Routine seats 11 upwards, overflowing to 1..10 only if back is full
        # P1: Emergency seats starting from 1
        if not seat_no:
            v_row = execute_query("SELECT capacity FROM vehicles WHERE vehicle_id = ?", (vehicle_id,), fetch="one") if vehicle_id else None
            max_cap = v_row["capacity"] if (v_row and v_row.get("capacity")) else 40

            occupied_rows = execute_query(
                """SELECT seat_no FROM bookings 
                   WHERE vehicle_id = ? 
                     AND status NOT IN ('cancelled', 'aborted_requeued', 'completed')""",
                (vehicle_id,),
                fetch="all"
            ) or []
            occupied = {r["seat_no"] for r in occupied_rows if r.get("seat_no")}

            # Active Tier 1 fixed seats that are locked (not released today)
            tier1_locked = set()
            try:
                t1_rows = execute_query(
                    """SELECT sa.seat_no 
                       FROM seat_allocations sa
                       LEFT JOIN daily_attendance da ON sa.allocation_id = da.allocation_id AND da.date = ?
                       WHERE sa.vehicle_id = ? AND sa.status = 'active'
                         AND (da.released_to_pool IS NULL OR da.released_to_pool = 0)""",
                    (requested_date.strip(), vehicle_id),
                    fetch="all"
                ) or []
                tier1_locked = {r["seat_no"] for r in t1_rows if r.get("seat_no")}
            except Exception:
                pass

            unavailable = occupied | tier1_locked

            if priority_level == "P2":
                chosen = None
                for s in range(1, max_cap + 1):
                    if s not in unavailable:
                        chosen = s
                        break
                if not chosen:
                    for s in range(1, max_cap + 1):
                        if s not in occupied:
                            chosen = s
                            break
                seat_no = chosen if chosen else ((len(occupied) % max_cap) + 1)
            elif priority_level == "P3":
                chosen = None
                for s in range(11, max_cap + 1):
                    if s not in unavailable:
                        chosen = s
                        break
                if not chosen:
                    for s in range(1, 11):
                        if s not in unavailable:
                            chosen = s
                            break
                if not chosen:
                    for s in range(11, max_cap + 1):
                        if s not in occupied:
                            chosen = s
                            break
                    if not chosen:
                        for s in range(1, 11):
                            if s not in occupied:
                                chosen = s
                                break
                seat_no = chosen if chosen else ((len(occupied) % max_cap) + 1)
            else:  # P1 emergency
                chosen = None
                for s in range(1, max_cap + 1):
                    if s not in unavailable:
                        chosen = s
                        break
                if not chosen:
                    for s in range(1, max_cap + 1):
                        if s not in occupied:
                            chosen = s
                            break
                seat_no = chosen if chosen else 1

        sql = """
            INSERT INTO bookings (request_id, student_id, route_id, schedule_id, vehicle_id, seat_no, priority_level, purpose, requested_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        booking_id = execute_query(
            sql,
            (
                request_id,
                student_id,
                route_id,
                schedule_id,
                vehicle_id,
                seat_no,
                priority_level,
                purpose.strip(),
                requested_date.strip(),
                status
            ),
            fetch="insert"
        )

        if recycled_attendance_id:
            try:
                execute_query(
                    "UPDATE daily_attendance SET booked_by_student_id = ? WHERE attendance_id = ?",
                    (student_id, recycled_attendance_id),
                    fetch="none"
                )
            except Exception:
                pass

        return cls.get_by_id(booking_id)

    @classmethod
    def get_by_id(cls, booking_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a booking with joined user, route, schedule, driver, and vehicle info."""
        sql = """
            SELECT 
                b.booking_id,
                b.request_id,
                b.student_id,
                b.route_id,
                b.schedule_id,
                b.vehicle_id,
                b.seat_no,
                b.priority_level,
                b.purpose,
                b.requested_date,
                b.status,
                b.booking_time,
                b.created_at,
                u.name AS student_name,
                u.email AS student_email,
                u.student_id AS student_roll,
                u.department AS student_department,
                r.route_name,
                r.origin,
                r.destination,
                r.distance_km,
                r.estimated_duration_mins,
                COALESCE(s.departure_time, '08:30:00') AS departure_time,
                COALESCE(s.arrival_time, '09:00:00') AS arrival_time,
                COALESCE(s.time_window, 'Morning Shift (06:30 - 12:00)') AS time_window,
                COALESCE(s.status, 'scheduled') AS schedule_status,
                COALESCE(v.registration_number, sv.registration_number, 'UK-07-CM-1001') AS vehicle_reg,
                COALESCE(v.model, sv.model, 'Tata Starbus 40-Seater') AS vehicle_model,
                COALESCE(d.name, 'Rajesh Kumar') AS driver_name,
                COALESCE(d.phone, '+91-9876543210') AS driver_phone,
                COALESCE(d.availability_status, 'available') AS driver_status,
                CASE
                    WHEN b.status = 'cancelled' THEN 'cancelled'
                    WHEN b.status IN ('in_route', 'in route', 'in-route') OR s.status = 'in_progress' OR d.availability_status = 'on_trip' THEN 'in_route'
                    WHEN b.status = 'completed' THEN 'completed'
                    WHEN s.status = 'completed' THEN 'completed'
                    ELSE 'not_started'
                END AS ride_status
            FROM bookings b
            JOIN users u ON b.student_id = u.user_id
            JOIN routes r ON b.route_id = r.route_id
            LEFT JOIN schedules s ON (
                b.schedule_id = s.schedule_id
                OR (b.schedule_id IS NULL AND s.schedule_id = (
                    SELECT s2.schedule_id FROM schedules s2 
                    WHERE s2.vehicle_id = b.vehicle_id OR s2.route_id = b.route_id 
                    ORDER BY s2.schedule_id ASC LIMIT 1
                ))
            )
            LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            LEFT JOIN vehicles sv ON s.vehicle_id = sv.vehicle_id
            LEFT JOIN drivers d ON d.driver_id = COALESCE(s.driver_id, (SELECT driver_id FROM schedules WHERE vehicle_id = b.vehicle_id LIMIT 1))
            WHERE b.booking_id = ?
        """
        return execute_query(sql, (booking_id,), fetch="one")

    @classmethod
    def list_all(
        cls,
        student_id: Optional[int] = None,
        status: Optional[str] = None,
        priority_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists bookings with joined student, route, vehicle, driver, and schedule details."""
        query = """
            SELECT 
                b.booking_id,
                b.request_id,
                b.student_id,
                b.route_id,
                b.schedule_id,
                b.vehicle_id,
                b.seat_no,
                b.priority_level,
                b.purpose,
                b.requested_date,
                b.status,
                b.booking_time,
                b.created_at,
                u.name AS student_name,
                u.email AS student_email,
                u.student_id AS student_roll,
                u.department AS student_department,
                r.route_name,
                r.origin,
                r.destination,
                r.distance_km,
                r.estimated_duration_mins,
                COALESCE(s.departure_time, '08:30:00') AS departure_time,
                COALESCE(s.arrival_time, '09:00:00') AS arrival_time,
                COALESCE(s.time_window, 'Morning Shift (06:30 - 12:00)') AS time_window,
                COALESCE(s.status, 'scheduled') AS schedule_status,
                COALESCE(v.registration_number, sv.registration_number, 'UK-07-CM-1001') AS vehicle_reg,
                COALESCE(v.model, sv.model, 'Tata Starbus 40-Seater') AS vehicle_model,
                COALESCE(d.name, 'Rajesh Kumar') AS driver_name,
                COALESCE(d.phone, '+91-9876543210') AS driver_phone,
                COALESCE(d.availability_status, 'available') AS driver_status,
                CASE
                    WHEN b.status = 'cancelled' THEN 'cancelled'
                    WHEN b.status IN ('in_route', 'in route', 'in-route') OR s.status = 'in_progress' OR d.availability_status = 'on_trip' THEN 'in_route'
                    WHEN b.status = 'completed' THEN 'completed'
                    WHEN s.status = 'completed' THEN 'completed'
                    ELSE 'not_started'
                END AS ride_status
            FROM bookings b
            JOIN users u ON b.student_id = u.user_id
            JOIN routes r ON b.route_id = r.route_id
            LEFT JOIN schedules s ON (
                b.schedule_id = s.schedule_id
                OR (b.schedule_id IS NULL AND s.schedule_id = (
                    SELECT s2.schedule_id FROM schedules s2 
                    WHERE s2.vehicle_id = b.vehicle_id OR s2.route_id = b.route_id 
                    ORDER BY s2.schedule_id ASC LIMIT 1
                ))
            )
            LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            LEFT JOIN vehicles sv ON s.vehicle_id = sv.vehicle_id
            LEFT JOIN drivers d ON d.driver_id = COALESCE(s.driver_id, (SELECT driver_id FROM schedules WHERE vehicle_id = b.vehicle_id LIMIT 1))
            WHERE 1=1
        """
        params = []
        if student_id:
            query += " AND b.student_id = ?"
            params.append(student_id)
        if status:
            if status in ("in_route", "in route", "in-route"):
                query += " AND (b.status IN ('in_route', 'in route', 'in-route') OR s.status = 'in_progress' OR d.availability_status = 'on_trip')"
            else:
                query += " AND b.status = ?"
                params.append(status)
        if priority_level:
            query += " AND b.priority_level = ?"
            params.append(priority_level)

        query += " ORDER BY b.booking_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def update(cls, booking_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Updates booking details or status."""
        existing = cls.get_by_id(booking_id)
        if not existing:
            return None

        priority = kwargs.get("priority_level", existing["priority_level"])
        status = kwargs.get("status", existing["status"])
        cls.validate_attributes(priority, status)

        allowed = ["schedule_id", "vehicle_id", "seat_no", "priority_level", "purpose", "requested_date", "status"]
        updates = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                params.append(value)

        if not updates:
            return existing

        params.append(booking_id)
        sql = f"UPDATE bookings SET {', '.join(updates)} WHERE booking_id = ?"
        execute_query(sql, tuple(params), fetch="none")
        return cls.get_by_id(booking_id)

    @classmethod
    def delete(cls, booking_id: int) -> bool:
        """Deletes a booking record."""
        sql = "DELETE FROM bookings WHERE booking_id = ?"
        rows_affected = execute_query(sql, (booking_id,), fetch="none")
        return rows_affected > 0
