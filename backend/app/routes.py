from flask import Blueprint, jsonify, request

from app import services

requests_blueprint = Blueprint("requests", __name__)


# Las rutas traducen la petición HTTP a llamadas de negocio y asignan códigos HTTP.
@requests_blueprint.get("")
def list_requests():
    return jsonify(services.get_requests()), 200


@requests_blueprint.post("")
def create_request():
    payload = request.get_json(silent=True) or {}
    created, error = services.add_request(payload)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(created), 201


@requests_blueprint.patch("/<int:request_id>/status")
def update_request_status(request_id):
    payload = request.get_json(silent=True) or {}
    updated, error = services.change_status(request_id, payload)
    if error:
        status_code = 404 if error.startswith("No existe") else 400
        return jsonify({"error": error}), status_code
    return jsonify(updated), 200