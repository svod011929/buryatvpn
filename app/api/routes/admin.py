"""Административные маршруты."""

from flask import Blueprint, jsonify, request

from app.core.security import security_manager
from app.database.connection import db_manager
from app.services.user_service import UserService

admin_bp = Blueprint("admin", __name__)
user_service = UserService()


def _is_admin_request() -> bool:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return False

    try:
        payload = security_manager.verify_token(token)
    except Exception:
        return False
    return payload.get("role") == "admin"


@admin_bp.route("/dashboard", methods=["GET"])
async def dashboard():
    """Сводная статистика для админ-панели."""
    if not _is_admin_request():
        return jsonify({"error": "Unauthorized"}), 401

    users_stats = await user_service.get_users_statistics()
    db_info = await db_manager.get_db_info()

    return jsonify(
        {
            "users": users_stats,
            "database": db_info,
        }
    )


@admin_bp.route("/backup", methods=["POST"])
async def backup():
    """Создать backup SQLite БД для простого администрирования."""
    if not _is_admin_request():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    backup_path = data.get("path")
    result_path = await db_manager.backup_database(backup_path)
    return jsonify({"status": "ok", "backup_path": result_path})
