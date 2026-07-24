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
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from database import AVATARS, GOAL_SEEDS, SEED_DATA, copy_template, get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FAMILYHERO_SECRET_KEY", "familyhero-local-key")
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
               WHERE poll_date=? AND active=1
               ORDER BY id DESC LIMIT 1""",
            (today,),
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
               GROUP BY c.id,c.name,c.avatar_key
               ORDER BY today_score DESC,c.name""",
            (today,),
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
@child_login_required
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
@child_login_required
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
@child_login_required
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
        if len(password) < 6 or password != confirm:
            flash("Şifreler aynı olmalı ve en az 6 karakter olmalı.", "error")
            return render_template("reset_password.html", token=token)
        with get_db() as conn:
            child = conn.execute("SELECT id,email FROM children WHERE id=?", (payload["child_id"],)).fetchone()
            if not child or (child["email"] or "").lower() != payload["email"].lower():
                abort(400)
            conn.execute("UPDATE children SET password_hash=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (generate_password_hash(password), child["id"]))
        flash("Şifreniz yenilendi. Şimdi giriş yapabilirsiniz.", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


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


@app.route("/admin/children/<int:child_id>", methods=["GET", "POST"])
@admin_required
def admin_child_profile(child_id):
    with get_db() as conn:
        child = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
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
                    conn.execute(
                        """UPDATE children SET name=?,email=?,birth_date=?,favorite_team=?,school=?,title=?,updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                        (name, email, birth_date, favorite_team, school, title, child_id),
                    )
                    flash("Çocuk profil bilgileri güncellendi.", "success")
                    return redirect(url_for("admin_child_profile", child_id=child_id))
                except Exception:
                    flash("Bilgiler kaydedilemedi. E-posta başka bir profilde kullanılıyor olabilir.", "error")
        child = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
        task_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE child_id=? AND active=1", (child_id,)).fetchone()[0]
        total_score = conn.execute("SELECT COALESCE(SUM(t.points),0) FROM completions cp JOIN tasks t ON t.id=cp.task_id WHERE t.child_id=?", (child_id,)).fetchone()[0]
    return render_template("admin_child_profile.html", child=child, avatars=AVATARS, task_count=task_count, total_score=total_score)


@app.post("/admin/children/<int:child_id>/send-password-reset")
@admin_required
def admin_send_password_reset(child_id):
    with get_db() as conn:
        child = conn.execute("SELECT id,name,email FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        abort(404)
    if not child["email"]:
        flash("Bu çocuk için kayıtlı e-posta adresi yok.", "error")
        return redirect(url_for("admin_child_profile", child_id=child_id))
    token = password_serializer().dumps({"child_id": child["id"], "email": child["email"]})
    reset_url = url_for("reset_password", token=token, _external=True)
    try:
        if send_reset_email(child["email"], reset_url):
            flash(f"Şifre sıfırlama bağlantısı {child['email']} adresine gönderildi.", "success")
        else:
            flash("E-posta gönderilemedi. Railway SMTP değişkenlerini kontrol edin.", "error")
    except Exception:
        app.logger.exception("Yönetici şifre sıfırlama e-postası gönderilemedi")
        flash("E-posta gönderilirken hata oluştu. SMTP ayarlarını kontrol edin.", "error")
    return redirect(url_for("admin_child_profile", child_id=child_id))


@app.post("/admin/children/add")
@admin_required
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

    if not name or not child_key or not email or len(password) < 4:
        flash("Ad, e-posta, kullanıcı anahtarı ve en az 4 karakterli şifre gereklidir.", "error")
        return redirect(url_for("admin_panel"))
    if not re.fullmatch(r"[a-z0-9_-]+", child_key):
        flash("Kullanıcı anahtarı yalnızca küçük harf, rakam, - ve _ içerebilir.", "error")
        return redirect(url_for("admin_panel"))
    if avatar_key not in AVATARS:
        avatar_key = "scientist"

    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO children(child_key,name,email,title,password_hash,avatar_key,birth_date,favorite_team,school) VALUES(?,?,?,?,?,?,?,?,?)",
                (child_key, name, email, title, generate_password_hash(password), avatar_key, birth_date, favorite_team, school),
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


@app.route("/admin/statistics")
@admin_required
def admin_statistics():
    days = request.args.get("days", default=7, type=int)
    if days not in (7, 14, 30):
        days = 7
    end_day = istanbul_now().date()
    start_day = end_day - timedelta(days=days - 1)
    date_labels = [start_day + timedelta(days=i) for i in range(days)]

    with get_db() as conn:
        children = conn.execute("SELECT id,name,avatar_key FROM children ORDER BY id").fetchall()
        active_tasks = conn.execute(
            """SELECT child_id,COUNT(*) task_count,COALESCE(SUM(points),0) possible_daily
               FROM tasks WHERE active=1 GROUP BY child_id"""
        ).fetchall()
        daily_rows = conn.execute(
            """SELECT t.child_id,cp.completion_date,COUNT(*) completed_count,COALESCE(SUM(t.points),0) score
               FROM completions cp JOIN tasks t ON t.id=cp.task_id
               WHERE cp.completion_date BETWEEN ? AND ?
               GROUP BY t.child_id,cp.completion_date
               ORDER BY cp.completion_date""",
            (start_day.isoformat(), end_day.isoformat()),
        ).fetchall()
        category_rows = conn.execute(
            """SELECT t.category,COUNT(*) completed_count,COALESCE(SUM(t.points),0) score
               FROM completions cp JOIN tasks t ON t.id=cp.task_id
               WHERE cp.completion_date BETWEEN ? AND ?
               GROUP BY t.category ORDER BY score DESC,t.category""",
            (start_day.isoformat(), end_day.isoformat()),
        ).fetchall()
        missed_rows = conn.execute(
            """SELECT c.name child_name,t.description,t.category,COUNT(cp.id) completed_count
               FROM tasks t JOIN children c ON c.id=t.child_id
               LEFT JOIN completions cp ON cp.task_id=t.id AND cp.completion_date BETWEEN ? AND ?
               WHERE t.active=1
               GROUP BY c.name,t.id,t.description,t.category
               ORDER BY completed_count ASC,c.name,t.description LIMIT 8""",
            (start_day.isoformat(), end_day.isoformat()),
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


@app.route("/admin/polls", methods=["GET", "POST"])
@admin_required
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
                "SELECT p.*,COUNT(v.id) vote_count FROM family_polls p LEFT JOIN family_poll_votes v ON v.poll_id=p.id WHERE p.id=? GROUP BY p.id,p.title,p.description,p.poll_date,p.active,p.created_at,p.updated_at",
                (poll_id,),
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
                conn.execute("UPDATE family_polls SET active=0,updated_at=CURRENT_TIMESTAMP WHERE poll_date=?", (poll_date,))
                cur = conn.execute(
                    "INSERT INTO family_polls(title,description,poll_date) VALUES(?,?,?)",
                    (title, description, poll_date),
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
               GROUP BY p.id,p.title,p.description,p.poll_date,p.active,p.created_at,p.updated_at
               ORDER BY p.poll_date DESC,p.id DESC LIMIT 30"""
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
            builder_poll = conn.execute("SELECT * FROM family_polls WHERE id=?", (source_id,)).fetchone()
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
@admin_required
def admin_poll_toggle(poll_id):
    with get_db() as conn:
        poll = conn.execute("SELECT active FROM family_polls WHERE id=?", (poll_id,)).fetchone()
        if poll:
            conn.execute("UPDATE family_polls SET active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (0 if poll["active"] else 1, poll_id))
    return redirect(url_for("admin_polls"))


@app.post("/admin/polls/<int:poll_id>/delete")
@admin_required
def admin_poll_delete(poll_id):
    with get_db() as conn:
        conn.execute("DELETE FROM family_polls WHERE id=?", (poll_id,))
    flash("Oylama silindi.", "success")
    return redirect(url_for("admin_polls"))


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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)