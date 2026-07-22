from collections import OrderedDict
from datetime import date, datetime
from functools import wraps
import os
import re
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from database import AVATARS, GOAL_SEEDS, SEED_DATA, copy_template, get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FAMILYHERO_SECRET_KEY", "familyhero-local-key")
init_db()


def child_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "child_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


def current_child():
    with get_db() as conn:
        return conn.execute("SELECT * FROM children WHERE id=?", (session.get("child_id"),)).fetchone()


@app.route("/home")
def home():
    if session.get("admin_id"):
        return redirect(url_for("admin_panel"))
    if session.get("child_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("child_id"):
        return redirect(url_for("dashboard"))
    with get_db() as conn:
        children = conn.execute("SELECT child_key,name,avatar_key FROM children ORDER BY id").fetchall()
    if request.method == "POST":
        key = request.form.get("child_key", "").lower().strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            child = conn.execute("SELECT * FROM children WHERE child_key=?", (key,)).fetchone()
        if not child or not check_password_hash(child["password_hash"], password):
            flash("İsim veya şifre hatalı.", "error")
            return render_template("login.html", children=children, avatars=AVATARS), 401
        session.clear()
        session.update(child_id=child["id"], child_name=child["name"])
        return redirect(url_for("dashboard"))
    return render_template("login.html", children=children, avatars=AVATARS)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@child_login_required
def dashboard():
    child = current_child()
    today = date.today().isoformat()
    with get_db() as conn:
        tasks = conn.execute(
            """SELECT t.*, CASE WHEN cp.id IS NULL THEN 0 ELSE 1 END done
               FROM tasks t LEFT JOIN completions cp
               ON cp.task_id=t.id AND cp.completion_date=?
               WHERE t.child_id=? AND t.active=1 ORDER BY t.sort_order,t.id""",
            (today, child["id"]),
        ).fetchall()
        today_score = conn.execute(
            "SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=? AND cp.completion_date=?",
            (child["id"], today),
        ).fetchone()[0]
        task_total = conn.execute(
            "SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?",
            (child["id"],),
        ).fetchone()[0]
        goal_bonus = conn.execute(
            """SELECT COALESCE(SUM(g.bonus_points),0) FROM goals g JOIN goal_progress gp ON gp.goal_id=g.id
               WHERE g.child_id=? AND gp.completed_date IS NOT NULL""", (child["id"],)
        ).fetchone()[0]
        goals = conn.execute(
            """SELECT g.*,COALESCE(gp.current_value,0) current_value,gp.completed_date
               FROM goals g LEFT JOIN goal_progress gp ON gp.goal_id=g.id
               WHERE g.child_id=? AND g.active=1 ORDER BY g.sort_order,g.id LIMIT 4""", (child["id"],)
        ).fetchall()
        last_reward = conn.execute(
            """SELECT COALESCE(r.description,rg.description) description,rg.grant_date
               FROM reward_grants rg LEFT JOIN rewards r ON r.id=rg.reward_id
               WHERE rg.child_id=? ORDER BY rg.grant_date DESC,rg.id DESC LIMIT 1""", (child["id"],)
        ).fetchone()
    task_count=len(tasks); done_count=sum(1 for t in tasks if t["done"])
    completion_percent=round(done_count*100/task_count) if task_count else 0
    total_score=task_total+goal_bonus
    return render_template("child_dashboard.html", child=child, avatars=AVATARS, today=today,
        today_score=today_score,total_score=total_score,task_count=task_count,done_count=done_count,
        completion_percent=completion_percent,goals=goals,last_reward=last_reward)


@app.route("/tasks")
@child_login_required
def child_tasks():
    child = current_child(); today=date.today().isoformat()
    with get_db() as conn:
        tasks=conn.execute("""SELECT t.*,CASE WHEN cp.id IS NULL THEN 0 ELSE 1 END done,COALESCE(cp.note,'') note
            FROM tasks t LEFT JOIN completions cp ON cp.task_id=t.id AND cp.completion_date=?
            WHERE t.child_id=? AND t.active=1 ORDER BY t.sort_order,t.id""",(today,child["id"])).fetchall()
        today_score=conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=? AND cp.completion_date=?",(child["id"],today)).fetchone()[0]
        total_score=conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?",(child["id"],)).fetchone()[0]
    grouped=OrderedDict()
    for task in tasks: grouped.setdefault(task["category"],[]).append(task)
    task_count=len(tasks); done_count=sum(1 for t in tasks if t["done"]); completion_percent=round(done_count*100/task_count) if task_count else 0
    return render_template("child.html",child=child,grouped=grouped,today_score=today_score,total_score=total_score,today=today,avatars=AVATARS,task_count=task_count,done_count=done_count,completion_percent=completion_percent)


@app.route("/badges")
@child_login_required
def child_badges():
    child=current_child()
    with get_db() as conn:
        goals=conn.execute("""SELECT g.*,COALESCE(gp.current_value,0) current_value,gp.completed_date
            FROM goals g LEFT JOIN goal_progress gp ON gp.goal_id=g.id WHERE g.child_id=? AND g.active=1 ORDER BY g.sort_order,g.id""",(child["id"],)).fetchall()
    return render_template("child_badges.html",child=child,goals=goals,avatars=AVATARS)


@app.route("/rewards")
@child_login_required
def child_rewards():
    child=current_child()
    with get_db() as conn:
        score=conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?",(child["id"],)).fetchone()[0]
        rewards=conn.execute("SELECT * FROM rewards WHERE child_id=? ORDER BY required_points,id",(child["id"],)).fetchall()
        grants=conn.execute("""SELECT COALESCE(r.description,rg.description) description,rg.grant_date,rg.note
            FROM reward_grants rg LEFT JOIN rewards r ON r.id=rg.reward_id WHERE rg.child_id=? ORDER BY rg.grant_date DESC,rg.id DESC""",(child["id"],)).fetchall()
    return render_template("child_rewards.html",child=child,rewards=rewards,grants=grants,total_score=score,avatars=AVATARS)


@app.post("/task/<int:task_id>/save")
@child_login_required
def save_task(task_id):
    child = current_child()
    today = date.today().isoformat()
    note = request.form.get("note", "").strip()[:250]
    with get_db() as conn:
        task = conn.execute("SELECT id FROM tasks WHERE id=? AND child_id=? AND active=1", (task_id, child["id"])).fetchone()
        if not task:
            abort(404)
        conn.execute(
            "INSERT INTO completions(task_id,completion_date,note) VALUES(?,?,?) ON CONFLICT(task_id,completion_date) DO UPDATE SET note=excluded.note",
            (task_id, today, note),
        )
    return redirect(url_for("child_tasks"))


@app.post("/task/<int:task_id>/undo")
@child_login_required
def undo_task(task_id):
    child = current_child()
    today = date.today().isoformat()
    with get_db() as conn:
        if not conn.execute("SELECT id FROM tasks WHERE id=? AND child_id=?", (task_id, child["id"])).fetchone():
            abort(404)
        conn.execute("DELETE FROM completions WHERE task_id=? AND completion_date=?", (task_id, today))
    return redirect(url_for("child_tasks"))


@app.route("/profile/avatar", methods=["GET", "POST"])
@child_login_required
def choose_avatar():
    child = current_child()
    if request.method == "POST":
        avatar_key = request.form.get("avatar_key", "")
        if avatar_key not in AVATARS:
            flash("Geçersiz avatar seçimi.", "error")
        else:
            with get_db() as conn:
                conn.execute("UPDATE children SET avatar_key=? WHERE id=?", (avatar_key, child["id"]))
            flash("Avatarın kaydedildi!", "success")
            return redirect(url_for("dashboard"))
    return render_template("avatar.html", child=child, avatars=AVATARS)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect(url_for("admin_panel"))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as conn:
            admin = conn.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if not admin or not check_password_hash(admin["password_hash"], password):
            flash("Admin kullanıcı adı veya şifre hatalı.", "error")
            return render_template("admin_login.html"), 401
        session.clear()
        session.update(admin_id=admin["id"], admin_name=admin["username"])
        return redirect(url_for("admin_panel"))
    return render_template("admin_login.html")


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_panel():
    with get_db() as conn:
        children = conn.execute(
            """SELECT c.*, COUNT(DISTINCT t.id) task_count,
                      COALESCE(SUM(CASE WHEN cp.id IS NOT NULL THEN t.points ELSE 0 END),0) total_score
               FROM children c
               LEFT JOIN tasks t ON t.child_id=c.id AND t.active=1
               LEFT JOIN completions cp ON cp.task_id=t.id
               GROUP BY c.id ORDER BY c.id"""
        ).fetchall()
    return render_template("admin.html", children=children, avatars=AVATARS)


@app.post("/admin/children/add")
@admin_required
def admin_add_child():
    name = request.form.get("name", "").strip()
    child_key = request.form.get("child_key", "").strip().lower()
    password = request.form.get("password", "")
    title = request.form.get("title", "Süper Kaşif").strip() or "Süper Kaşif"
    template_key = request.form.get("template_key", "")
    avatar_key = request.form.get("avatar_key", "scientist")

    if not name or not child_key or len(password) < 4:
        flash("Ad, kullanıcı anahtarı ve en az 4 karakterli şifre gereklidir.", "error")
        return redirect(url_for("admin_panel"))
    if not re.fullmatch(r"[a-z0-9_-]+", child_key):
        flash("Kullanıcı anahtarı yalnızca küçük harf, rakam, - ve _ içerebilir.", "error")
        return redirect(url_for("admin_panel"))
    if avatar_key not in AVATARS:
        avatar_key = "scientist"

    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO children(child_key,name,title,password_hash,avatar_key) VALUES(?,?,?,?,?)",
                (child_key, name, title, generate_password_hash(password), avatar_key),
            )
            new_child_id = cur.lastrowid
            if template_key in SEED_DATA:
                copy_template(conn, new_child_id, template_key)
            for order, (goal_title, criteria, target, bonus) in enumerate(GOAL_SEEDS):
                goal_cur = conn.execute(
                    "INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)",
                    (new_child_id, goal_title, criteria, target, bonus, order),
                )
                conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)", (goal_cur.lastrowid,))
    except Exception as exc:
        if "UNIQUE" in str(exc).upper():
            flash("Bu kullanıcı anahtarı zaten kullanılıyor.", "error")
        else:
            flash("Çocuk eklenemedi.", "error")
        return redirect(url_for("admin_panel"))

    flash(f"{name} başarıyla eklendi.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/report")
