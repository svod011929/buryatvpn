"""Middleware для API."""

from flask import Flask, jsonify, request


def setup_middleware(app: Flask) -> None:
    """Регистрация middleware и базовых проверок входящих запросов."""

    @app.before_request
    def validate_json_body():
        if request.method in {"POST", "PUT", "PATCH"} and request.path.startswith("/api/"):
            if request.content_type and "application/json" in request.content_type:
                return None
            # Для auth/login, verify и других JSON-only endpoint'ов.
            if request.path.startswith("/api/v1/"):
                return jsonify({"error": "Content-Type must be application/json"}), 415

    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response
