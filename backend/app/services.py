from datetime import date

from app import repository

ALLOWED_STATUSES = {"pendiente", "aprobada", "rechazada"}


def get_requests():
    return repository.list_requests()


def add_request(payload):
    # Aquí se valida la entrada antes de permitir que llegue a la base de datos.
    fields = ("applicant_name", "document_type", "request_date")
    values = {field: payload.get(field, "") for field in fields}

    # Normalizamos espacios antes de validar para no aceptar valores "vacíos".
    values = {field: value.strip() if isinstance(value, str) else "" for field, value in values.items()}
    if not all(values.values()):
        return None, "Todos los campos son obligatorios."

    try:
        date.fromisoformat(values["request_date"])
    except ValueError:
        return None, "La fecha debe tener un formato válido (AAAA-MM-DD)."

    request = repository.create_request(**values)
    return dict(request), None


def change_status(request_id, payload):
    # La lista permitida evita guardar estados arbitrarios enviados por el cliente.
    status = payload.get("status")
    if status not in ALLOWED_STATUSES:
        return None, "El estado debe ser pendiente, aprobada o rechazada."

    request = repository.update_status(request_id, status)
    if request is None:
        return None, "No existe una solicitud con ese identificador."
    return request, None