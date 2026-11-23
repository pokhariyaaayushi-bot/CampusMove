"""
User Domain Model & Authentication Data Access
"""

from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app.db import execute_query

VALID_ROLES = {"student", "faculty", "admin", "driver"}


class UserModel:

    @staticmethod
    def validate_role(role: str) -> None:
        """Validates user role constraint."""
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid user role '{role}'. Allowed: {VALID_ROLES}")

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        password: str,
        role: str = "student",
        student_id: Optional[int] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a new user record with hashed password."""
        cls.validate_role(role)

        if not name or not email or not password:
            raise ValueError("Name, email, and password are required.")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        password_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (student_id, name, email, phone, department, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        user_id = execute_query(
            sql,
            (
                student_id,
                name.strip(),
                email.strip().lower(),
                phone.strip() if phone else None,
                department.strip() if department else None,
                password_hash,
                role
            ),
            fetch="insert"
        )
        return cls.get_by_id(user_id)

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a user by ID (excluding password hash)."""
        sql = """
            SELECT user_id, student_id, name, email, phone, department, role, created_at
            FROM users
            WHERE user_id = ?
        """
        return execute_query(sql, (user_id,), fetch="one")

    @classmethod
    def get_by_email(cls, email: str, include_password: bool = False) -> Optional[Dict[str, Any]]:
        """Retrieves a user by email, optionally including password hash for auth."""
        if include_password:
            sql = "SELECT * FROM users WHERE email = ?"
        else:
            sql = """
                SELECT user_id, student_id, name, email, phone, department, role, created_at
                FROM users
                WHERE email = ?
            """
        return execute_query(sql, (email.strip().lower(),), fetch="one")

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        """Verifies candidate plaintext password against stored hash."""
        return check_password_hash(stored_hash, password)

    @classmethod
    def list_all(cls, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists users with optional role filtering."""
        query = "SELECT user_id, student_id, name, email, phone, department, role, created_at FROM users WHERE 1=1"
        params = []
        if role:
            query += " AND role = ?"
            params.append(role)
        query += " ORDER BY user_id ASC"
        return execute_query(query, tuple(params), fetch="all")

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """Deletes a user record by ID."""
        sql = "DELETE FROM users WHERE user_id = ?"
        rows_affected = execute_query(sql, (user_id,), fetch="none")
        return rows_affected > 0