@admin_required
def admin_report():
    selected_date = request.args.get("date", date.today().isoformat())
    try:
        datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        selected_date = date.today().isoformat()

    with get_db() as conn:
        children = conn.execute("SELECT * FROM children ORDER BY name").fetchall()
        selected_child_id = request.args.get("child_id", type=int)
        if not selected_child_id and children:
            selected_child_id = children[0]["id"]
        child = conn.execute("SELECT * FROM children WHERE id=?", (selected_child_id,)).fetchone() if selected_child_id else None
        report = None
        if child:
            completions = conn.execute(
                """SELECT t.category, t.description, t.points, cp.note, cp.created_at
                   FROM completions cp JOIN tasks t ON t.id=cp.task_id
                   WHERE t.child_id=? AND cp.completion_date=?
                   ORDER BY t.category,t.sort_order,t.id""",
                (child["id"], selected_date),
            ).fetchall()
            day_score = sum(row["points"] for row in completions)
            task_total = conn.execute(
                """SELECT COALESCE(SUM(t.points),0) FROM completions cp
                   JOIN tasks t ON t.id=cp.task_id
                   WHERE t.child_id=? AND cp.completion_date<=?""",
                (child["id"], selected_date),
            ).fetchone()[0]
            goal_bonus = conn.execute(
                """SELECT COALESCE(SUM(g.bonus_points),0) FROM goals g
                   JOIN goal_progress gp ON gp.goal_id=g.id
                   WHERE g.child_id=? AND gp.completed_date IS NOT NULL AND gp.completed_date<=?""",
                (child["id"], selected_date),
            ).fetchone()[0]
            total_to_date = task_total + goal_bonus
            reward_rows = conn.execute(
                "SELECT * FROM rewards WHERE child_id=? ORDER BY required_points,id",
                (child["id"],),
            ).fetchall()
            all_rewards = []
            for row in reward_rows:
                reward = dict(row)
                reward["eligible"] = reward["required_points"] <= total_to_date
                reward["points_remaining"] = max(0, reward["required_points"] - total_to_date)
                all_rewards.append(reward)
            granted_rewards = conn.execute(
                """SELECT rg.*, COALESCE(r.description, rg.description) reward_description
                   FROM reward_grants rg LEFT JOIN rewards r ON r.id=rg.reward_id
                   WHERE rg.child_id=? AND rg.grant_date=? ORDER BY rg.id DESC""",
                (child["id"], selected_date),
            ).fetchall()
            goals = conn.execute(
                """SELECT g.*, COALESCE(gp.current_value,0) current_value,
                          gp.completed_date, COALESCE(gp.note,'') progress_note
                   FROM goals g LEFT JOIN goal_progress gp ON gp.goal_id=g.id
                   WHERE g.child_id=? AND g.active=1 ORDER BY g.sort_order,g.id""",
                (child["id"],),
            ).fetchall()
            report = dict(child=child, completions=completions, day_score=day_score,
                          task_total=task_total, goal_bonus=goal_bonus, total_to_date=total_to_date,
                          all_rewards=all_rewards, granted_rewards=granted_rewards, goals=goals)
    return render_template("admin_report.html", children=children, report=report,
                           selected_child_id=selected_child_id, selected_date=selected_date, avatars=AVATARS)


