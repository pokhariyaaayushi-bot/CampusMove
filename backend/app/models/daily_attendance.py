"""
Daily Attendance & Seat Recycling Domain Model
Handles Tier 1 absence marking, dynamic seat release into Tier 2 Open Pool,
undo absence rules, digital QR check-in, and gamification points.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from backend.app.db import execute_query

VALID_ATTENDANCE_STATUS = {"present", "absent", "auto_released", "no_show"}


class DailyAttendanceModel:

    @classmethod
    def mark_absent(
        cls,
        allocation_id: int,
        query_date: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Marks a Tier 1 season pass holder as absent for query_date.
        Immediately releases their fixed seat into the Tier 2 Open Pool for peers!
        Awards commuter responsibility points.
        """
        if not query_date:
            query_date = date.today().isoformat()

        # Check allocation exists and is active
        alloc = execute_query(
            """SELECT sa.*, u.name AS student_name, r.route_name, v.model AS vehicle_model 
               FROM seat_allocations sa 
               JOIN users u ON sa.student_id = u.user_id 
               JOIN routes r ON sa.route_id = r.route_id 
               JOIN vehicles v ON sa.vehicle_id = v.vehicle_id 
               WHERE sa.allocation_id = ?""",
            (allocation_id,),
            fetch="one"
        )
        if not alloc:
            raise ValueError(f"Seat allocation #{allocation_id} not found.")
        if alloc["status"] != "active":
            raise ValueError(f"Seat allocation #{allocation_id} is currently {alloc['status']}.")

        # Check if record already exists for this date
        existing = execute_query(
            "SELECT * FROM daily_attendance WHERE allocation_id = ? AND date = ?",
            (allocation_id, query_date),
            fetch="one"
        )

        if existing:
            execute_query(
                """UPDATE daily_attendance 
                   SET status = 'absent', released_to_pool = 1, marked_at = CURRENT_TIMESTAMP
                   WHERE attendance_id = ?""",
                (existing["attendance_id"],),
                fetch="none"
            )
            attendance_id = existing["attendance_id"]
        else:
            attendance_id = execute_query(
                """INSERT INTO daily_attendance (allocation_id, date, status, marked_at, released_to_pool)
                   VALUES (?, ?, 'absent', CURRENT_TIMESTAMP, 1)""",
                (allocation_id, query_date),
                fetch="insert"
            )

        updated = execute_query(
            "SELECT * FROM daily_attendance WHERE attendance_id = ?",
            (attendance_id,),
            fetch="one"
        )

        # Broadcast push notification for commuters on this route that a Tier 1 seat was recycled
        try:
            execute_query(
                """INSERT INTO notifications (type, title, message, vehicle_id, is_read)
                   VALUES (?, ?, ?, ?, 0)""",
                (
                    "seat_recycled",
                    f"♻️ Seat Released on {alloc['route_name']}",
                    f"Fixed Seat #{alloc['seat_no']} on {alloc['route_name']} ({alloc['vehicle_model']}) was marked absent for {query_date}. It has been recycled into the Tier 2 Open Pool and is available for booking!",
                    alloc["vehicle_id"]
                ),
                fetch="none"
            )
        except Exception:
            pass

        return {
            "attendance": updated,
            "allocation": alloc,
            "message": f"Seat #{alloc['seat_no']} marked absent and successfully recycled into Tier 2 Open Pool for {query_date}.",
            "green_credits_earned": 50,
            "incentive_badge": "🌱 Responsible Transit Citizen (+50 Green Credits)"
        }

    @classmethod
    def undo_absent(
        cls,
        allocation_id: int,
        query_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reclaims the Tier 1 seat if it has not yet been booked by another student.
        """
        if not query_date:
            query_date = date.today().isoformat()

        existing = execute_query(
            "SELECT * FROM daily_attendance WHERE allocation_id = ? AND date = ?",
            (allocation_id, query_date),
            fetch="one"
        )
        if not existing:
            raise ValueError(f"No attendance record found for allocation #{allocation_id} on {query_date}.")

        if existing["status"] != "absent" and existing["status"] != "auto_released":
            raise ValueError(f"Seat is currently marked as '{existing['status']}', not absent.")

        # Check if seat has already been claimed by a Tier 2 commuter
        if existing["booked_by_student_id"]:
            claimed_user = execute_query("SELECT name FROM users WHERE user_id = ?", (existing["booked_by_student_id"],), fetch="one")
            claimed_name = claimed_user["name"] if claimed_user else f"User #{existing['booked_by_student_id']}"
            raise ValueError(
                f"Cannot reclaim seat: It has already been booked by another commuter ({claimed_name}) from the Tier 2 Open Pool for {query_date}."
            )

        execute_query(
            """UPDATE daily_attendance 
               SET status = 'present', released_to_pool = 0, marked_at = CURRENT_TIMESTAMP
               WHERE attendance_id = ?""",
            (existing["attendance_id"],),
            fetch="none"
        )

        updated = execute_query(
            "SELECT * FROM daily_attendance WHERE attendance_id = ?",
            (existing["attendance_id"],),
            fetch="one"
        )
        return {
            "attendance": updated,
            "message": f"Absence revoked successfully. Your guaranteed seat has been restored for {query_date}."
        }

    @classmethod
    def check_in(
        cls,
        allocation_id: int,
        query_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records commuter digital QR check-in on the bus."""
        if not query_date:
            query_date = date.today().isoformat()

        existing = execute_query(
            "SELECT * FROM daily_attendance WHERE allocation_id = ? AND date = ?",
            (allocation_id, query_date),
            fetch="one"
        )

        if existing:
            if existing["status"] == "absent" and existing["booked_by_student_id"]:
                raise ValueError("Cannot check in: seat was marked absent and re-booked by another passenger.")
            execute_query(
                """UPDATE daily_attendance 
                   SET status = 'present', released_to_pool = 0, marked_at = CURRENT_TIMESTAMP
                   WHERE attendance_id = ?""",
                (existing["attendance_id"],),
                fetch="none"
            )
            attendance_id = existing["attendance_id"]
        else:
            attendance_id = execute_query(
                """INSERT INTO daily_attendance (allocation_id, date, status, marked_at, released_to_pool)
                   VALUES (?, ?, 'present', CURRENT_TIMESTAMP, 0)""",
                (allocation_id, query_date),
                fetch="insert"
            )

        updated = execute_query("SELECT * FROM daily_attendance WHERE attendance_id = ?", (attendance_id,), fetch="one")
        return {
            "attendance": updated,
            "message": f"Checked in successfully for {query_date}!"
        }

    @classmethod
    def get_by_allocation(
        cls,
        allocation_id: int,
        query_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieves attendance record for a specific allocation on query_date."""
        if not query_date:
            query_date = date.today().isoformat()

        return execute_query(
            "SELECT * FROM daily_attendance WHERE allocation_id = ? AND date = ?",
            (allocation_id, query_date),
            fetch="one"
        )

    @classmethod
    def get_schedule_attendance(
        cls,
        schedule_id: int,
        query_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists attendance records for all Tier 1 season passes on a schedule for a given date."""
        if not query_date:
            query_date = date.today().isoformat()

        sql = """
            SELECT 
                sa.allocation_id,
                sa.student_id,
                sa.seat_no,
                u.name AS student_name,
                u.email AS student_email,
                u.phone AS student_phone,
                u.student_id AS student_roll,
                COALESCE(da.status, 'unrecorded') AS attendance_status,
                da.marked_at,
                da.released_to_pool,
                da.booked_by_student_id,
                bu.name AS booked_by_name
            FROM seat_allocations sa
            JOIN users u ON sa.student_id = u.user_id
            LEFT JOIN daily_attendance da ON sa.allocation_id = da.allocation_id AND da.date = ?
            LEFT JOIN users bu ON da.booked_by_student_id = bu.user_id
            WHERE sa.schedule_id = ? AND sa.status = 'active'
            ORDER BY sa.seat_no ASC
        """
        return execute_query(sql, (query_date, schedule_id), fetch="all") or []

    @classmethod
    def auto_release_unclaimed(
        cls,
        schedule_id: int,
        query_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Auto-releases un-checked-in Tier 1 seats 15 minutes before departure into the open pool.
        """
        if not query_date:
            query_date = date.today().isoformat()

        # Find allocations on schedule with NO attendance record or not marked present
        unclaimed = execute_query(
            """SELECT sa.allocation_id, sa.seat_no, sa.student_id
               FROM seat_allocations sa
               LEFT JOIN daily_attendance da ON sa.allocation_id = da.allocation_id AND da.date = ?
               WHERE sa.schedule_id = ? 
                 AND sa.status = 'active' 
                 AND (da.attendance_id IS NULL OR (da.status != 'present' AND da.released_to_pool = 0))""",
            (query_date, schedule_id),
            fetch="all"
        ) or []

        released_seats = []
        for row in unclaimed:
            alloc_id = row["allocation_id"]
            existing = execute_query(
                "SELECT attendance_id FROM daily_attendance WHERE allocation_id = ? AND date = ?",
                (alloc_id, query_date),
                fetch="one"
            )
            if existing:
                execute_query(
                    """UPDATE daily_attendance 
                       SET status = 'auto_released', released_to_pool = 1, marked_at = CURRENT_TIMESTAMP
                       WHERE attendance_id = ?""",
                    (existing["attendance_id"],),
                    fetch="none"
                )
            else:
                execute_query(
                    """INSERT INTO daily_attendance (allocation_id, date, status, marked_at, released_to_pool)
                       VALUES (?, ?, 'auto_released', CURRENT_TIMESTAMP, 1)""",
                    (alloc_id, query_date),
                    fetch="none"
                )
            released_seats.append(row["seat_no"])

        return {
            "schedule_id": schedule_id,
            "date": query_date,
            "auto_released_count": len(released_seats),
            "released_seats": released_seats,
            "message": f"Successfully auto-released {len(released_seats)} unclaimed Tier 1 seats to Tier 2 Open Pool."
        }

    @classmethod
    def auto_grab_released_seat(
        cls,
        schedule_id: int,
        query_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Auto-assigns newly released Tier 1 seats to pending waitlisted transport requests on this schedule/route,
        ranked using the enhanced priority policy (P1/P2/P3 with distance & green credit tiebreakers).
        """
        if not query_date:
            query_date = date.today().isoformat()

        sched = execute_query("SELECT route_id, vehicle_id FROM schedules WHERE schedule_id = ?", (schedule_id,), fetch="one")
        if not sched:
            raise ValueError(f"Schedule #{schedule_id} not found.")

        # Find unclaimed recycled seats on this schedule for query_date
        recycled_seats = execute_query(
            """SELECT da.attendance_id, sa.seat_no, sa.route_id, sa.schedule_id, sa.vehicle_id
               FROM daily_attendance da
               JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id
               WHERE sa.schedule_id = ? AND da.date = ? 
                 AND da.released_to_pool = 1 AND da.booked_by_student_id IS NULL
               ORDER BY sa.seat_no ASC""",
            (schedule_id, query_date),
            fetch="all"
        ) or []

        if not recycled_seats:
            return {"message": "No unclaimed recycled seats available on this schedule for today.", "assigned": []}

        # Find pending transport requests on this route
        from backend.app.algorithms.priority_scheduler import rank_booking_requests
        pending = execute_query(
            """SELECT tr.*, r.distance_km,
                      COALESCE((
                          SELECT COUNT(*) * 50 
                          FROM daily_attendance da 
                          JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id 
                          WHERE sa.student_id = tr.student_id AND da.status = 'absent'
                      ), 0) AS green_credits
               FROM transport_requests tr
               JOIN routes r ON tr.route_id = r.route_id
               WHERE tr.route_id = ? AND tr.status = 'pending'""",
            (sched["route_id"],),
            fetch="all"
        ) or []

        ranked_requests = rank_booking_requests(pending)
        assigned = []

        for seat_item in recycled_seats:
            if not ranked_requests:
                break
            req = ranked_requests.pop(0)

            from backend.app.models.booking import BookingModel
            booking = BookingModel.create(
                student_id=req["student_id"],
                route_id=req["route_id"],
                purpose=req.get("purpose") or "Auto-Grab Dynamic Transit Pass",
                requested_date=query_date,
                request_id=req["request_id"],
                schedule_id=schedule_id,
                vehicle_id=sched["vehicle_id"],
                seat_no=seat_item["seat_no"],
                priority_level=req.get("priority", "P3"),
                status="confirmed"
            )
            execute_query("UPDATE transport_requests SET status = 'allocated' WHERE request_id = ?", (req["request_id"],), fetch="none")
            assigned.append({
                "request_id": req["request_id"],
                "student_id": req["student_id"],
                "seat_no": seat_item["seat_no"],
                "booking_id": booking["booking_id"]
            })

        return {
            "schedule_id": schedule_id,
            "date": query_date,
            "assigned_count": len(assigned),
            "assigned": assigned,
            "message": f"Successfully auto-assigned {len(assigned)} released seats to pending commuter requests."
        }

