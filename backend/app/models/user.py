from werkzeug.security import generate_password_hash, check_password_hash


class UserModel:

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        password: str,
        role: str = "student"
    ):
        cls.validate_role(role)

        if len(password) < 6:
            raise ValueError(
                "Password must be at least 6 characters long."
            )

        # Cryptographic Salt + Scrypt Hash
        password_hash = generate_password_hash(password)

        sql = """
        INSERT INTO users
        (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """

        user_id = execute_query(
            sql,
            (
                name.strip(),
                email.strip().lower(),
                password_hash,
                role
            ),
            fetch="insert"
        )

        return cls.get_by_id(user_id)