@app.post("/admin/rewards/grant")
@admin_required
def admin_grant_reward():
    child_id = request.form.get("child_id", type=int)
    reward_id = request.form.get("reward_id", type=int)
    grant_date = request.form.get("grant_date", date.today().isoformat())
    note = request.form.get("note", "").strip()[:250]
    custom_description = request.form.get("custom_description", "").strip()[:150]
    allow_locked = request.form.get("allow_locked") == "1"
    try:
        datetime.strptime(grant_date, "%Y-%m-%d")
    except ValueError:
        grant_date = date.today().isoformat()
    with get_db() as conn:
        child = conn.execute("SELECT id,name FROM children WHERE id=?", (child_id,)).fetchone()
        if not child:
            abort(404)
        if reward_id:
            reward = conn.execute("SELECT id,required_points,description FROM rewards WHERE id=? AND child_id=?", (reward_id, child_id)).fetchone()
            if not reward:
                abort(404)
            task_total = conn.execute(
                """SELECT COALESCE(SUM(t.points),0) FROM completions cp
                   JOIN tasks t ON t.id=cp.task_id
                   WHERE t.child_id=? AND cp.completion_date<=?""",
                (child_id, grant_date),
            ).fetchone()[0]
            goal_bonus = conn.execute(
                """SELECT COALESCE(SUM(g.bonus_points),0) FROM goals g
                   JOIN goal_progress gp ON gp.goal_id=g.id
                   WHERE g.child_id=? AND gp.completed_date IS NOT NULL AND gp.completed_date<=?""",
                (child_id, grant_date),
            ).fetchone()[0]
            current_total = task_total + goal_bonus
            if reward["required_points"] > current_total and not allow_locked:
                flash(f"Bu ödül için {reward['required_points'] - current_total} puan daha gerekiyor. Manuel vermek için onay kutusunu işaretleyin.", "error")
                return redirect(url_for("admin_report", date=grant_date, child_id=child_id) + "#rewards")
            description = ""
        elif custom_description:
            reward_id = None
            description = custom_description
        else:
            flash("Verilen ödülü seçin veya özel ödül açıklaması yazın.", "error")
            return redirect(url_for("admin_report", date=grant_date, child_id=child_id))
        conn.execute(
            "INSERT INTO reward_grants(child_id,reward_id,description,grant_date,note) VALUES(?,?,?,?,?)",
            (child_id, reward_id, description, grant_date, note),
        )
    flash(f"{child['name']} için verilen ödül kaydedildi.", "success")
    return redirect(url_for("admin_report", date=grant_date, child_id=child_id))


