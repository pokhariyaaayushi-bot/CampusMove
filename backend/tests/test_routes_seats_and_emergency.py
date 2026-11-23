
import pytest

from backend.app.models.route import RouteModel


def test_route_valid_attributes():
    RouteModel.validate_attributes(10.5, 30)


def test_route_rejects_zero_distance():
    with pytest.raises(ValueError, match="positive number"):
        RouteModel.validate_attributes(0, 30)


def test_route_rejects_negative_distance():
    with pytest.raises(ValueError, match="positive number"):
        RouteModel.validate_attributes(-5, 30)


def test_route_rejects_zero_duration():
    with pytest.raises(ValueError, match="positive integer"):
        RouteModel.validate_attributes(10, 0)


def test_route_rejects_invalid_duration():
    with pytest.raises(ValueError, match="positive integer"):
        RouteModel.validate_attributes(10, 30.5)


def test_route_rejects_missing_route_name():
    with pytest.raises(ValueError, match="required"):
        RouteModel.create("", "Dehradun", "Mussoorie", 30, 60)


def test_route_rejects_missing_origin():
    with pytest.raises(ValueError, match="required"):
        RouteModel.create("Route A", "", "Mussoorie", 30, 60)


def test_route_rejects_missing_destination():
    with pytest.raises(ValueError, match="required"):
        RouteModel.create("Route A", "Dehradun", "", 30, 60)