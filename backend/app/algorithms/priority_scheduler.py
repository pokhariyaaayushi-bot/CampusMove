from typing import List, Dict, Any, Optional


PRIORITY_WEIGHTS = {
    "P1": 1,  # Emergency / Medical (Highest)
    "P2": 2,  # Official Duty / Faculty
    "P3": 3   # Routine Student Commute (Standard)
}


def rank_booking_requests(
    requests: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    if not requests:
        return []

    return sorted(
        requests,
        key=lambda req: (
            PRIORITY_WEIGHTS.get(
                req.get("priority_level", "P3"),
                99
            ),
            req.get("created_at", "")
        )
    )


def select_next_request(
    requests: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    ranked = rank_booking_requests(requests)
    return ranked[0] if ranked else None