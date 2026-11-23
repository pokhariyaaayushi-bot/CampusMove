"""
CampusMove Flask Application Factory
"""

import os
from pathlib import Path
from flask import Flask, send_from_directory, request
from backend.app.config import config_by_name
from backend.app.db import close_db, execute_query, init_db, seed_db
from backend.app.routes.vehicles import vehicles_bp
from backend.app.routes.drivers import drivers_bp
from backend.app.routes.routes import routes_bp
from backend.app.routes.schedules import schedules_bp
from backend.app.routes.auth import auth_bp
from backend.app.routes.bookings import bookings_bp
from backend.app.routes.algorithms import algorithms_bp
from backend.app.routes.notifications import notifications_bp
from backend.app.routes.seat_allocations import seat_allocations_bp
from backend.app.routes.attendance import attendance_bp

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def create_app(config_name: str = "development") -> Flask:
    """Creates and configures the Flask application."""
    app = Flask(__name__)

    # Load configuration
    cfg_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(cfg_class)

    # Register database connection teardown
    app.teardown_appcontext(close_db)

    # Apply the MySQL-first schema on application startup. It is idempotent,
    # so restarting the service never overwrites existing data.
    with app.app_context():
        init_db()
        # A first-time Docker volume has an empty schema. Populate the demo
        # accounts and transit data automatically so the documented logins
        # work immediately after `docker compose up`.
        if not app.config.get("TESTING"):
            user_count = execute_query("SELECT COUNT(*) AS count FROM users", fetch="one")
            if user_count["count"] == 0:
                seed_db()

    # Enable CORS for frontend integration
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # Register blueprints
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(algorithms_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(seat_allocations_bp)
    app.register_blueprint(attendance_bp)

    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "CampusMove API",
            "environment": config_name
        }, 200

    # Serve React Frontend UI directly from Flask root
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return {"error": "Not Found"}, 404
        if FRONTEND_DIR.exists():
            file_path = FRONTEND_DIR / path
            if path and file_path.exists() and not file_path.is_dir():
                return send_from_directory(str(FRONTEND_DIR), path)
            index_file = FRONTEND_DIR / "index.html"
            if index_file.exists():
                return send_from_directory(str(FRONTEND_DIR), "index.html")
        return {
            "status": "healthy",
            "service": "CampusMove API",
            "message": "Frontend files located in /frontend"
        }, 200

    return app

