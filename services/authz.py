from functools import wraps

from flask import abort, redirect, session, url_for

from database import get_db


def _identity_row():
    user_id = session.get("user_id")
    family_id = session.get("family_id")
    if not user_id:
        return None

    with get_db() as conn:
        user = conn.execute(
            """
            SELECT id AS user_id, username, display_name, user_type
              FROM users
             WHERE id=? AND active=1
            """,
            (user_id,),
        ).fetchone()
        if not user:
            return None

        membership = None
        if family_id:
            membership = conn.execute(
                """
                SELECT id AS membership_id, family_id, member_kind
                  FROM family_memberships
                 WHERE user_id=? AND family_id=? AND status='active'
                 LIMIT 1
                """,
                (user_id, family_id),
            ).fetchone()

    identity = dict(user)
    identity.update(
        {
            "membership_id": membership["membership_id"] if membership else None,
            "family_id": membership["family_id"] if membership else family_id,
            "member_kind": membership["member_kind"] if membership else None,
        }
    )
    return identity


def is_platform_admin():
    identity = _identity_row()
    return bool(identity and identity.get("user_type") == "platform_admin")


def current_permissions():
    identity = _identity_row()
    if not identity:
        return set()

    if identity.get("user_type") == "platform_admin":
        return {"*"}

    if not identity.get("membership_id"):
        return set()

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT p.permission_key
              FROM permissions p
              JOIN role_permissions rp ON rp.permission_id=p.id
              JOIN membership_roles mr ON mr.role_id=rp.role_id
             WHERE mr.membership_id=?
            """,
            (identity["membership_id"],),
        ).fetchall()
    return {row["permission_key"] for row in rows}


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


def platform_admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("admin_login"))
        if not is_platform_admin():
            abort(403)
        return view(*args, **kwargs)

    return wrapped


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
