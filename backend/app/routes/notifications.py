"""
Notifications REST Endpoints
Handles admin notifications: vehicle full, driver leave, dispatch alerts, etc.
"""

from flask import Blueprint, request
from backend.app.db import execute_query
from backend.app.utils.response import api_response, api_error

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


def ensure_notifications_table():
    """Schema creation is centralized in ``db/schema.sql``."""
    return None


def create_notification(type_, title, message, vehicle_id=None, driver_id=None, route_id=None):
    """Helper to create a notification from other modules."""
    try:
        ensure_notifications_table()
        if not route_id and vehicle_id:
            s_row = execute_query(
                "SELECT route_id FROM schedules WHERE vehicle_id = ? AND status != 'cancelled' ORDER BY schedule_id DESC LIMIT 1",
                (vehicle_id,),
                fetch="one"
            )
            if s_row:
                route_id = s_row["route_id"]

        execute_query(
            """INSERT INTO notifications (type, title, message, vehicle_id, driver_id, route_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (type_, title, message, vehicle_id, driver_id, route_id),
            fetch="none"
        )
    except Exception as e:
        print(f"[Notification Error] Could not create notification: {e}")


@notifications_bp.route("", methods=["GET"])
def get_notifications():
    """Get all admin notifications with optional read/unread filter, enriched with route details."""
    ensure_notifications_table()
    is_read = request.args.get("is_read")
    
    # Eliminate duplicate repetitions by selecting the latest alert and joining route context
    query = """
        SELECT n.*,
               COALESCE(s.route_id, 1) AS resolved_route_id,
               COALESCE(r2.route_name, 'Campus Transit Route') AS route_name,
               COALESCE(r2.origin, 'GEU Main Gate') AS origin,
               COALESCE(r2.destination, 'Campus') AS destination,
               v.model AS vehicle_model, v.registration_number AS vehicle_reg
        FROM notifications n
        INNER JOIN (
            SELECT MAX(notification_id) AS max_id
            FROM notifications
            GROUP BY type, title, message
        ) latest ON n.notification_id = latest.max_id
        LEFT JOIN (
            SELECT vehicle_id, MAX(route_id) AS route_id
            FROM schedules
            WHERE status != 'cancelled'
            GROUP BY vehicle_id
        ) s ON n.vehicle_id = s.vehicle_id
        LEFT JOIN routes r2 ON s.route_id = r2.route_id
        LEFT JOIN vehicles v ON n.vehicle_id = v.vehicle_id
        WHERE 1=1
    """
    params = []
    if is_read is not None:
        query += " AND n.is_read = ?"
        params.append(int(is_read))
    query += " ORDER BY n.notification_id DESC LIMIT 100"
    notifs = execute_query(query, tuple(params), fetch="all") or []

    unread_row = execute_query(
        """SELECT COUNT(DISTINCT CONCAT(title, message)) as cnt
           FROM notifications WHERE is_read = 0""",
        fetch="one"
    )
    unread_count = unread_row["cnt"] if unread_row else 0

    return api_response(
        data={"notifications": notifs, "unread_count": unread_count},
        message="Notifications retrieved successfully"
    )


@notifications_bp.route("/mark-read", methods=["POST"])
def mark_all_read():
    """Mark all notifications as read."""
    ensure_notifications_table()
    execute_query("UPDATE notifications SET is_read = 1", fetch="none")
    return api_response(message="All notifications marked as read")


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
def mark_read(notification_id: int):
    """Mark a single notification as read."""
    ensure_notifications_table()
    execute_query(
        "UPDATE notifications SET is_read = 1 WHERE notification_id = ?",
        (notification_id,),
        fetch="none"
    )
    return api_response(message="Notification marked as read")


@notifications_bp.route("/<int:notification_id>/resolve-vehicle-full", methods=["POST"])
def resolve_vehicle_full(notification_id: int):
    """Admin endpoint: Assigns an unassigned standby vehicle and driver to relieve a full route."""
    data = request.get_json() or {}
    vehicle_id = data.get("vehicle_id")
    driver_id = data.get("driver_id")
    route_id = data.get("route_id")

    if not vehicle_id or not driver_id:
        return api_error(message="vehicle_id and driver_id are required", error_code="VALIDATION_ERROR", status_code=400)

    # Automatically preserve the exact same path / route from the full vehicle's schedule
    if not route_id:
        notif = execute_query(
            "SELECT vehicle_id FROM notifications WHERE notification_id = ?",
            (notification_id,),
            fetch="one"
        )
        if notif and notif.get("vehicle_id"):
            sched = execute_query(
                "SELECT route_id FROM schedules WHERE vehicle_id = ? AND status != 'cancelled' ORDER BY schedule_id DESC LIMIT 1",
                (notif["vehicle_id"],),
                fetch="one"
            )
            if sched:
                route_id = sched["route_id"]
        if not route_id:
            route_id = 1

    # Verify vehicle is not already actively assigned to a route / schedule
    active_v = execute_query(
        "SELECT schedule_id, route_id FROM schedules WHERE vehicle_id = ? AND status != 'cancelled' LIMIT 1",
        (vehicle_id,),
        fetch="one"
    )
    if active_v:
        return api_error(
            message=f"Vehicle #{vehicle_id} is already actively assigned to Route #{active_v['route_id']}. Please choose an unassigned standby vehicle.",
            error_code="VEHICLE_ALREADY_ASSIGNED",
            status_code=400
        )

    # Verify driver is not already actively assigned to a route / schedule
    active_d = execute_query(
        "SELECT schedule_id, route_id FROM schedules WHERE driver_id = ? AND status != 'cancelled' LIMIT 1",
        (driver_id,),
        fetch="one"
    )
    if active_d:
        return api_error(
            message=f"Driver #{driver_id} is already actively driving Route #{active_d['route_id']}. Please choose an unassigned standby driver.",
            error_code="DRIVER_ALREADY_ASSIGNED",
            status_code=400
        )

    sched_id = execute_query(
        """INSERT INTO schedules (route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, status)
           VALUES (?, ?, ?, '08:30:00', '09:00:00', 'Secondary Relief Shift', 'scheduled')""",
        (route_id, vehicle_id, driver_id),
        fetch="insert"
    )
    execute_query("UPDATE notifications SET is_read = 1 WHERE notification_id = ?", (notification_id,), fetch="none")

    # Update fleet statuses
    execute_query("UPDATE vehicles SET availability_status = 'in_use' WHERE vehicle_id = ?", (vehicle_id,), fetch="none")
    execute_query("UPDATE drivers SET availability_status = 'on_trip' WHERE driver_id = ?", (driver_id,), fetch="none")

    return api_response(
        data={"schedule_id": sched_id, "vehicle_id": vehicle_id, "driver_id": driver_id, "route_id": route_id},
        message="Relief vehicle and driver deployed successfully for this route!"
    )


@notifications_bp.route("", methods=["DELETE"])
def clear_all_notifications():
    """Clear all notifications (admin action)."""
    ensure_notifications_table()
    execute_query("DELETE FROM notifications WHERE is_read = 1", fetch="none")
    return api_response(message="Read notifications cleared")


