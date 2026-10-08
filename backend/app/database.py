import sqlite3

from flask import current_app, g


def get_database():
    # Una conexión por petición evita compartir cursores entre solicitudes.
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
        g.database.row_factory = sqlite3.Row
    return g.database


def close_database(_error=None):
    database = g.pop("database", None)
    if database is not None:
        database.close()


def initialize_database(app):
    with app.app_context():
        database = get_database()
        # SQLite crea el archivo si aún no existe; la tabla se crea una sola vez.
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_name TEXT NOT NULL,
                document_type TEXT NOT NULL,
                document_number TEXT NOT NULL,
                request_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK (status IN ('pendiente', 'aprobada', 'rechazada'))
            )
            """
        )
        columns = {
            row["name"] for row in database.execute("PRAGMA table_info(requests)")
        }
        if "document_number" not in columns:
            # Las bases anteriores conservan sus filas y reciben un valor vacío hasta migrarse.
            database.execute(
                "ALTER TABLE requests ADD COLUMN document_number TEXT NOT NULL DEFAULT ''"
            )
        database.commit()
        app.teardown_appcontext(close_database)