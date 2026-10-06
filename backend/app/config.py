import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv("SECRET_KEY", "campusmove-dev-secret-key-2026")
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # 'sqlite' or 'mysql'

    # SQLite Settings
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "campusmove.db"))

    # MySQL Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "campusmove")

    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite and isolated environment."""
    TESTING = True
    DEBUG = True
    DB_TYPE = "sqlite"
    SQLITE_DB_PATH = ":memory:"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