@app.post("/admin/rewards/grant/<int:grant_id>/delete")
@admin_required
def admin_delete_grant(grant_id):
    selected_date = request.form.get("date", date.today().isoformat())
    child_id = request.form.get("child_id", type=int)
    with get_db() as conn:
        conn.execute("DELETE FROM reward_grants WHERE id=?", (grant_id,))
    flash("Ödül kaydı silindi.", "success")
    return redirect(url_for("admin_report", date=selected_date, child_id=child_id))


@app.route("/admin/config")
@admin_required
def admin_config():
    with get_db() as conn:
        children = conn.execute("SELECT * FROM children ORDER BY name").fetchall()
        child_id = request.args.get("child_id", type=int) or (children[0]["id"] if children else None)
        child = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone() if child_id else None
        tasks = conn.execute("SELECT * FROM tasks WHERE child_id=? ORDER BY category,sort_order,id", (child_id,)).fetchall() if child else []
        rewards = conn.execute("SELECT * FROM rewards WHERE child_id=? ORDER BY required_points,id", (child_id,)).fetchall() if child else []
        goals = conn.execute("""SELECT g.*,COALESCE(gp.current_value,0) current_value,gp.completed_date,COALESCE(gp.note,'') progress_note
                                FROM goals g LEFT JOIN goal_progress gp ON gp.goal_id=g.id
                                WHERE g.child_id=? ORDER BY g.sort_order,g.id""", (child_id,)).fetchall() if child else []
        categories = sorted({t["category"] for t in tasks})
    return render_template("admin_config.html", children=children, child=child, child_id=child_id,
                           tasks=tasks, rewards=rewards, goals=goals, categories=categories)


