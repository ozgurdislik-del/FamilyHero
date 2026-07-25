from functools import wraps

from flask import abort, redirect, session, url_for

from database import get_db


def _identity_row():
    user_id = session.get("user_id")
    family_id = session.get("family_id")
    if not user_id:
        return None
    with get_db() as conn:
        return conn.execute(
            """
            SELECT u.id AS user_id, u.username, u.display_name, u.user_type,
                   fm.id AS membership_id, fm.family_id, fm.member_kind
              FROM users u
              LEFT JOIN family_memberships fm
                ON fm.user_id=u.id AND fm.status='active'
             WHERE u.id=? AND u.active=1
               AND (? IS NULL OR fm.family_id=? OR fm.family_id IS NULL)
             ORDER BY fm.id NULLS LAST
             LIMIT 1
            """,
            (user_id, family_id, family_id),
        ).fetchone()


def current_permissions():
    identity = _identity_row()
    if not identity:
        return set()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT p.permission_key
              FROM permissions p
              JOIN role_permissions rp ON rp.permission_id=p.id
              JOIN membership_roles mr ON mr.role_id=rp.role_id
              JOIN family_memberships fm ON fm.id=mr.membership_id
             WHERE fm.user_id=? AND fm.status='active'
               AND (? IS NULL OR fm.family_id=?)
            """,
            (identity["user_id"], identity.get("family_id"), identity.get("family_id")),
        ).fetchall()
        permissions = {row["permission_key"] for row in rows}
        if identity.get("user_type") == "platform_admin":
            permissions.add("*")
        return permissions


def can(permission_key):
    permissions = current_permissions()
    return "*" in permissions or permission_key in permissions


def permission_required(permission_key, login_endpoint="admin_login"):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for(login_endpoint))
            if not can(permission_key):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def establish_identity_session(username, *, child_id=None, admin_id=None):
    with get_db() as conn:
        identity = conn.execute(
            """
            SELECT u.id AS user_id, fm.family_id
              FROM users u
              LEFT JOIN family_memberships fm
                ON fm.user_id=u.id AND fm.status='active'
             WHERE u.username=? AND u.active=1
             ORDER BY fm.id NULLS LAST
             LIMIT 1
            """,
            (username,),
        ).fetchone()
    if not identity:
        return False
    session["user_id"] = identity["user_id"]
    session["family_id"] = identity.get("family_id")
    if child_id is not None:
        session["child_id"] = child_id
    if admin_id is not None:
        session["admin_id"] = admin_id
    return True
