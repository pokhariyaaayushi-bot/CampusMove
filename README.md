# CampusMove
Camps Move is a web-based platform designed to simplify and improve camp management by providing centralized data storage, user management, activity tracking, and efficient information retrieval. It uses a structured database and a user-friendly interface to reduce manual work and support better decision-making.

## Run with MySQL

CampusMove now uses MySQL 8 as its application database. Start the complete
stack with:

```bash
docker compose up --build
```

Open `http://127.0.0.1:5001/`. The backend waits for MySQL to become healthy,
then applies the idempotent schema in `db/schema.sql`.

To move the existing SQLite data into MySQL, run this once after the stack is
healthy:

```bash
docker compose exec backend python backend/migrate_sqlite_to_mysql.py --source /app/legacysqllitedb
```

The importer preserves IDs and skips records that are already present, making
it safe to rerun. Set `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`,
`MYSQL_ROOT_PASSWORD`, or `HOST_PORT` in a `.env` file to override the local
development defaults.

Windows users should follow the step-by-step [Windows setup guide](docs/windows-setup-guide.md).


## Project layout

- `backend/` — Flask API, MySQL data access, and automated tests.
- `frontend/` — the browser UI served by Flask.
- `db/` — MySQL schema and repeatable demo seed data.
- `docs/` — Windows setup.
- `reports/phase-3/` — the final Phase 3 PDF/source with its college logos and member images.
- `legacysqllitedb` — preserved SQLite backup for one-time migration only.
