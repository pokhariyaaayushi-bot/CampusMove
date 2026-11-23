
import pytest

from backend.app.models.user import UserModel


def test_user_model_has_create_method():
    assert callable(UserModel.create)


def test_user_create_rejects_short_password():
    with pytest.raises(ValueError, match="at least 6 characters"):
        UserModel.create(
            name="Test Student",
            email="student@example.com",
            password="123"
        )


def test_user_create_checks_role_before_password():
    with pytest.raises(AttributeError):
        UserModel.create(
            name="Test Student",
            email="student@example.com",
            password="password123",
            role="student"
        )