"""Маршруты работы с пользователями."""

from flask import Blueprint, jsonify, request

from app.core.security import security_manager
from app.services.user_service import UserService

users_bp = Blueprint("users", __name__)
user_service = UserService()


def _extract_token_payload():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        return security_manager.verify_token(token)
    except Exception:
        return None


@users_bp.route("", methods=["GET"])
async def list_users():
    """Список пользователей для админ-панели."""
    payload = _extract_token_payload()
    if not payload or payload.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    limit = min(max(request.args.get("limit", default=50, type=int) or 50, 1), 200)
    offset = max(request.args.get("offset", default=0, type=int) or 0, 0)
    active_only = request.args.get("active_only", default="true").lower() != "false"
    search = request.args.get("search")

    users = await user_service.get_users_list(
        limit=limit,
        offset=offset,
        search=search,
        active_only=active_only,
    )
    return jsonify({"items": users, "limit": limit, "offset": offset})


@users_bp.route("/<int:telegram_id>/ban", methods=["POST"])
async def ban_user(telegram_id: int):
    """Блокировка/разблокировка пользователя."""
    payload = _extract_token_payload()
    if not payload or payload.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    banned = bool(data.get("banned", True))
    updated = await user_service.ban_user(telegram_id, banned=banned)
    return jsonify({"telegram_id": telegram_id, "banned": banned, "updated": updated})
