from __future__ import annotations

from flask import jsonify


def success(payload: object, status_code: int = 200):
    return jsonify({"data": payload}), status_code


def error(code: str, message: str, status_code: int):
    return jsonify({"error": {"code": code, "message": message}}), status_code
