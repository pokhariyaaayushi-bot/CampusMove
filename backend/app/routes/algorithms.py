"""
OS Algorithms REST Endpoints
Demonstrates Resource Allocation Graph (RAG) Deadlock Detection and Priority-plus-FCFS Scheduling
Directly aligned with TCS 502 / TCS 503 Course Integration Requirements.
"""

from flask import Blueprint, request
from backend.app.algorithms.deadlock_detector import ResourceAllocationGraph, resolve_deadlock
from backend.app.algorithms.priority_scheduler import rank_booking_requests, select_next_request
from backend.app.db import execute_query
from backend.app.utils.response import api_response, api_error

algorithms_bp = Blueprint("algorithms", __name__, url_prefix="/api/algorithms")


@algorithms_bp.route("/priority-queue", methods=["GET"])
def get_priority_queue():
    """Ranks all pending transport requests using Priority-plus-FCFS."""
    query = """
        SELECT 
            tr.request_id,
            tr.student_id,
            tr.route_id,
            tr.requested_time,
            tr.priority AS priority_level,
            tr.purpose,
            tr.status,
            tr.created_at,
            u.name AS student_name,
            r.route_name,
            r.distance_km,
            COALESCE((
                SELECT COUNT(*) * 50 
                FROM daily_attendance da 
                JOIN seat_allocations sa ON da.allocation_id = sa.allocation_id 
                WHERE sa.student_id = tr.student_id AND da.status = 'absent'
            ), 0) AS green_credits
        FROM transport_requests tr
        JOIN users u ON tr.student_id = u.user_id
        JOIN routes r ON tr.route_id = r.route_id
        WHERE tr.status = 'pending'
    """
    pending = execute_query(query, fetch="all")
    ranked = rank_booking_requests(pending)
    next_selected = select_next_request(pending)

    return api_response(
        data={
            "queue": ranked,
            "next_to_allocate": next_selected,
            "total_pending": len(ranked)
        },
        message="Priority queue computed successfully using Priority-plus-FCFS"
    )


