from collections import OrderedDict
from datetime import date, datetime, timedelta
from functools import wraps
import os
import re
import json
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database import (AVATARS, GOAL_SEEDS, SEED_DATA, clone_family_templates, copy_family_defaults_to_child, copy_template, get_db, init_db)
from config import Config
from services.authz import is_platform_admin, permission_required, platform_admin_required
from services.audit import audit_event

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(
    seconds=app.config["PERMANENT_SESSION_LIFETIME_SECONDS"]
)

# CSRF koruması: tüm state değiştiren POST isteklerinde token zorunlu.
csrf = CSRFProtect(app)
app.jinja_env.globals["csrf_token"] = generate_csrf

# Giriş uç noktalarında brute-force / şifre tahmin denemelerini sınırla.
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[])

init_db()
app.logger.info("FamilyHero PostgreSQL veritabanı hazır; DATABASE_URL kullanılıyor.")

ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")

DAILY_FACTS = [
    "İtalya’nın başkenti Roma’dır. Roma’nın efsane futbolcularından biri Francesco Totti’dir. ⚽",
    "Aziz Sancar, DNA onarımı üzerine çalışmalarıyla 2015 Nobel Kimya Ödülü’nü kazandı. 🧬",
    "Dünyanın en büyük okyanusu Pasifik Okyanusu’dur. 🌊",
    "Satrançta her oyuncu oyuna 16 taşla başlar. ♟️",
    "Bir ahtapotun üç kalbi vardır. 🐙",
    "Eyfel Kulesi yaz aylarında sıcaklık nedeniyle birkaç santimetre uzayabilir. 🗼",
    "Türkiye’nin en uzun nehri Kızılırmak’tır. 🏞️",
    "Arılar birbirlerine yön tarif etmek için dans eder. 🐝",
    "Dünya, Güneş’in etrafındaki turunu yaklaşık 365 gün 6 saatte tamamlar. 🌍",
    "İnsan vücudundaki en büyük organ deridir. 🧑‍🔬",
    "Mavi balinalar, Dünya’da yaşamış en büyük hayvanlardır. 🐋",
    "Bir yıldırımın sıcaklığı Güneş’in yüzeyinden daha yüksek olabilir. ⚡",
    "Japonya binlerce adadan oluşan bir ülkedir. 🗾",
    "Penguenler kuş olmalarına rağmen uçamaz; çok iyi yüzücüdürler. 🐧",
    "Ay’daki yerçekimi Dünya’dakinin yaklaşık altıda biridir. 🌙",
    "Dünyanın en yüksek dağı Everest’tir. 🏔️",
    "Leonardo da Vinci hem sanatçı hem de mucit ve bilim insanıydı. 🎨",
    "Filler hortumlarını su içmek, koklamak ve nesneleri tutmak için kullanır. 🐘",
    "Bir gün 24 saat, bir saat 60 dakika ve bir dakika 60 saniyedir. ⏰",
    "Kutup ayılarının derisi siyahtır; tüyleri ise ışığı yansıttığı için beyaz görünür. 🐻‍❄️",
    "Dünyanın en büyük sıcak çölü Sahra Çölü’dür. 🏜️",
    "Kalp, bir günde yaklaşık 100 bin kez atabilir. ❤️",
    "Mozart ilk bestelerini çocuk yaşta yapmaya başladı. 🎼",
    "Bukalemunların gözleri birbirinden bağımsız hareket edebilir. 🦎",
    "Türkiye iki kıta üzerinde yer alır: Avrupa ve Asya. 🌉",
    "Güneş bir yıldızdır ve Dünya’ya en yakın yıldızdır. ☀️",
    "Dünyanın en hızlı kara hayvanı çitadır. 🐆",
    "İstanbul geçmişte Roma, Bizans ve Osmanlı imparatorluklarına başkentlik yaptı. 🏛️",
    "Su, deniz seviyesinde 100 derecede kaynar. 💧",
    "Yunuslar birbirleriyle ıslık benzeri seslerle iletişim kurar. 🐬",
    "Basketbolda bir takım sahada beş oyuncuyla mücadele eder. 🏀",
    "Mars, yüzeyindeki demir oksit nedeniyle Kızıl Gezegen olarak bilinir. 🔴",
    "Dünyanın en büyük kıtası Asya’dır. 🌏",
    "Kaplumbağalar milyonlarca yıldır Dünya’da yaşayan canlılardır. 🐢",
    "Futbolda standart bir maç, uzatmalar hariç 90 dakika sürer. ⚽",
    "Bitkiler fotosentez sırasında ışık enerjisini kullanır. 🌿",
    "Bir kar tanesinin kristal yapısı genellikle altı köşelidir. ❄️",
    "Nil Nehri, dünyanın en uzun nehirlerinden biridir. 🌍",
    "Kediler çok yüksek frekanslı sesleri insanlardan daha iyi duyabilir. 🐈",
    "Türk bayrağındaki yıldız beş köşelidir. 🇹🇷",
    "Satürn’ün belirgin halkaları buz ve kaya parçalarından oluşur. 🪐",
    "İnsan beyninin büyük bölümü sudan oluşur. 🧠",
    "Zürafaların dili yaklaşık yarım metre uzunluğa ulaşabilir. 🦒",
    "Dünyanın en küçük kuşlarından biri arı sinek kuşudur. 🐦",
    "Pusulanın kırmızı ucu genellikle kuzeyi gösterir. 🧭",
    "Olimpiyat halkaları beş kıtayı temsil eden beş halkadan oluşur. 🏅",
    "Gökkuşağı, ışığın su damlalarında kırılması ve yansımasıyla oluşur. 🌈",
    "Bir insanın kemik sayısı yetişkinlikte genellikle 206’dır. 🦴",
    "Dünya’nın doğal uydusu Ay’dır. 🌙",
    "Kangurular güçlü arka bacakları sayesinde uzun mesafelere sıçrayabilir. 🦘",
]

def istanbul_now():
    return datetime.now(ISTANBUL_TZ)

def allowed_completion_date(raw_date):
    now = istanbul_now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    try:
        selected = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        selected = today
    editable = selected == today or (selected == yesterday and now.time() < datetime.strptime("11:00", "%H:%M").time())
    return selected, editable

def password_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="familyhero-password-reset")

