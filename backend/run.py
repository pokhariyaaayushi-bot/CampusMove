"""
CampusMove Backend Server Runner
"""

import os
from backend.app import create_app
from backend.app.db import init_db

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"🚀 Starting CampusMove Server at http://{host}:{port}")
    app.run(host=host, port=port, debug=True)

