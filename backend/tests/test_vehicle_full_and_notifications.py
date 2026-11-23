
import pytest

from backend.app.models.vehicle import VehicleModel


def test_valid_vehicle_attributes():
    VehicleModel.validate_attributes(40)


def test_vehicle_rejects_zero_capacity():
    with pytest.raises(ValueError, match="positive integer"):
        VehicleModel.validate_attributes(0)


def test_vehicle_rejects_negative_capacity():
    with pytest.raises(ValueError, match="positive integer"):
        VehicleModel.validate_attributes(-5)


def test_vehicle_rejects_invalid_availability():
    with pytest.raises(ValueError, match="Invalid availability"):
        VehicleModel.validate_attributes(40, availability="busy")


def test_vehicle_rejects_invalid_maintenance():
    with pytest.raises(ValueError, match="Invalid maintenance"):
        VehicleModel.validate_attributes(40, maintenance="broken")


def test_vehicle_rejects_invalid_owner_type():
    with pytest.raises(ValueError, match="Invalid owner type"):
        VehicleModel.validate_attributes(40, owner_type="personal")


def test_vehicle_accepts_valid_statuses():
    VehicleModel.validate_attributes(
        40,
        availability="available",
        maintenance="good",
        owner_type="college"
    )


def test_vehicle_model_has_crud_methods():
    assert callable(VehicleModel.create)
    assert callable(VehicleModel.get_by_id)
    assert callable(VehicleModel.list_all)
    assert callable(VehicleModel.update)
    assert callable(VehicleModel.delete)
