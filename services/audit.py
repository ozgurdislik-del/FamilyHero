import json

from flask import request, session

from database import get_db


def _safe_json(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


def audit_event(action_key, entity_type, entity_id=None, before=None, after=None):
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs(
                    family_id, actor_user_id, action_key, entity_type,
                    entity_id, before_data, after_data, request_ip
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    session.get("family_id"),
                    session.get("user_id"),
                    action_key,
                    entity_type,
                    str(entity_id) if entity_id is not None else None,
                    _safe_json(before),
                    _safe_json(after),
                    request.headers.get("X-Forwarded-For", request.remote_addr),
                ),
            )
    except Exception:
        # Audit logging must never break the user transaction path.
        return False
    return True
