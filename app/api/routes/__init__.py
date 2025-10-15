"""
Регистрация всех маршрутов API.
"""

from flask import Flask
from app.api.routes.auth import auth_bp
from app.api.routes.users import users_bp
from app.api.routes.admin import admin_bp


def register_routes(app: Flask):
    """Регистрация всех маршрутов."""

    # API версионирование
    api_prefix = '/api/v1'

    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(users_bp, url_prefix=f'{api_prefix}/users')
    app.register_blueprint(admin_bp, url_prefix=f'{api_prefix}/admin')