@app.post("/admin/tasks/add")
@admin_required
def admin_task_add():
    child_id=request.form.get("child_id",type=int); category=request.form.get("category","").strip()
    description=request.form.get("description","").strip(); points=max(0,request.form.get("points",type=int) or 0)
    if child_id and category and description:
        with get_db() as conn:
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM tasks WHERE child_id=?",(child_id,)).fetchone()[0]
            conn.execute("INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)",(child_id,category,description,points,order))
        flash("Görev eklendi.","success")
    else: flash("Grup ve görev açıklaması zorunludur.","error")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/tasks/<int:task_id>/edit")
@admin_required
def admin_task_edit(task_id):
    child_id=request.form.get("child_id",type=int); category=request.form.get("category","").strip(); description=request.form.get("description","").strip()
    points=max(0,request.form.get("points",type=int) or 0); active=1 if request.form.get("active") else 0
    with get_db() as conn: conn.execute("UPDATE tasks SET category=?,description=?,points=?,active=? WHERE id=? AND child_id=?",(category,description,points,active,task_id,child_id))
    flash("Görev güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/categories/rename")
@admin_required
def admin_category_rename():
    child_id=request.form.get("child_id",type=int); old=request.form.get("old_category",""); new=request.form.get("new_category","").strip()
    if new:
        with get_db() as conn: conn.execute("UPDATE tasks SET category=? WHERE child_id=? AND category=?",(new,child_id,old))
        flash("Görev grubu yeniden adlandırıldı.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/add")
