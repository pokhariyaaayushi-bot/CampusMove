"""
Vehicle & Driver Domain and API Tests
Contributed by: Aayushi Pokhariya (Member 1 - Workstream A: Fleet Management)
"""

import pytest


def test_create_and_get_vehicle(client):
    """Verifies vehicle creation and retrieval via REST API."""
    payload = {
        "registration_number": "UK-07-TEST-101",
        "model": "Ashok Leyland Electric",
        "capacity": 35,
        "availability_status": "available",
        "maintenance_status": "good"
    }
    res = client.post("/api/vehicles", json=payload)
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["registration_number"] == "UK-07-TEST-101"
    assert data["capacity"] == 35

    # Retrieve by ID
    get_res = client.get(f"/api/vehicles/{data['vehicle_id']}")
    assert get_res.status_code == 200
    assert get_res.get_json()["data"]["model"] == "Ashok Leyland Electric"


def test_vehicle_validation_constraints(client):
    """Verifies that invalid capacity and statuses trigger domain validation errors."""
    # Invalid capacity <= 0
    res = client.post("/api/vehicles", json={
        "registration_number": "UK-07-BAD-01",
        "model": "Van",
        "capacity": 0
    })
    assert res.status_code == 400
    assert "capacity must be a positive integer" in res.get_json()["error"]["message"]

    # Invalid status
    res2 = client.post("/api/vehicles", json={
        "registration_number": "UK-07-BAD-02",
        "model": "Van",
        "capacity": 10,
        "availability_status": "flying"
    })
    assert res2.status_code == 400


def test_vehicle_unique_registration(client):
    """Verifies relational UNIQUE constraint on vehicle registration number."""
    payload = {
        "registration_number": "UK-07-DUP-01",
        "model": "Toyota Coaster",
        "capacity": 22
    }
    res1 = client.post("/api/vehicles", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate registration
    res2 = client.post("/api/vehicles", json=payload)
    assert res2.status_code == 409
    assert res2.get_json()["error"]["code"] == "DUPLICATE_RESOURCE"


def test_driver_crud_and_status_transitions(client):
    """Verifies driver creation, update, and deletion."""
    driver_data = {
        "name": "Kailash Joshi",
        "phone": "+91-9811223344",
        "license_number": "LIC-KJ-9988",
        "availability_status": "available"
    }
    # Create driver
    res = client.post("/api/drivers", json=driver_data)
    assert res.status_code == 201
    driver_id = res.get_json()["data"]["driver_id"]

    # Update driver status to 'on_trip'
    update_res = client.put(f"/api/drivers/{driver_id}", json={"availability_status": "on_trip"})
    assert update_res.status_code == 200
    assert update_res.get_json()["data"]["availability_status"] == "on_trip"

    # Filter drivers by status
    list_res = client.get("/api/drivers?availability_status=on_trip")
    assert list_res.status_code == 200
    assert len(list_res.get_json()["data"]) >= 1

    # Delete driver
    del_res = client.delete(f"/api/drivers/{driver_id}")
    assert del_res.status_code == 200

    # Verify not found after delete
    get_res = client.get(f"/api/drivers/{driver_id}")
    assert get_res.status_code == 404
