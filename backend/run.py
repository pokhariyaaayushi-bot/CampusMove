"""
CampusMove Backend Server Runner
"""

import os
import sys
from pathlib import Path

# Ensure root workspace is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.app import create_app
from backend.app.db import init_db

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # line 23‑24 in run.py
    host = os.getenv("HOST", "0.0.0.0")   # <-- change here
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting CampusMove Server at http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
