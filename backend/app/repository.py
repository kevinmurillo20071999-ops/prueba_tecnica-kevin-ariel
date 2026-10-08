from app.database import get_database


def list_requests():
    rows = get_database().execute(
        "SELECT id, applicant_name, document_type, request_date, status "
        "FROM requests ORDER BY id DESC"
    ).fetchall()
    return [dict(row) for row in rows]


def create_request(applicant_name, document_type, request_date):
    database = get_database()
    # Los parámetros separados protegen la consulta y evitan concatenar datos del usuario.
    cursor = database.execute(
        "INSERT INTO requests (applicant_name, document_type, request_date) "
        "VALUES (?, ?, ?)",
        (applicant_name, document_type, request_date),
    )
    database.commit()
    return database.execute(
        "SELECT id, applicant_name, document_type, request_date, status "
        "FROM requests WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()


def update_status(request_id, status):
    database = get_database()
    cursor = database.execute(
        "UPDATE requests SET status = ? WHERE id = ?", (status, request_id)
    )
    database.commit()
    if cursor.rowcount == 0:
        return None
    row = database.execute(
        "SELECT id, applicant_name, document_type, request_date, status "
        "FROM requests WHERE id = ?",
        (request_id,),
    ).fetchone()
    return dict(row)