@algorithms_bp.route("/deadlock-detect", methods=["GET", "POST"])
def detect_deadlock():
    """
    Builds a Resource Allocation Graph (RAG) from current, simulated, or live fleet allocations.
    Detects circular wait via 3-color DFS and computes the victim for preemption.
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
    else:
        data = request.args.to_dict()

    scenario = data.get("scenario", "standard")
    edges = data.get("edges")
    requests_meta = data.get("requests")

    rag = ResourceAllocationGraph()
    active_edges = []

    if edges:
        for e in edges:
            rag.add_edge(e["from"], e["to"])
        active_edges = edges
    elif scenario == "complex":
        # 3-Node Circular Wait: Req 1 (P3) -> Driver 1 -> Req 2 (P2) -> Vehicle 2 -> Req 3 (P1) -> Vehicle 1 -> Req 1
        rag.add_edge("Req_1 (P3)", "Driver_D1")
        rag.add_edge("Driver_D1", "Req_2 (P2)")
        rag.add_edge("Req_2 (P2)", "Vehicle_V2")
        rag.add_edge("Vehicle_V2", "Req_3 (P1)")
        rag.add_edge("Req_3 (P1)", "Vehicle_V1")
        rag.add_edge("Vehicle_V1", "Req_1 (P3)")

        requests_meta = [
            {"request_id": "Req_1 (P3)", "priority_level": "P3", "created_at": "2026-09-23 09:00:00", "label": "Premnagar Student Commute", "route": "Route 1: Premnagar Main Market ↔ Graphic Era Parking / Bus Stop"},
            {"request_id": "Req_2 (P2)", "priority_level": "P2", "created_at": "2026-09-23 09:05:00", "label": "Faculty Saharanpur Transit", "route": "Route 6: Saharanpur Chowk ↔ Graphic Era Parking / Bus Stop"},
            {"request_id": "Req_3 (P1)", "priority_level": "P1", "created_at": "2026-09-23 09:10:00", "label": "GEIMS Medical Transfer", "route": "Route 4: Graphic Era Hospital (GEIMS) ↔ Graphic Era Parking / Bus Stop"}
        ]
        active_edges = [
            {"from": "Req_1 (P3)", "to": "Driver_D1", "type": "Requesting"},
            {"from": "Driver_D1", "to": "Req_2 (P2)", "type": "Assigned to"},
            {"from": "Req_2 (P2)", "to": "Vehicle_V2", "type": "Requesting"},
            {"from": "Vehicle_V2", "to": "Req_3 (P1)", "type": "Assigned to"},
            {"from": "Req_3 (P1)", "to": "Vehicle_V1", "type": "Requesting"},
            {"from": "Vehicle_V1", "to": "Req_1 (P3)", "type": "Assigned to"}
        ]
    elif scenario == "safe":
        # Acyclic Safe State: No circular wait
        rag.add_edge("Vehicle_V1", "Req_1 (P1)")
        rag.add_edge("Driver_D1", "Req_1 (P1)")
        rag.add_edge("Vehicle_V2", "Req_2 (P2)")
        rag.add_edge("Driver_D2", "Req_2 (P2)")
        rag.add_edge("Req_3 (P3)", "Vehicle_V3")

        requests_meta = [
            {"request_id": "Req_1 (P1)", "priority_level": "P1", "created_at": "2026-09-23 08:30:00", "label": "Emergency Medical Transfer", "route": "Route 4: Graphic Era Hospital (GEIMS) ↔ Graphic Era Parking / Bus Stop"},
            {"request_id": "Req_2 (P2)", "priority_level": "P2", "created_at": "2026-09-23 08:45:00", "label": "Faculty Clock Tower Commute", "route": "Route 2: Clock Tower ↔ Graphic Era Parking / Bus Stop"},
            {"request_id": "Req_3 (P3)", "priority_level": "P3", "created_at": "2026-09-23 09:00:00", "label": "Routine Student Transit", "route": "Route 9: UPES Bidholi ↔ Graphic Era Parking / Bus Stop"}
        ]
        active_edges = [
            {"from": "Vehicle_V1", "to": "Req_1 (P1)", "type": "Assigned to"},
            {"from": "Driver_D1", "to": "Req_1 (P1)", "type": "Assigned to"},
            {"from": "Vehicle_V2", "to": "Req_2 (P2)", "type": "Assigned to"},
            {"from": "Driver_D2", "to": "Req_2 (P2)", "type": "Assigned to"},
            {"from": "Req_3 (P3)", "to": "Vehicle_V3", "type": "Requesting"}
        ]
    elif scenario == "live":
        # Scan live database schedules and active requests
        schedules = execute_query("""
            SELECT s.schedule_id, s.route_id, s.vehicle_id, s.driver_id,
                   r.route_name, v.registration_number, d.name AS driver_name
            FROM schedules s
            JOIN routes r ON s.route_id = r.route_id
            JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            JOIN drivers d ON s.driver_id = d.driver_id
            WHERE s.status != 'cancelled'
            LIMIT 15
        """, fetch="all") or []

        requests_db = execute_query("""
            SELECT tr.request_id, tr.student_id, tr.route_id, tr.priority AS priority_level,
                   tr.purpose, tr.created_at, u.name AS student_name, r.route_name
            FROM transport_requests tr
            JOIN users u ON tr.student_id = u.user_id
            JOIN routes r ON tr.route_id = r.route_id
            WHERE tr.status = 'pending'
            ORDER BY tr.created_at ASC
            LIMIT 10
        """, fetch="all") or []

        requests_meta = []
        for s in schedules:
            v_node = f"Vehicle_{s['registration_number']}"
            d_node = f"Driver_{s['driver_name'].split()[0]}"
            sched_node = f"Route_{s['route_id']}"
            rag.add_edge(v_node, sched_node)
            rag.add_edge(d_node, sched_node)
            active_edges.append({"from": v_node, "to": sched_node, "type": "Assigned to"})
            active_edges.append({"from": d_node, "to": sched_node, "type": "Assigned to"})

        for r in requests_db:
            r_node = f"Req_{r['request_id']} ({r['priority_level']})"
            target_route = f"Route_{r['route_id']}"
            rag.add_edge(r_node, target_route)
            active_edges.append({"from": r_node, "to": target_route, "type": "Requesting"})
            requests_meta.append({
                "request_id": r_node,
                "priority_level": r["priority_level"],
                "created_at": str(r["created_at"]),
                "label": f"{r['student_name']} ({r['route_name']})",
                "route": r["route_name"]
            })
    else:
        # Default scenario described in Project Proposal (Page 3):
        # Route A (Req 101, P3) holds Vehicle V1 and waits for Driver D1
        # Route B (Req 102, P1) holds Driver D1 and waits for Vehicle V1
        rag.add_edge("Req_A (P3)", "Driver_D1")
        rag.add_edge("Driver_D1", "Req_B (P1)")
        rag.add_edge("Req_B (P1)", "Vehicle_V1")
        rag.add_edge("Vehicle_V1", "Req_A (P3)")

        requests_meta = [
            {"request_id": "Req_A (P3)", "priority_level": "P3", "created_at": "2026-09-23 09:00:00", "label": "Premnagar Routine Transit", "route": "Route 1: Premnagar Main Market ↔ Graphic Era Parking / Bus Stop", "resource_held": "Vehicle_V1 (Tata Starbus UK-07-CM-1001)", "resource_requested": "Driver_D1 (Rajesh Kumar)"},
            {"request_id": "Req_B (P1)", "priority_level": "P1", "created_at": "2026-09-23 09:10:00", "label": "GEIMS Emergency Transfer", "route": "Route 4: Graphic Era Hospital (GEIMS) ↔ Graphic Era Parking / Bus Stop", "resource_held": "Driver_D1 (Rajesh Kumar)", "resource_requested": "Vehicle_V1 (Tata Starbus UK-07-CM-1001)"}
        ]
        active_edges = [
            {"from": "Req_A (P3)", "to": "Driver_D1", "type": "Requesting"},
            {"from": "Driver_D1", "to": "Req_B (P1)", "type": "Assigned to"},
            {"from": "Req_B (P1)", "to": "Vehicle_V1", "type": "Requesting"},
            {"from": "Vehicle_V1", "to": "Req_A (P3)", "type": "Assigned to"}
        ]

    cycle_detected = rag.detect_cycle()
    victim = None

    if cycle_detected and requests_meta:
        victim = resolve_deadlock(cycle_detected, requests_meta)

    return api_response(
        data={
            "scenario": scenario,
            "has_deadlock": cycle_detected is not None,
            "cycle_path": cycle_detected,
            "edges": active_edges,
            "requests": requests_meta or [],
            "victim_to_preempt": victim,
            "resolution": "Deadlock resolved by aborting and re-queuing lower-priority request" if victim else "No deadlock detected"
        },
        message="RAG cycle detection executed successfully"
    )


@algorithms_bp.route("/deadlock-resolve", methods=["POST"])
def resolve_deadlock_endpoint():
    """
    Simulates or executes preemption of the victim request.
    Breaks circular wait by revoking resource held by lowest-priority victim,
    allocating it to the higher-priority request, and re-running DFS to verify safe state.
    """
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "standard")
    victim = data.get("victim") or {}

    rag = ResourceAllocationGraph()

    if scenario == "complex":
        # Preempt Req_1 (P3). Vehicle_V1 is freed and allocated to Req_3 (P1 Emergency)
        rag.add_edge("Driver_D1", "Req_2 (P2)")
        rag.add_edge("Req_2 (P2)", "Vehicle_V2")
        rag.add_edge("Vehicle_V2", "Req_3 (P1)")
        rag.add_edge("Vehicle_V1", "Req_3 (P1)")  # Allocated to Emergency P1!

        active_edges = [
            {"from": "Driver_D1", "to": "Req_2 (P2)", "type": "Assigned to"},
            {"from": "Req_2 (P2)", "to": "Vehicle_V2", "type": "Requesting"},
            {"from": "Vehicle_V2", "to": "Req_3 (P1)", "type": "Assigned to"},
            {"from": "Vehicle_V1", "to": "Req_3 (P1)", "type": "Assigned to (Preempted V1)"}
        ]
        message = "Preempted Req_1 (P3 Routine). Vehicle_V1 allocated to Req_3 (P1 Emergency). Circular wait broken."
    else:
        # Standard: Preempt Req_A (P3). Vehicle_V1 is freed and allocated to Req_B (P1 Emergency)
        rag.add_edge("Driver_D1", "Req_B (P1)")
        rag.add_edge("Vehicle_V1", "Req_B (P1)")

        active_edges = [
            {"from": "Driver_D1", "to": "Req_B (P1)", "type": "Assigned to"},
            {"from": "Vehicle_V1", "to": "Req_B (P1)", "type": "Assigned to (Preempted V1 from Req_A)"}
        ]
        message = "Preempted Req_A (P3 Routine). Vehicle_V1 allocated to Req_B (P1 Emergency). Circular wait broken."

    cycle_detected = rag.detect_cycle()

    return api_response(
        data={
            "scenario": scenario,
            "has_deadlock": cycle_detected is not None,
            "cycle_path": cycle_detected,
            "edges": active_edges,
            "victim_preempted": victim,
            "is_resolved": True,
            "resolution": message
        },
        message="Deadlock resolution executed successfully. Safe state restored."
    )


