"""
Маршруты аутентификации.
"""

from flask import Blueprint, request, jsonify
from app.core.security import security_manager, rate_limiter
from app.services.user_service import UserService
from config.settings import settings
from config.logging import api_logger

auth_bp = Blueprint('auth', __name__)
user_service = UserService()


@auth_bp.route('/login', methods=['POST'])
async def login():
    """Аутентификация администратора."""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        email = data['email']
        password = data['password']

        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if rate_limiter.is_blocked(client_ip):
            return jsonify({'error': 'Too many attempts. Try later'}), 429

        # Проверка учетных данных
        if (email == settings.web.admin_email and 
            security_manager.verify_password(password, settings.web.admin_password_hash)):

            # Создание JWT токена
            token_data = {
                'email': email,
                'role': 'admin'
            }

            access_token = security_manager.create_access_token(token_data)

            rate_limiter.record_attempt(client_ip, success=True)
            api_logger.info(f"Admin login successful: {email}")

            return jsonify({
                'access_token': access_token,
                'token_type': 'bearer',
                'expires_in': settings.security.jwt_expire_hours * 3600
            })
        else:
            rate_limiter.record_attempt(client_ip, success=False)
            api_logger.warning(f"Failed login attempt: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        api_logger.error(f"Login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500


@auth_bp.route('/verify', methods=['POST'])
async def verify_token():
    """Проверка JWT токена."""
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401

        token = auth_header.split(' ')[1]
        payload = security_manager.verify_token(token)

        return jsonify({
            'valid': True,
            'payload': payload
        })

    except Exception as e:
        return jsonify({'error': 'Invalid token', 'valid': False}), 401