def send_reset_email(recipient, reset_url):
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    sender = os.environ.get(
        "RESEND_FROM",
        "FamilyHero <onboarding@resend.dev>",
    ).strip()

    if not api_key:
        app.logger.error("RESEND_API_KEY tanımlı değil; e-posta gönderilemedi.")
        return False

    safe_url = escape(reset_url, quote=True)
    payload = {
        "from": sender,
        "to": [recipient],
        "subject": "FamilyHero şifre sıfırlama bağlantısı",
        "html": f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#172033">
          <h2>FamilyHero şifre sıfırlama</h2>
          <p>Yeni şifrenizi belirlemek için aşağıdaki düğmeye tıklayın.</p>
          <p style="margin:28px 0">
            <a href="{safe_url}"
               style="display:inline-block;background:#4f5ff5;color:#fff;padding:14px 22px;
                      text-decoration:none;border-radius:8px;font-weight:700">
              Şifremi sıfırla
            </a>
          </p>
          <p>Bu isteği siz yapmadıysanız bu e-postayı yok sayabilirsiniz.</p>
          <p style="font-size:12px;color:#667085;word-break:break-all">
            Düğme çalışmazsa bağlantıyı tarayıcınıza yapıştırın:<br>{safe_url}
          </p>
          <p style="font-size:12px;color:#667085">Bağlantı 1 saat geçerlidir.</p>
        </div>
        """,
    }

    request_obj = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "FamilyHero/4.3",
        },
        method="POST",
    )

    try:
        with urlopen(request_obj, timeout=20) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            if 200 <= response.status < 300:
                app.logger.info(
                    "Resend e-postası gönderildi. alıcı=%s yanıt=%s",
                    recipient,
                    response_body,
                )
                return True

            app.logger.error(
                "Resend beklenmeyen durum kodu döndürdü. status=%s yanıt=%s",
                response.status,
                response_body,
            )
            return False
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        app.logger.error(
            "Resend API hatası. status=%s yanıt=%s",
            exc.code,
            error_body,
        )
        return False
    except (URLError, TimeoutError, OSError):
        app.logger.exception("Resend API bağlantısı kurulamadı.")
        return False


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


def current_family_id():
    family_id = session.get("family_id")
    if not family_id:
        abort(403)
    return family_id


def owned_child(conn, child_id):
    return conn.execute(
        "SELECT * FROM children WHERE id=? AND family_id=?",
        (child_id, current_family_id()),
    ).fetchone()


def current_child():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM children WHERE id=? AND family_id=?",
            (session.get("child_id"), session.get("family_id")),
        ).fetchone()


def normalize_family_code(value):
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:40]


def assign_membership_role(conn, membership_id, role_key):
    """Bir aile üyeliğine rol atar; rol bulunamazsa işlemi güvenli biçimde durdurur."""
    role = conn.execute(
        "SELECT id FROM roles WHERE role_key=?",
        (role_key,),
    ).fetchone()
    if not role:
        raise RuntimeError(f"RBAC rolü bulunamadı: {role_key}")
    conn.execute(
        """INSERT INTO membership_roles(membership_id,role_id)
           VALUES(?,?)
           ON CONFLICT DO NOTHING""",
        (membership_id, role["id"]),
    )


def create_family_owner(*, family_name, family_code, username, email, password):
    family_name = (family_name or "").strip()[:100]
    family_code = normalize_family_code(family_code)
    username = (username or "").strip().lower()[:50]
    email = (email or "").strip().lower()[:150] or None
    password = password or ""

    errors = {}
    if not family_name:
        errors["family_name"] = "Aile adı zorunludur."
    if not re.fullmatch(r"[a-z0-9-]{4,40}", family_code):
        errors["family_code"] = "Aile kodu en az 4 karakter olmalı; küçük harf, rakam ve - içerebilir."
    if not re.fullmatch(r"[a-z0-9_.-]{4,50}", username):
        errors["username"] = "Kullanıcı adı en az 4 karakter olmalı; küçük harf, rakam, nokta, - ve _ içerebilir."
    if len(password) < 10:
        errors["password"] = "Şifre en az 10 karakter olmalıdır."

    if errors:
        return None, errors

    with get_db() as conn:
        if conn.execute("SELECT 1 FROM families WHERE LOWER(slug)=LOWER(?)", (family_code,)).fetchone():
            errors["family_code"] = "Bu aile kodu zaten kullanılıyor."
        if conn.execute("SELECT 1 FROM users WHERE LOWER(username)=LOWER(?)", (username,)).fetchone():
            errors["username"] = "Bu kullanıcı adı platformda zaten kullanılıyor."
        if email and conn.execute("SELECT 1 FROM users WHERE LOWER(email)=LOWER(?)", (email,)).fetchone():
            errors["email"] = "Bu e-posta adresi zaten kullanılıyor."
        if errors:
            return None, errors

        source_family = conn.execute("SELECT id FROM families WHERE slug='default-family'").fetchone()
        family = conn.execute(
            "INSERT INTO families(name,slug) VALUES(?,?) RETURNING id",
            (family_name, family_code),
        ).fetchone()
        user = conn.execute(
            """INSERT INTO users(email,username,display_name,password_hash,user_type)
               VALUES(?,?,?,?,?) RETURNING id""",
            (email, username, family_name + " Yöneticisi", generate_password_hash(password), "member"),
        ).fetchone()
        conn.execute(
            "UPDATE families SET created_by_user_id=? WHERE id=?",
            (user["id"], family["id"]),
        )
        membership = conn.execute(
            """INSERT INTO family_memberships(family_id,user_id,member_kind,login_name,status)
               VALUES(?,?,?,?,?) RETURNING id""",
            (family["id"], user["id"], "adult", username, "active"),
        ).fetchone()
        assign_membership_role(conn, membership["id"], "family_owner")
        if source_family:
            clone_family_templates(conn, source_family["id"], family["id"])

    return {
        "family_id": family["id"],
        "family_name": family_name,
        "family_code": family_code,
        "username": username,
        "email": email,
    }, {}


@app.context_processor
def inject_release_info():
    family_name = None
    if session.get("family_id"):
        try:
            with get_db() as conn:
                row = conn.execute("SELECT name FROM families WHERE id=?", (session["family_id"],)).fetchone()
                family_name = row["name"] if row else None
        except Exception:
            family_name = None
    return {
        "app_version": "4.33.0-beta",
        "current_family_name": family_name,
        "is_platform_admin": is_platform_admin(),
        "current_admin_name": session.get("admin_name", "Yönetici"),
    }

@app.route("/home")
def home():
    if session.get("admin_id"):
        return redirect(url_for("admin_panel"))
    if session.get("child_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.get("/api/login/families")
@limiter.limit("60 per minute")
def login_family_search():
    query = (request.args.get("q") or "").strip().lower()[:80]
    if len(query) < 2:
        return jsonify([])
    like = f"%{query}%"
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id,name,slug FROM families
                WHERE status='active' AND (LOWER(name) LIKE ? OR LOWER(slug) LIKE ?)
                ORDER BY CASE WHEN LOWER(slug)=? THEN 0 ELSE 1 END,name
                LIMIT 15""",
            (like, like, query),
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/api/login/families/<int:family_id>/members")
@limiter.limit("60 per minute")
def login_family_members(family_id):
    mode = (request.args.get("mode") or "all").lower()
    with get_db() as conn:
        family = conn.execute(
            "SELECT id FROM families WHERE id=? AND status='active'",
            (family_id,),
        ).fetchone()
        if not family:
            return jsonify([]), 404
        rows = conn.execute(
            """SELECT fm.id AS membership_id,fm.login_name,fm.member_kind,fm.child_id,
                      COALESCE(c.name,u.display_name,fm.login_name) AS display_name,
                      COALESCE(c.avatar_key,'') AS avatar_key,
                      CASE WHEN EXISTS(
                          SELECT 1 FROM membership_roles mr
                          JOIN roles r ON r.id=mr.role_id
                          WHERE mr.membership_id=fm.id
                            AND r.role_key IN ('platform_admin','family_owner','family_admin','parent')
                      ) THEN 1 ELSE 0 END AS is_admin
                 FROM family_memberships fm
                 LEFT JOIN users u ON u.id=fm.user_id
                 LEFT JOIN children c ON c.id=fm.child_id
                WHERE fm.family_id=? AND fm.status='active'
                  AND ((fm.member_kind='child' AND c.id IS NOT NULL)
                       OR (fm.member_kind<>'child' AND COALESCE(u.active,0)=1))
                ORDER BY CASE WHEN fm.member_kind='adult' THEN 0 ELSE 1 END,
                         COALESCE(c.name,u.display_name,fm.login_name)""",
            (family_id,),
        ).fetchall()
    members = []
    for row in rows:
        item = dict(row)
        if mode == "adult" and not item["is_admin"]:
            continue
        if mode == "child" and item["member_kind"] != "child":
            continue
        members.append(item)
    return jsonify(members)


@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if session.get("admin_id"):
        return redirect(url_for("admin_panel"))
    if session.get("child_id"):
        return redirect(url_for("dashboard"))

    username = (request.form.get("username") or "").strip().lower()
    if request.method == "POST":
        password = request.form.get("password", "")
        with get_db() as conn:
            member = conn.execute(
                """SELECT fm.id AS membership_id,fm.family_id,fm.login_name,fm.member_kind,fm.child_id,
                          u.id AS user_id,u.display_name,u.password_hash AS user_password_hash,u.user_type,
                          c.name AS child_name,c.password_hash AS child_password_hash,
                          CASE WHEN EXISTS(
                              SELECT 1 FROM membership_roles mr
                              JOIN roles r ON r.id=mr.role_id
                              WHERE mr.membership_id=fm.id
                                AND r.role_key IN ('platform_admin','family_owner','family_admin','parent')
                          ) THEN 1 ELSE 0 END AS is_admin
                     FROM users u
                     JOIN family_memberships fm ON fm.user_id=u.id AND fm.status='active'
                     LEFT JOIN children c ON c.id=fm.child_id
                    WHERE LOWER(u.username)=LOWER(?) AND u.active=1
                    LIMIT 1""",
                (username,),
            ).fetchone()

        password_hash = None
        if member:
            password_hash = member["child_password_hash"] if member["member_kind"] == "child" else member["user_password_hash"]
        if not member or not password_hash or not check_password_hash(password_hash, password):
            audit_event("auth.login.failed", "username", username or None)
            flash("Kullanıcı adı veya şifre hatalı.", "error")
            return render_template("login.html", username=username), 401

        session.clear()
        session.permanent = True
        session.update(
            user_id=member["user_id"],
            family_id=member["family_id"],
            membership_id=member["membership_id"],
        )
        if member["member_kind"] == "child":
            session.update(child_id=member["child_id"], child_name=member["child_name"])
            audit_event("auth.login.success", "child", member["child_id"])
            return redirect(url_for("dashboard"))
        if member["is_admin"]:
            session.update(admin_id=member["user_id"], admin_name=member["login_name"])
            audit_event("auth.login.success", "admin", member["user_id"])
            return redirect(url_for("admin_panel"))

        session.clear()
        abort(403)

    return render_template("login.html", username=username)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@child_login_required
def dashboard():
    child = current_child()
    today = istanbul_now().date().isoformat()
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
        poll = conn.execute(
            """SELECT * FROM family_polls
               WHERE poll_date=? AND active=1 AND family_id=?
               ORDER BY id DESC LIMIT 1""",
            (today, child["family_id"]),
        ).fetchone()
        poll_options = []
        child_vote_option_id = None
        poll_total_votes = 0
        if poll:
            poll_options = conn.execute(
                """SELECT o.*,COUNT(v.id) vote_count
                   FROM family_poll_options o
                   LEFT JOIN family_poll_votes v ON v.option_id=o.id
                   WHERE o.poll_id=?
                   GROUP BY o.id,o.poll_id,o.option_text,o.emoji,o.sort_order
                   ORDER BY o.sort_order,o.id""",
                (poll["id"],),
            ).fetchall()
            vote = conn.execute(
                "SELECT option_id FROM family_poll_votes WHERE poll_id=? AND child_id=?",
                (poll["id"], child["id"]),
            ).fetchone()
            child_vote_option_id = vote["option_id"] if vote else None
            poll_total_votes = sum(option["vote_count"] for option in poll_options)
        family_rows = conn.execute(
            """SELECT c.id,c.name,c.avatar_key,
                      COALESCE(SUM(CASE WHEN t.active=1 THEN t.points ELSE 0 END),0) possible_score,
                      COALESCE(SUM(CASE WHEN cp.id IS NOT NULL THEN t.points ELSE 0 END),0) today_score,
                      COUNT(DISTINCT CASE WHEN t.active=1 THEN t.id END) task_count,
                      COUNT(DISTINCT cp.id) done_count
               FROM children c
               LEFT JOIN tasks t ON t.child_id=c.id AND t.active=1
               LEFT JOIN completions cp ON cp.task_id=t.id AND cp.completion_date=?
               WHERE c.family_id=?
               GROUP BY c.id,c.name,c.avatar_key
               ORDER BY today_score DESC,c.name""",
            (today, child["family_id"]),
        ).fetchall()
    task_count=len(tasks); done_count=sum(1 for t in tasks if t["done"])
    completion_percent=round(done_count*100/task_count) if task_count else 0
    total_score=task_total+goal_bonus
    family_leaderboard=[]
    for index,row in enumerate(family_rows, start=1):
        item=dict(row)
        item["rank"]=index
        item["progress_percent"]=round(item["today_score"]*100/item["possible_score"]) if item["possible_score"] else 0
        family_leaderboard.append(item)
    current_rank=next((item["rank"] for item in family_leaderboard if item["id"]==child["id"]),1)
    leader=family_leaderboard[0] if family_leaderboard else None
    if leader and leader["id"]==child["id"]:
        motivation_message="Bugünün lideri sensin! Seriyi korumaya devam et. 🏆"
    elif leader:
        difference=max(0,leader["today_score"]-today_score)
        motivation_message=f"{leader['name']} bugün {difference} puan önde. Bir görev daha tamamlayarak farkı kapatabilirsin! 🚀"
    else:
        motivation_message="İlk puanı sen kazan ve aile sıralamasında öne geç! ⚡"
    daily_fact = DAILY_FACTS[date.fromisoformat(today).toordinal() % len(DAILY_FACTS)]
    return render_template("child_dashboard.html", child=child, avatars=AVATARS, today=today, daily_fact=daily_fact,
        today_score=today_score,total_score=total_score,task_count=task_count,done_count=done_count,
        completion_percent=completion_percent,goals=goals,last_reward=last_reward,
        family_leaderboard=family_leaderboard,current_rank=current_rank,motivation_message=motivation_message,
        poll=poll,poll_options=poll_options,child_vote_option_id=child_vote_option_id,
        poll_total_votes=poll_total_votes,poll_closed=istanbul_now().hour>=16)


@app.post("/polls/<int:poll_id>/vote")
@permission_required("poll.vote", login_endpoint="login")
def child_poll_vote(poll_id):
    child = current_child()
    now = istanbul_now()
    today = now.date().isoformat()
    if now.hour >= 16:
        flash("Oylama saat 16:00'da kapandı.", "error")
        return redirect(url_for("dashboard"))
    option_id = request.form.get("option_id", type=int)
    with get_db() as conn:
        poll = conn.execute("SELECT * FROM family_polls WHERE id=? AND poll_date=? AND active=1", (poll_id, today)).fetchone()
        option = conn.execute("SELECT id FROM family_poll_options WHERE id=? AND poll_id=?", (option_id, poll_id)).fetchone() if option_id else None
        if not poll or not option:
            flash("Geçerli bir seçenek seçin.", "error")
            return redirect(url_for("dashboard"))
        existing = conn.execute("SELECT id FROM family_poll_votes WHERE poll_id=? AND child_id=?", (poll_id, child["id"])).fetchone()
        if existing:
            conn.execute("UPDATE family_poll_votes SET option_id=?,created_at=CURRENT_TIMESTAMP WHERE id=?", (option_id, existing["id"]))
            flash("Oyun güncellendi.", "success")
        else:
            conn.execute("INSERT INTO family_poll_votes(poll_id,option_id,child_id) VALUES(?,?,?)", (poll_id, option_id, child["id"]))
            flash("Oyun kaydedildi.", "success")
    return redirect(url_for("dashboard"))


@app.route("/tasks")
@child_login_required
def child_tasks():
    child = current_child()
    now = istanbul_now()
    today_date = now.date()
    yesterday_date = today_date - timedelta(days=1)
    selected, editable = allowed_completion_date(request.args.get("date", today_date.isoformat()))
    if selected not in (today_date, yesterday_date):
        selected = today_date
        editable = True
    selected_date = selected.isoformat()
    with get_db() as conn:
        tasks=conn.execute("""SELECT t.*,CASE WHEN cp.id IS NULL THEN 0 ELSE 1 END done,COALESCE(cp.note,'') note,cp.created_at,cp.updated_at
            FROM tasks t LEFT JOIN completions cp ON cp.task_id=t.id AND cp.completion_date=?
            WHERE t.child_id=? AND t.active=1 ORDER BY t.sort_order,t.id""",(selected_date,child["id"])).fetchall()
        day_score=conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=? AND cp.completion_date=?",(child["id"],selected_date)).fetchone()[0]
        total_score=conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?",(child["id"],)).fetchone()[0]
    grouped=OrderedDict()
    for task in tasks: grouped.setdefault(task["category"],[]).append(task)
    task_count=len(tasks); done_count=sum(1 for t in tasks if t["done"]); completion_percent=round(done_count*100/task_count) if task_count else 0
    return render_template("child.html",child=child,grouped=grouped,today_score=day_score,total_score=total_score,today=selected_date,avatars=AVATARS,task_count=task_count,done_count=done_count,completion_percent=completion_percent,selected_date=selected_date,today_date=today_date.isoformat(),yesterday_date=yesterday_date.isoformat(),editable=editable,is_yesterday=selected==yesterday_date,lock_time="11:00")


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
@permission_required("task.complete", login_endpoint="login")
def save_task(task_id):
    child = current_child()
    selected, editable = allowed_completion_date(request.form.get("completion_date"))
    if not editable:
        flash("Zaman doldu; düne ait veri giremezsiniz.", "error")
        return redirect(url_for("child_tasks", date=selected.isoformat()))
    completion_date = selected.isoformat()
    note = request.form.get("note", "").strip()[:250]
    with get_db() as conn:
        task = conn.execute("SELECT id FROM tasks WHERE id=? AND child_id=? AND active=1", (task_id, child["id"])).fetchone()
        if not task:
            abort(404)
        conn.execute(
            "INSERT INTO completions(task_id,completion_date,note) VALUES(?,?,?) ON CONFLICT(task_id,completion_date) DO UPDATE SET note=excluded.note, updated_at=CURRENT_TIMESTAMP",
            (task_id, completion_date, note),
        )
    return redirect(url_for("child_tasks", date=completion_date))


@app.post("/task/<int:task_id>/undo")
@permission_required("task.complete", login_endpoint="login")
def undo_task(task_id):
    child = current_child()
    selected, editable = allowed_completion_date(request.form.get("completion_date"))
    if not editable:
        flash("Zaman doldu; düne ait veri giremezsiniz.", "error")
        return redirect(url_for("child_tasks", date=selected.isoformat()))
    completion_date = selected.isoformat()
    with get_db() as conn:
        if not conn.execute("SELECT id FROM tasks WHERE id=? AND child_id=?", (task_id, child["id"])).fetchone():
            abort(404)
        conn.execute("DELETE FROM completions WHERE task_id=? AND completion_date=?", (task_id, completion_date))
    return redirect(url_for("child_tasks", date=completion_date))


@app.route("/profile")
@child_login_required
def child_profile():
    child = current_child()
    return render_template("child_profile.html", child=child, avatars=AVATARS)


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


@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        with get_db() as conn:
            child = conn.execute("SELECT id,email FROM children WHERE LOWER(email)=?", (email,)).fetchone()
        if child:
            token = password_serializer().dumps({"child_id": child["id"], "email": child["email"]})
            reset_url = url_for("reset_password", token=token, _external=True)
            try:
                sent = send_reset_email(child["email"], reset_url)
                if not sent and app.debug:
                    flash(f"Test bağlantısı: {reset_url}", "success")
            except Exception:
                app.logger.exception("Şifre sıfırlama e-postası gönderilemedi")
        flash("Bu e-posta sistemde kayıtlıysa şifre sıfırlama bağlantısı gönderildi.", "success")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        payload = password_serializer().loads(token, max_age=3600)
    except SignatureExpired:
        flash("Şifre sıfırlama bağlantısının süresi dolmuş.", "error")
        return redirect(url_for("forgot_password"))
    except BadSignature:
        flash("Şifre sıfırlama bağlantısı geçersiz.", "error")
        return redirect(url_for("forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(password) < 10 or password != confirm:
            flash("Şifreler aynı olmalı ve en az 10 karakter olmalı.", "error")
            return render_template("reset_password.html", token=token)
        with get_db() as conn:
            child = conn.execute("SELECT id,email FROM children WHERE id=?", (payload["child_id"],)).fetchone()
            if not child or (child["email"] or "").lower() != payload["email"].lower():
                abort(400)
            new_hash = generate_password_hash(password)
            conn.execute(
                "UPDATE children SET password_hash=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (new_hash, child["id"]),
            )
            conn.execute(
                """UPDATE users SET password_hash=?,must_change_password=0,updated_at=CURRENT_TIMESTAMP
                   WHERE id=(SELECT user_id FROM family_memberships WHERE child_id=? LIMIT 1)""",
                (new_hash, child["id"]),
            )
        audit_event("auth.password.reset", "child", payload["child_id"])
        flash("Şifreniz yenilendi. Şimdi giriş yapabilirsiniz.", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect(url_for("admin_panel"))

    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT id,username,display_name,password_hash FROM users WHERE LOWER(username)=LOWER(?) AND active=1",
                (username,),
            ).fetchone()
            membership = None
            if user:
                membership = conn.execute(
                    """SELECT fm.id AS membership_id, fm.family_id, fm.login_name
                         FROM family_memberships fm
                         JOIN membership_roles mr ON mr.membership_id=fm.id
                         JOIN roles r ON r.id=mr.role_id
                        WHERE fm.user_id=? AND fm.status='active'
                          AND r.role_key IN ('platform_admin','family_owner','family_admin','parent')
                        ORDER BY CASE r.role_key
                                     WHEN 'platform_admin' THEN 0
                                     WHEN 'family_owner' THEN 1
                                     WHEN 'family_admin' THEN 2
                                     ELSE 3
                                 END, fm.id
                        LIMIT 1""",
                    (user["id"],),
                ).fetchone()

        valid = bool(
            user and user["password_hash"] and membership
            and check_password_hash(user["password_hash"], password)
        )
        if not valid:
            audit_event("auth.admin_login.failed", "user", user["id"] if user else None)
            flash("Kullanıcı adı veya şifre hatalı.", "error")
            return render_template("admin_login.html", username=username), 401

        session.clear()
        session.permanent = True
        session.update(
            user_id=user["id"],
            family_id=membership["family_id"],
            membership_id=membership["membership_id"],
            admin_id=user["id"],
            admin_name=user["display_name"] or membership["login_name"],
        )
        audit_event("auth.login.success", "admin", user["id"])
        return redirect(url_for("admin_panel"))

    return render_template("admin_login.html", username=username)


@app.route("/register-family", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def register_family():
    if session.get("admin_id") and is_platform_admin():
        return redirect(url_for("super_admin_families"))

    form = {
        "family_name": request.form.get("family_name", ""),
        "family_code": request.form.get("family_code", ""),
        "username": request.form.get("username", ""),
        "email": request.form.get("email", ""),
    }
    errors = {}
    if request.method == "POST":
        created, errors = create_family_owner(
            family_name=form["family_name"],
            family_code=form["family_code"],
            username=form["username"],
            email=form["email"],
            password=request.form.get("password", ""),
        )
        if created:
            audit_event("platform.family.created.public", "family", created["family_id"], after=created)
            flash("Aileniz oluşturuldu. Yönetici girişi yapabilirsiniz.", "success")
            return redirect(url_for("admin_login"))

    return render_template("register_family.html", form=form, errors=errors)


@app.route("/super-admin/families", methods=["GET", "POST"])
@platform_admin_required
def super_admin_families():
    form = {
        "family_name": request.form.get("family_name", ""),
        "family_code": request.form.get("family_code", ""),
        "username": request.form.get("username", ""),
        "email": request.form.get("email", ""),
    }
    errors = {}

    if request.method == "POST":
        created, errors = create_family_owner(
            family_name=form["family_name"],
            family_code=form["family_code"],
            username=form["username"],
            email=form["email"],
            password=request.form.get("password", ""),
        )
        if created:
            audit_event("platform.family.created", "family", created["family_id"], after=created)
            flash(f"{created['family_name']} oluşturuldu. Yönetici: {created['username']}", "success")
            return redirect(url_for("super_admin_families", q=created["family_code"]))

    search_query = (request.args.get("q") or "").strip()[:100]
    params = []
    where_clause = ""
    if search_query:
        like = f"%{search_query.lower()}%"
        where_clause = """WHERE LOWER(f.name) LIKE ? OR LOWER(f.slug) LIKE ?
                           OR LOWER(COALESCE(owner_membership.login_name,'')) LIKE ?
                           OR LOWER(COALESCE(owner.email,'')) LIKE ?"""
        params = [like, like, like, like]

    result_limit = 50 if search_query else 25
    with get_db() as conn:
        total_count = conn.execute("SELECT COUNT(*) FROM families").fetchone()[0]
        families = conn.execute(
            f"""
            SELECT f.id,f.name,f.slug,f.status,f.created_at,
                   owner_membership.login_name AS owner_username,owner.email AS owner_email,
                   COUNT(DISTINCT CASE WHEN fm.member_kind='adult' THEN fm.id END) AS adult_count,
                   COUNT(DISTINCT c.id) AS child_count
              FROM families f
              LEFT JOIN users owner ON owner.id=f.created_by_user_id
              LEFT JOIN family_memberships owner_membership
                     ON owner_membership.family_id=f.id AND owner_membership.user_id=f.created_by_user_id
              LEFT JOIN family_memberships fm ON fm.family_id=f.id AND fm.status='active'
              LEFT JOIN children c ON c.family_id=f.id
              {where_clause}
             GROUP BY f.id,f.name,f.slug,f.status,f.created_at,
                      owner_membership.login_name,owner.email
             ORDER BY f.created_at DESC,f.id DESC
             LIMIT {result_limit}
            """,
            tuple(params),
        ).fetchall()

    return render_template(
        "super_admin_families.html",
        families=families,
        form=form,
        errors=errors,
        selected_family_id=session.get("family_id"),
        total_count=total_count,
        search_query=search_query,
    )


@app.post("/super-admin/families/<int:family_id>/switch")
@platform_admin_required
def super_admin_switch_family(family_id):
    with get_db() as conn:
        family = conn.execute(
            "SELECT id,name,slug,status FROM families WHERE id=?",
            (family_id,),
        ).fetchone()
    if not family:
        abort(404)
    if family["status"] != "active":
        flash("Pasif bir aileye geçilemez.", "error")
        return redirect(url_for("super_admin_families"))

    session["family_id"] = family["id"]
    audit_event("platform.family.switched", "family", family["id"])
    flash(f"{family['name']} çalışma alanına geçildi.", "success")
    return redirect(url_for("admin_panel"))


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@permission_required("family.view")
def admin_panel():
    with get_db() as conn:
        children = conn.execute(
            """SELECT c.*, COUNT(DISTINCT t.id) task_count,
                      COALESCE(SUM(CASE WHEN cp.id IS NOT NULL THEN t.points ELSE 0 END),0) total_score
               FROM children c
               LEFT JOIN tasks t ON t.child_id=c.id AND t.active=1
               LEFT JOIN completions cp ON cp.task_id=t.id
               WHERE c.family_id=?
               GROUP BY c.id ORDER BY c.id""",
            (current_family_id(),),
        ).fetchall()
    return render_template("admin.html", children=children, avatars=AVATARS)


@app.route("/admin/children/<int:child_id>", methods=["GET", "POST"])
@permission_required("member.manage")
def admin_child_profile(child_id):
    with get_db() as conn:
        child = owned_child(conn, child_id)
        if not child:
            abort(404)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower() or None
            birth_date = request.form.get("birth_date", "").strip() or None
            favorite_team = request.form.get("favorite_team", "").strip()
            school = request.form.get("school", "").strip()
            title = request.form.get("title", "").strip() or "Süper Kaşif"
            if not name:
                flash("Ad soyad alanı boş bırakılamaz.", "error")
            else:
                try:
                    before = dict(child)
                    conn.execute(
                        """UPDATE children SET name=?,email=?,birth_date=?,favorite_team=?,school=?,title=?,updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                        (name, email, birth_date, favorite_team, school, title, child_id),
                    )
                    conn.execute(
                        """UPDATE users SET display_name=?,email=?,updated_at=CURRENT_TIMESTAMP
                           WHERE id=(SELECT user_id FROM family_memberships WHERE child_id=? AND family_id=? LIMIT 1)""",
                        (name, email, child_id, current_family_id()),
                    )
                    audit_event(
                        "member.update", "child", child_id, before=before,
                        after={"name": name, "email": email, "birth_date": birth_date,
                               "favorite_team": favorite_team, "school": school, "title": title},
                    )
                    flash("Çocuk profil bilgileri güncellendi.", "success")
                    return redirect(url_for("admin_child_profile", child_id=child_id))
                except Exception:
                    flash("Bilgiler kaydedilemedi. E-posta başka bir profilde kullanılıyor olabilir.", "error")
        child = owned_child(conn, child_id)
        task_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE child_id=? AND active=1", (child_id,)).fetchone()[0]
        total_score = conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?", (child_id,)).fetchone()[0]
    return render_template("admin_child_profile.html", child=child, avatars=AVATARS, task_count=task_count, total_score=total_score)


@app.post("/admin/children/<int:child_id>/send-password-reset")
@permission_required("member.manage")
def admin_send_password_reset(child_id):
    with get_db() as conn:
        child = conn.execute("SELECT id,name,email FROM children WHERE id=? AND family_id=?", (child_id, current_family_id())).fetchone()
    if not child:
        abort(404)
    if not child["email"]:
        flash("Bu çocuk için kayıtlı e-posta adresi yok.", "error")
        return redirect(url_for("admin_child_profile", child_id=child_id))
    token = password_serializer().dumps({"child_id": child["id"], "email": child["email"]})
    reset_url = url_for("reset_password", token=token, _external=True)
    try:
        if send_reset_email(child["email"], reset_url):
            audit_event("member.password_reset.sent", "child", child_id)
            flash(f"Şifre sıfırlama bağlantısı {child['email']} adresine gönderildi.", "success")
        else:
            flash("E-posta gönderilemedi. Railway SMTP değişkenlerini kontrol edin.", "error")
    except Exception:
        app.logger.exception("Yönetici şifre sıfırlama e-postası gönderilemedi")
        flash("E-posta gönderilirken hata oluştu. SMTP ayarlarını kontrol edin.", "error")
    return redirect(url_for("admin_child_profile", child_id=child_id))


@app.post("/admin/children/add")
@permission_required("member.manage")
def admin_add_child():
    name = request.form.get("name", "").strip()
    child_key = request.form.get("child_key", "").strip().lower()
    password = request.form.get("password", "")
    email = request.form.get("email", "").strip().lower()
    title = request.form.get("title", "Süper Kaşif").strip() or "Süper Kaşif"
    birth_date = request.form.get("birth_date", "").strip() or None
    favorite_team = request.form.get("favorite_team", "").strip()
    school = request.form.get("school", "").strip()
    template_key = request.form.get("template_key", "")
    avatar_key = request.form.get("avatar_key", "scientist")
    family_id = current_family_id()

    if not name or not child_key or not email or len(password) < 10:
        flash("Ad, e-posta, kullanıcı anahtarı ve en az 10 karakterli şifre gereklidir.", "error")
        return redirect(url_for("admin_panel"))
    if not re.fullmatch(r"[a-z0-9_-]+", child_key):
        flash("Kullanıcı anahtarı yalnızca küçük harf, rakam, - ve _ içerebilir.", "error")
        return redirect(url_for("admin_panel"))
    if avatar_key not in AVATARS:
        avatar_key = "scientist"

    try:
        with get_db() as conn:
            if conn.execute(
                "SELECT 1 FROM users WHERE LOWER(username)=LOWER(?)",
                (child_key,),
            ).fetchone():
                flash("Bu kullanıcı adı platformda zaten kullanılıyor.", "error")
                return redirect(url_for("admin_panel"))
            if conn.execute("SELECT 1 FROM users WHERE LOWER(email)=LOWER(?)", (email,)).fetchone():
                flash("Bu e-posta adresi başka bir profilde kullanılıyor.", "error")
                return redirect(url_for("admin_panel"))

            family = conn.execute("SELECT id,slug FROM families WHERE id=?", (family_id,)).fetchone()
            password_hash = generate_password_hash(password)
            cur = conn.execute(
                """INSERT INTO children(family_id,child_key,name,email,title,password_hash,avatar_key,birth_date,favorite_team,school)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (family_id, child_key, name, email, title, password_hash, avatar_key, birth_date, favorite_team, school),
            )
            new_child_id = cur.lastrowid
            copied = copy_family_defaults_to_child(conn, family_id, new_child_id)
            if not copied["tasks"] and template_key in SEED_DATA:
                copy_template(conn, new_child_id, template_key)
            if not copied["goals"]:
                for order, (goal_title, criteria, target, bonus) in enumerate(GOAL_SEEDS):
                    goal_cur = conn.execute(
                        "INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)",
                        (new_child_id, goal_title, criteria, target, bonus, order),
                    )
                    conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)", (goal_cur.lastrowid,))

            user = conn.execute(
                """INSERT INTO users(email,username,display_name,password_hash,user_type)
                   VALUES(?,?,?,?,?) RETURNING id""",
                (email, child_key, name, password_hash, "member"),
            ).fetchone()
            membership = conn.execute(
                """INSERT INTO family_memberships(family_id,user_id,member_kind,child_id,login_name,status)
                   VALUES(?,?,?,?,?,?) RETURNING id""",
                (family_id, user["id"], "child", new_child_id, child_key, "active"),
            ).fetchone()
            assign_membership_role(conn, membership["id"], "child")
    except Exception:
        app.logger.exception("Çocuk eklenemedi")
        flash("Çocuk eklenemedi. Kullanıcı adı veya e-posta başka bir kayıtta olabilir.", "error")
        return redirect(url_for("admin_panel"))

    audit_event("member.create", "child", new_child_id, after={"name": name, "child_key": child_key, "email": email})
    flash(f"{name} başarıyla eklendi; aile varsayılanları uygulandı.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/statistics")
@permission_required("statistics.view")
def admin_statistics():
    days = request.args.get("days", default=7, type=int)
    if days not in (7, 14, 30):
        days = 7
    end_day = istanbul_now().date()
    start_day = end_day - timedelta(days=days - 1)
    date_labels = [start_day + timedelta(days=i) for i in range(days)]

    with get_db() as conn:
        children = conn.execute("SELECT id,name,avatar_key FROM children WHERE family_id=? ORDER BY id", (current_family_id(),)).fetchall()
        active_tasks = conn.execute(
            """SELECT child_id,COUNT(*) task_count,COALESCE(SUM(points),0) possible_daily
               FROM tasks t JOIN children c ON c.id=t.child_id WHERE t.active=1 AND c.family_id=? GROUP BY child_id""",
            (current_family_id(),)
        ).fetchall()
        daily_rows = conn.execute(
            """SELECT t.child_id,cp.completion_date,COUNT(*) completed_count,COALESCE(SUM(t.points),0) score
               FROM completions cp JOIN tasks t ON t.id=cp.task_id
               JOIN children c ON c.id=t.child_id
               WHERE cp.completion_date BETWEEN ? AND ? AND c.family_id=?
               GROUP BY t.child_id,cp.completion_date
               ORDER BY cp.completion_date""",
            (start_day.isoformat(), end_day.isoformat(), current_family_id()),
        ).fetchall()
        category_rows = conn.execute(
            """SELECT t.category,COUNT(*) completed_count,COALESCE(SUM(t.points),0) score
               FROM completions cp JOIN tasks t ON t.id=cp.task_id
               JOIN children c ON c.id=t.child_id
               WHERE cp.completion_date BETWEEN ? AND ? AND c.family_id=?
               GROUP BY t.category ORDER BY score DESC,t.category""",
            (start_day.isoformat(), end_day.isoformat(), current_family_id()),
        ).fetchall()
        missed_rows = conn.execute(
            """SELECT c.name child_name,t.description,t.category,COUNT(cp.id) completed_count
               FROM tasks t JOIN children c ON c.id=t.child_id
               LEFT JOIN completions cp ON cp.task_id=t.id AND cp.completion_date BETWEEN ? AND ?
               WHERE t.active=1 AND c.family_id=?
               GROUP BY c.name,t.id,t.description,t.category
               ORDER BY completed_count ASC,c.name,t.description LIMIT 8""",
            (start_day.isoformat(), end_day.isoformat(), current_family_id()),
        ).fetchall()

    task_map={row["child_id"]:dict(row) for row in active_tasks}
    daily_map={(row["child_id"],str(row["completion_date"])):dict(row) for row in daily_rows}
    child_series=[]
    total_points=0
    total_completed=0
    total_possible=0
    max_daily_score=1
    for child_row in children:
        child=dict(child_row)
        task_info=task_map.get(child["id"],{"task_count":0,"possible_daily":0})
        points=[]
        completed=[]
        for day in date_labels:
            item=daily_map.get((child["id"],day.isoformat()),{"score":0,"completed_count":0})
            points.append(int(item["score"] or 0))
            completed.append(int(item["completed_count"] or 0))
        period_score=sum(points)
        period_completed=sum(completed)
        possible=int(task_info["possible_daily"] or 0)*days
        completion_capacity=int(task_info["task_count"] or 0)*days
        completion_rate=round(period_completed*100/completion_capacity) if completion_capacity else 0
        max_daily_score=max(max_daily_score,max(points) if points else 0)
        total_points+=period_score
        total_completed+=period_completed
        total_possible+=completion_capacity
        child.update(points=points,completed=completed,period_score=period_score,
                     period_completed=period_completed,possible_score=possible,
                     completion_rate=completion_rate)
        child_series.append(child)
    child_series.sort(key=lambda item:(item["period_score"],item["completion_rate"]),reverse=True)
    for index,item in enumerate(child_series,start=1):
        item["rank"]=index
    overall_rate=round(total_completed*100/total_possible) if total_possible else 0
    categories=[]
    max_category=max([int(row["score"] or 0) for row in category_rows] or [1])
    for row in category_rows:
        item=dict(row)
        item["width"]=round(int(item["score"] or 0)*100/max_category) if max_category else 0
        categories.append(item)
    missed=[]
    for row in missed_rows:
        item=dict(row)
        item["missed_count"]=max(0,days-int(item["completed_count"] or 0))
        missed.append(item)
    return render_template("admin_statistics.html",children=children,child_series=child_series,
        date_labels=date_labels,start_date=start_day,end_date=end_day,days=days,
        total_points=total_points,total_completed=total_completed,overall_rate=overall_rate,
        categories=categories,missed=missed,max_daily_score=max_daily_score,avatars=AVATARS)


@app.route("/admin/report")
@permission_required("report.view")
def admin_report():
    selected_date = request.args.get("date", date.today().isoformat())
    try:
        datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        selected_date = date.today().isoformat()

    with get_db() as conn:
        children = conn.execute("SELECT * FROM children WHERE family_id=? ORDER BY name", (current_family_id(),)).fetchall()
        selected_child_id = request.args.get("child_id", type=int)
        if not selected_child_id and children:
            selected_child_id = children[0]["id"]
        child = conn.execute("SELECT * FROM children WHERE id=? AND family_id=?", (selected_child_id, current_family_id())).fetchone() if selected_child_id else None
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
@permission_required("reward.manage")
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
        child = conn.execute("SELECT id,name FROM children WHERE id=? AND family_id=?", (child_id, current_family_id())).fetchone()
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
@permission_required("reward.manage")
def admin_delete_grant(grant_id):
    selected_date = request.form.get("date", date.today().isoformat())
    child_id = request.form.get("child_id", type=int)
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("DELETE FROM reward_grants WHERE id=? AND child_id=?", (grant_id, child_id))
    flash("Ödül kaydı silindi.", "success")
    return redirect(url_for("admin_report", date=selected_date, child_id=child_id))


@app.route("/admin/polls", methods=["GET", "POST"])
@permission_required("poll.manage")
def admin_polls():
    today = istanbul_now().date().isoformat()
    edit_id = request.args.get("edit_id", type=int)
    copy_id = request.args.get("copy_id", type=int)

    if request.method == "POST":
        poll_id = request.form.get("poll_id", type=int)
        title = request.form.get("title", "").strip()[:120]
        description = request.form.get("description", "").strip()[:250]
        poll_date = request.form.get("poll_date", today)
        try:
            datetime.strptime(poll_date, "%Y-%m-%d")
        except ValueError:
            poll_date = today

        option_texts = request.form.getlist("option_text")
        option_emojis = request.form.getlist("option_emoji")
        options = []
        for index, text in enumerate(option_texts[:6]):
            text = text.strip()[:100]
            if text:
                emoji = option_emojis[index].strip()[:8] if index < len(option_emojis) else ""
                options.append((emoji, text))

        with get_db() as conn:
            existing = conn.execute(
                "SELECT p.*,COUNT(v.id) vote_count FROM family_polls p LEFT JOIN family_poll_votes v ON v.poll_id=p.id WHERE p.id=? AND p.family_id=? GROUP BY p.id,p.family_id,p.title,p.description,p.poll_date,p.active,p.created_at,p.updated_at",
                (poll_id, current_family_id()),
            ).fetchone() if poll_id else None

            if not title:
                flash("Oylama başlığı zorunludur.", "error")
            elif existing and existing["vote_count"] > 0:
                conn.execute(
                    "UPDATE family_polls SET title=?,description=?,poll_date=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (title, description, poll_date, poll_id),
                )
                flash("Oylama güncellendi. Oy kullanıldığı için seçenekler korunmuştur.", "success")
                return redirect(url_for("admin_polls"))
            elif len(options) < 2:
                flash("En az iki seçenek girilmelidir.", "error")
            elif existing:
                conn.execute(
                    "UPDATE family_polls SET title=?,description=?,poll_date=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (title, description, poll_date, poll_id),
                )
                conn.execute("DELETE FROM family_poll_options WHERE poll_id=?", (poll_id,))
                for order, (emoji, text) in enumerate(options):
                    conn.execute(
                        "INSERT INTO family_poll_options(poll_id,option_text,emoji,sort_order) VALUES(?,?,?,?)",
                        (poll_id, text, emoji, order),
                    )
                flash("Oylama güncellendi.", "success")
                return redirect(url_for("admin_polls"))
            else:
                conn.execute("UPDATE family_polls SET active=0,updated_at=CURRENT_TIMESTAMP WHERE poll_date=? AND family_id=?", (poll_date, current_family_id()))
                cur = conn.execute(
                    "INSERT INTO family_polls(family_id,title,description,poll_date) VALUES(?,?,?,?)",
                    (current_family_id(), title, description, poll_date),
                )
                for order, (emoji, text) in enumerate(options):
                    conn.execute(
                        "INSERT INTO family_poll_options(poll_id,option_text,emoji,sort_order) VALUES(?,?,?,?)",
                        (cur.lastrowid, text, emoji, order),
                    )
                flash("Aile oylaması yayınlandı.", "success")
                return redirect(url_for("admin_polls"))

    with get_db() as conn:
        polls = conn.execute(
            """SELECT p.*,COUNT(DISTINCT v.id) vote_count,COUNT(DISTINCT o.id) option_count
               FROM family_polls p
               LEFT JOIN family_poll_options o ON o.poll_id=p.id
               LEFT JOIN family_poll_votes v ON v.poll_id=p.id
               WHERE p.family_id=?
               GROUP BY p.id,p.family_id,p.title,p.description,p.poll_date,p.active,p.created_at,p.updated_at
               ORDER BY p.poll_date DESC,p.id DESC LIMIT 30""",
            (current_family_id(),)
        ).fetchall()
        poll_details = {}
        poll_voters = {}
        for poll in polls:
            poll_details[poll["id"]] = conn.execute(
                """SELECT o.*,COUNT(v.id) vote_count
                   FROM family_poll_options o LEFT JOIN family_poll_votes v ON v.option_id=o.id
                   WHERE o.poll_id=? GROUP BY o.id,o.poll_id,o.option_text,o.emoji,o.sort_order
                   ORDER BY o.sort_order,o.id""", (poll["id"],)
            ).fetchall()
            poll_voters[poll["id"]] = conn.execute(
                """SELECT c.name FROM family_poll_votes v
                   JOIN children c ON c.id=v.child_id
                   WHERE v.poll_id=? ORDER BY c.name""",
                (poll["id"],),
            ).fetchall()

        builder_poll = None
        builder_options = []
        builder_mode = "new"
        source_id = edit_id or copy_id
        if source_id:
            builder_poll = conn.execute("SELECT * FROM family_polls WHERE id=? AND family_id=?", (source_id, current_family_id())).fetchone()
            if builder_poll:
                builder_options = conn.execute(
                    "SELECT * FROM family_poll_options WHERE poll_id=? ORDER BY sort_order,id",
                    (source_id,),
                ).fetchall()
                builder_mode = "edit" if edit_id else "copy"

    return render_template(
        "admin_polls.html", polls=polls, poll_details=poll_details, poll_voters=poll_voters,
        today=today, builder_poll=builder_poll, builder_options=builder_options, builder_mode=builder_mode
    )


@app.post("/admin/polls/<int:poll_id>/toggle")
@permission_required("poll.manage")
def admin_poll_toggle(poll_id):
    with get_db() as conn:
        poll = conn.execute("SELECT active FROM family_polls WHERE id=? AND family_id=?", (poll_id, current_family_id())).fetchone()
        if poll:
            conn.execute("UPDATE family_polls SET active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (0 if poll["active"] else 1, poll_id))
    return redirect(url_for("admin_polls"))


@app.post("/admin/polls/<int:poll_id>/delete")
@permission_required("poll.manage")
def admin_poll_delete(poll_id):
    with get_db() as conn:
        conn.execute("DELETE FROM family_polls WHERE id=? AND family_id=?", (poll_id, current_family_id()))
    flash("Oylama silindi.", "success")
    return redirect(url_for("admin_polls"))


@app.route("/admin/config")
@permission_required("family.view")
def admin_config():
    with get_db() as conn:
        children = conn.execute("SELECT * FROM children WHERE family_id=? ORDER BY name", (current_family_id(),)).fetchall()
        child_id = request.args.get("child_id", type=int) or (children[0]["id"] if children else None)
        child = owned_child(conn, child_id) if child_id else None
        tasks = conn.execute("SELECT * FROM tasks WHERE child_id=? ORDER BY category,sort_order,id", (child_id,)).fetchall() if child else []
        rewards = conn.execute("SELECT * FROM rewards WHERE child_id=? ORDER BY required_points,id", (child_id,)).fetchall() if child else []
        goals = conn.execute("""SELECT g.*,COALESCE(gp.current_value,0) current_value,gp.completed_date,COALESCE(gp.note,'') progress_note
                                FROM goals g LEFT JOIN goal_progress gp ON gp.goal_id=g.id
                                WHERE g.child_id=? ORDER BY g.sort_order,g.id""", (child_id,)).fetchall() if child else []
        categories = sorted({t["category"] for t in tasks})
    return render_template("admin_config.html", children=children, child=child, child_id=child_id,
                           tasks=tasks, rewards=rewards, goals=goals, categories=categories)


@app.post("/admin/tasks/add")
@permission_required("task.create")
def admin_task_add():
    child_id=request.form.get("child_id",type=int); category=request.form.get("category","").strip()
    description=request.form.get("description","").strip(); points=max(0,request.form.get("points",type=int) or 0)
    if child_id and category and description:
        with get_db() as conn:
            if not owned_child(conn, child_id): abort(404)
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM tasks WHERE child_id=?",(child_id,)).fetchone()[0]
            conn.execute("INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)",(child_id,category,description,points,order))
        flash("Görev eklendi.","success")
    else: flash("Grup ve görev açıklaması zorunludur.","error")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/tasks/<int:task_id>/edit")
@permission_required("task.update")
def admin_task_edit(task_id):
    child_id=request.form.get("child_id",type=int); category=request.form.get("category","").strip(); description=request.form.get("description","").strip()
    points=max(0,request.form.get("points",type=int) or 0); active=1 if request.form.get("active") else 0
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("UPDATE tasks SET category=?,description=?,points=?,active=? WHERE id=? AND child_id=?",(category,description,points,active,task_id,child_id))
    flash("Görev güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/categories/rename")
@permission_required("task.update")
def admin_category_rename():
    child_id=request.form.get("child_id",type=int); old=request.form.get("old_category",""); new=request.form.get("new_category","").strip()
    if new:
        with get_db() as conn:
            if not owned_child(conn, child_id): abort(404)
            conn.execute("UPDATE tasks SET category=? WHERE child_id=? AND category=?",(new,child_id,old))
        flash("Görev grubu yeniden adlandırıldı.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/add")
@permission_required("reward.manage")
def admin_reward_add():
    child_id=request.form.get("child_id",type=int); desc=request.form.get("description","").strip(); pts=max(0,request.form.get("required_points",type=int) or 0)
    if desc:
        with get_db() as conn:
            if not owned_child(conn, child_id): abort(404)
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM rewards WHERE child_id=?",(child_id,)).fetchone()[0]
            conn.execute("INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)",(child_id,pts,desc,order))
        flash("Ödül eklendi.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/<int:reward_id>/edit")
@permission_required("reward.manage")
def admin_reward_edit(reward_id):
    child_id=request.form.get("child_id",type=int); desc=request.form.get("description","").strip(); pts=max(0,request.form.get("required_points",type=int) or 0)
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("UPDATE rewards SET description=?,required_points=? WHERE id=? AND child_id=?",(desc,pts,reward_id,child_id))
    flash("Ödül güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/rewards/<int:reward_id>/delete")
@permission_required("reward.manage")
def admin_reward_delete(reward_id):
    child_id=request.form.get("child_id",type=int)
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("DELETE FROM rewards WHERE id=? AND child_id=?",(reward_id,child_id))
    flash("Ödül silindi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/add")
@permission_required("goal.manage")
def admin_goal_add():
    child_id=request.form.get("child_id",type=int); title=request.form.get("title","").strip(); criteria=request.form.get("criteria","").strip()
    target=max(1,request.form.get("target_value",type=int) or 1); bonus=max(0,request.form.get("bonus_points",type=int) or 0)
    if title:
        with get_db() as conn:
            if not owned_child(conn, child_id): abort(404)
            order=conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM goals WHERE child_id=?",(child_id,)).fetchone()[0]
            cur=conn.execute("INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)",(child_id,title,criteria,target,bonus,order))
            conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)",(cur.lastrowid,))
        flash("Hedef/rozet eklendi.","success")
    return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/edit")
@permission_required("goal.manage")
def admin_goal_edit(goal_id):
    child_id=request.form.get("child_id",type=int); title=request.form.get("title","").strip(); criteria=request.form.get("criteria","").strip()
    target=max(1,request.form.get("target_value",type=int) or 1); bonus=max(0,request.form.get("bonus_points",type=int) or 0); active=1 if request.form.get("active") else 0
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("UPDATE goals SET title=?,criteria=?,target_value=?,bonus_points=?,active=? WHERE id=? AND child_id=?",(title,criteria,target,bonus,active,goal_id,child_id))
    flash("Hedef güncellendi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/progress")
@permission_required("goal.manage")
def admin_goal_progress(goal_id):
    child_id=request.form.get("child_id",type=int); value=max(0,request.form.get("current_value",type=int) or 0); note=request.form.get("note","").strip()[:250]
    completed=request.form.get("completed_date","").strip() or None
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        goal=conn.execute("SELECT target_value FROM goals WHERE id=? AND child_id=?",(goal_id,child_id)).fetchone()
        if not goal: abort(404)
        if value >= goal["target_value"] and not completed: completed=date.today().isoformat()
        if value < goal["target_value"] and request.form.get("clear_completion"): completed=None
        conn.execute("""INSERT INTO goal_progress(goal_id,current_value,completed_date,note) VALUES(?,?,?,?)
                        ON CONFLICT(goal_id) DO UPDATE SET current_value=excluded.current_value,completed_date=excluded.completed_date,note=excluded.note,updated_at=CURRENT_TIMESTAMP""",(goal_id,value,completed,note))
    flash("Hedef ilerlemesi kaydedildi.","success"); return redirect(url_for("admin_config",child_id=child_id))


@app.post("/admin/goals/<int:goal_id>/delete")
@permission_required("goal.manage")
def admin_goal_delete(goal_id):
    child_id=request.form.get("child_id",type=int)
    with get_db() as conn:
        if not owned_child(conn, child_id): abort(404)
        conn.execute("DELETE FROM goals WHERE id=? AND child_id=?",(goal_id,child_id))
    flash("Hedef silindi.","success"); return redirect(url_for("admin_config",child_id=child_id))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)