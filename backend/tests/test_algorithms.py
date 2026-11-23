"""
Algorithm Tests: Deadlock Detection (RAG) and Priority Scheduling
"""

from backend.app.algorithms.deadlock_detector import (
    ResourceAllocationGraph,
    resolve_deadlock
)
from backend.app.algorithms.priority_scheduler import (
    rank_booking_requests,
    select_next_request,
    PRIORITY_WEIGHTS
)


def test_rag_no_cycle():
    """Verifies that an acyclic resource graph does not report a deadlock."""
    rag = ResourceAllocationGraph()
    rag.add_edge("Req_1", "Res_A")
    rag.add_edge("Res_A", "Req_2")
    rag.add_edge("Req_2", "Res_B")

    cycle = rag.detect_cycle()
    assert cycle is None


def test_rag_cycle_detection():
    """Verifies that circular wait in RAG detects the exact cycle."""
    rag = ResourceAllocationGraph()
    # Req1 holds ResA, waiting for ResB
    # Req2 holds ResB, waiting for ResA
    rag.add_edge("Req_1", "Res_B")
    rag.add_edge("Res_B", "Req_2")
    rag.add_edge("Req_2", "Res_A")
    rag.add_edge("Res_A", "Req_1")

    cycle = rag.detect_cycle()
    assert cycle is not None
    assert len(cycle) >= 4
    # Ensure cycle forms a loop
    assert cycle[0] == cycle[-1]


def test_resolve_deadlock_victim_selection():
    """Verifies that resolve_deadlock picks the lowest priority and latest timestamp request as victim."""
    requests = [
        {"request_id": "Req_1", "priority_level": "P1", "created_at": "2026-09-23 09:00:00"},
        {"request_id": "Req_2", "priority_level": "P3", "created_at": "2026-09-23 09:05:00"},
        {"request_id": "Req_3", "priority_level": "P3", "created_at": "2026-09-23 09:10:00"},
    ]
    cycle_path = ["Req_1", "Res_A", "Req_2", "Res_B", "Req_3", "Res_C", "Req_1"]

    victim = resolve_deadlock(cycle_path, requests)
    assert victim is not None
    # Req_3 has lowest priority (P3) and latest timestamp (09:10:00)
    assert victim["request_id"] == "Req_3"


def test_priority_scheduler_ranking():
    """Verifies priority scheduler sorts P1 > P2 > P3 with FIFO tie-breaking."""
    requests = [
        {"request_id": 1, "priority_level": "P3", "created_at": "2026-09-23 08:30:00"},
        {"request_id": 2, "priority_level": "P1", "created_at": "2026-09-23 09:15:00"},
        {"request_id": 3, "priority_level": "P2", "created_at": "2026-09-23 09:00:00"},
        {"request_id": 4, "priority_level": "P1", "created_at": "2026-09-23 09:05:00"},
    ]

    ranked = rank_booking_requests(requests)
    ranked_ids = [r["request_id"] for r in ranked]
    # P1 (earlier first: Req 4 at 09:05, then Req 2 at 09:15), then P2 (Req 3), then P3 (Req 1)
    assert ranked_ids == [4, 2, 3, 1]

    next_req = select_next_request(requests)
    assert next_req["request_id"] == 4


def test_priority_scheduler_empty():
    """Verifies empty list handling."""
    assert rank_booking_requests([]) == []
    assert select_next_request([]) is None