@admin_required
def admin_reward_add():
    child_id=request.form.get("child_id",type=int); desc=request.form.get("description","").strip(); pts=max(0,request.form.get("required_points",type=int) or 0)
    if desc:
        with get_db() as conn:
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM rewards WHERE child_id=?",(child_id,)).fetchone()[0]
            conn.execute("INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)",(child_id,pts,desc,order))
        flash("Ödül eklendi.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/<int:reward_id>/edit")
@admin_required
def admin_reward_edit(reward_id):
    child_id=request.form.get("child_id",type=int); desc=request.form.get("description","").strip(); pts=max(0,request.form.get("required_points",type=int) or 0)
    with get_db() as conn: conn.execute("UPDATE rewards SET description=?,required_points=? WHERE id=? AND child_id=?",(desc,pts,reward_id,child_id))
    flash("Ödül güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/<int:reward_id>/delete")
@admin_required
def admin_reward_delete(reward_id):
    child_id=request.form.get("child_id",type=int)
    with get_db() as conn: conn.execute("DELETE FROM rewards WHERE id=? AND child_id=?",(reward_id,child_id))
    flash("Ödül silindi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/add")
@admin_required
def admin_goal_add():
    child_id=request.form.get("child_id",type=int); title=request.form.get("title","").strip(); criteria=request.form.get("criteria","").strip()
    target=max(1,request.form.get("target_value",type=int) or 1); bonus=max(0,request.form.get("bonus_points",type=int) or 0)
    if title:
        with get_db() as conn:
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM goals WHERE child_id=?",(child_id,)).fetchone()[0]
            cur=conn.execute("INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)",(child_id,title,criteria,target,bonus,order))
            conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)",(cur.lastrowid,))
        flash("Hedef/rozet eklendi.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/edit")
@admin_required
def admin_goal_edit(goal_id):
    child_id=request.form.get("child_id",type=int); title=request.form.get("title","").strip(); criteria=request.form.get("criteria","").strip()
    target=max(1,request.form.get("target_value",type=int) or 1); bonus=max(0,request.form.get("bonus_points",type=int) or 0); active=1 if request.form.get("active") else 0
    with get_db() as conn: conn.execute("UPDATE goals SET title=?,criteria=?,target_value=?,bonus_points=?,active=? WHERE id=? AND child_id=?",(title,criteria,target,bonus,active,goal_id,child_id))
    flash("Hedef güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/progress")
@admin_required
def admin_goal_progress(goal_id):
    child_id=request.form.get("child_id",type=int); value=max(0,request.form.get("current_value",type=int) or 0); note=request.form.get("note","").strip()[:250]
    completed=request.form.get("completed_date","").strip() or None
    with get_db() as conn:
        goal=conn.execute("SELECT target_value FROM goals WHERE id=? AND child_id=?",(goal_id,child_id)).fetchone()
        if not goal: abort(404)
        if value >= goal["target_value"] and not completed: completed=date.today().isoformat()
        if value < goal["target_value"] and request.form.get("clear_completion"): completed=None
        conn.execute("""INSERT INTO goal_progress(goal_id,current_value,completed_date,note) VALUES(?,?,?,?)
                        ON CONFLICT(goal_id) DO UPDATE SET current_value=excluded.current_value,completed_date=excluded.completed_date,note=excluded.note,updated_at=CURRENT_TIMESTAMP""",(goal_id,value,completed,note))
    flash("Hedef ilerlemesi kaydedildi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/delete")
@admin_required
def admin_goal_delete(goal_id):
    child_id=request.form.get("child_id",type=int)
    with get_db() as conn: conn.execute("DELETE FROM goals WHERE id=? AND child_id=?",(goal_id,child_id))
    flash("Hedef silindi.","success"); return redirect(url_for("admin_config",child_id=child_id))


if __name__ == "__main__":
    app.run(debug=True)
