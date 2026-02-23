from __future__ import annotations

from flask import Flask
from typing import Optional

from api.routes.auth import auth_blueprint
from api.routes.profile import profile_blueprint
from api.routes.telemetry import telemetry_blueprint
from api.routes.readings import readings_blueprint
from api.routes.tarot import tarot_blueprint
from api.services.service_registry import Services, build_services


def create_app(services: Optional[Services] = None) -> Flask:
    app = Flask(__name__)
    app_services = services or build_services()
    app.extensions["services"] = app_services

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(telemetry_blueprint)
    app.register_blueprint(tarot_blueprint)
    app.register_blueprint(readings_blueprint)

    @app.get("/api/python")
    def health_check() -> tuple[dict[str, str], int]:
        return {"status": "ok", "service": "flask"}, 200

    return app
