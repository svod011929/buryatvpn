"""
Главный модуль веб-API.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import asyncio

from config.settings import settings
from config.logging import api_logger
from app.api.routes import register_routes
from app.api.middleware import setup_middleware
from app.core.monitoring import get_metrics, health_checker
from app.core.exceptions import BuryatVPNException


def create_app() -> Flask:
    """Создание Flask приложения."""
    app = Flask(__name__)

    # Конфигурация
    app.config['SECRET_KEY'] = settings.security.secret_key
    app.config['DEBUG'] = settings.web.debug

    # CORS для API
    CORS(app, origins=["*"])  # В продакшене ограничить origins

    # Безопасность
    Talisman(app, force_https=not settings.web.debug)

    # Rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["1000 per hour", "100 per minute"]
    )

    # Middleware
    setup_middleware(app)

    # Маршруты
    register_routes(app)

    # Обработчик ошибок
    @app.errorhandler(BuryatVPNException)
    def handle_custom_exception(e):
        return jsonify({
            'error': e.message,
            'code': e.code
        }), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        api_logger.error(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    # Health check
    @app.route('/health')
    async def health_check():
        try:
            health_status = await health_checker.check_health()
            status_code = 200 if health_status['healthy'] else 503
            return jsonify(health_status), status_code
        except Exception as e:
            api_logger.error(f"Health check error: {e}")
            return jsonify({'healthy': False, 'error': str(e)}), 503

    # Metrics endpoint
    @app.route('/metrics')
    def metrics():
        return get_metrics(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

    api_logger.info("Flask app created")
    return app


async def start_web_server():
    """Запуск веб-сервера."""
    app = create_app()

    try:
        api_logger.info(f"Starting web server on {settings.web.host}:{settings.web.port}")

        # Запуск в production режиме требует WSGI сервер (gunicorn, waitress)
        if settings.web.debug:
            app.run(
                host=settings.web.host,
                port=settings.web.port,
                debug=True,
                threaded=True
            )
        else:
            # Для продакшена используйте gunicorn или другой WSGI сервер
            from waitress import serve
            serve(
                app,
                host=settings.web.host,
                port=settings.web.port,
                threads=4
            )

    except Exception as e:
        api_logger.error(f"Failed to start web server: {e}")
        raise
