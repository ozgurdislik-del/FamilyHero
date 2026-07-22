import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "familyhero.db"

AVATARS = {
    "scientist": "🧑‍🔬",
    "space_scientist": "👨‍🚀",
    "football_hero": "⚽",
    "goalkeeper": "🧤",
}

SEED_DATA = {
    "uzay": {
        "name": "Uzay",
        "title": "Süper Kaşif",
        "avatar": "space_scientist",
        "tasks": [
            ("Öğrenme Görevleri", "20 dakika Türkçe kitap Okudu", 10),
            ("Öğrenme Görevleri", "Okuduğu kitabı 3 cümle ile anlattı", 10),
            ("Öğrenme Görevleri", "5 yeni kelime öğrendi", 10),
            ("Öğrenme Görevleri", "Yaz ödev kitabından 4 sayfa çözdü", 10),
            ("Öğrenme Görevleri", "Duolingo da ingilizce çalıştı", 10),
            ("Öğrenme Görevleri", "15 dakika İngilizce kitap okudu", 10),
            ("Öğrenme Görevleri", "Haritadan 1 ülke seçip başkentini öğrendi ve bayrağını çizdi.", 10),
            ("Öğrenme Görevleri", "10 ingilizce kelime ve anlamını yazdı", 10),
            ("Öğrenme Görevleri", "Türkiye harita puzzlenı yaptı. Türkiye haritasını çizdi", 10),
            ("Öğrenme Görevleri", "Bir deney videosu izledi ve ailesine anlattı", 10),
            ("Akıl Oyunları", "Kodlama çalışması yaptı", 10),
            ("Akıl Oyunları", "Hergün 1 satranç maçı yaptı", 10),
            ("Akıl Oyunları", "Lego, yapboz veya zeka oyunu oynadı", 10),
            ("Akıl Oyunları", "Sudoku bulmaca çözdü", 10),
            ("Akıl Oyunları", "Dünya harita puzzlenı yaptı", 10),
            ("Ev Kahramanı", "Yatağını topladı", 5),
            ("Ev Kahramanı", "Odasını topladı", 5),
            ("Ev Kahramanı", "Pijamasını katladı", 5),
            ("Ev Kahramanı", "Perdesini açıp, odasını havalandırdı", 5),
            ("Ev Kahramanı", "Anneye ev işlerinde yardım etti (bulaşık makinesi boşaltma/ çamaşır asma-toplama/ ortak alanları toplama / buzdolabı temizleme / kiler temizleme)", 15),
            ("Ev Kahramanı", "Yüzme kursu havuz çantasını hazırladı", 15),
            ("Sağlıklı Yaşam", "Sabah dişlerini fırçaladı", 5),
            ("Sağlıklı Yaşam", "Akşam dişlerini fırçaladı", 5),
            ("Sağlıklı Yaşam", "Sağlıklı bir ara öğün hazırladı", 5),
            ("Sağlıklı Yaşam", "En az 30 dakika spor veya hareket yaptı", 10),
            ("Sağlıklı Yaşam", "Günlük 1,5 lt.su hedefini tamamladı", 10),
            ("Sağlıklı Yaşam", "Yüzme antremanına itirazsız gitti", 20),
            ("Sağlıklı Yaşam", "Basketbol oynadı 20 dakika", 10),
            ("Sağlıklı Yaşam", "Havuzda 25 mt 8 tur (yani 16 kere git-gel) yüzdü", 15),
            ("Sağlıklı Yaşam", "Gazlı içecek- ıce tea- şekerli içecek tüketmedi", 10),
            ("Sağlıklı Yaşam", "Abur cubur yemedi", 10),
            ("Sağlıklı Yaşam", "Gece 23.00 den önce yattı", 15),
            ("İyi Kalpli Çocuk", "Bir iyilik yaptı veya nazik bir davranış sergiledi", 15),
            ("İyi Kalpli Çocuk", "Bir çiçek yetiştirdi", 10),
            ("İyi Kalpli Çocuk", "Bir büyüğünü aradı veya ziyaret etti, sohbet etti.", 15),
            ("İyi Kalpli Çocuk", "Evde kimse söylemeden bir işi üstlendi", 15),
            ("Ekstra Puan Avcısı", "Haftada 7 kitap bitirdi.", 25),
            ("Ekstra Puan Avcısı", "Tatlısız, şekersiz, atıştırmalık olmadan 1 hafta bitirdi", 25),
            ("Ekstra Puan Avcısı", "Ailece kutu oyunu, masa oyunu organize etti", 25),
            ("Ekstra Puan Avcısı", "1 gün telefonsuz zaman geçirdi", 25),
        ],
        "rewards": [
            (1200, "1 öğün dışarıdan yemek yeme"),
            (1500, "1 öğün dışarıdan yemek yeme + 200 TL'lik oyun harcaması"),
            (1750, "1 öğün dışarıdan yemek yeme + 400 TL'lik oyun harcaması"),
            (2500, "2 öğün dışarıdan yemek yeme + 500 TL'lik oyun harcaması + forma"),
        ],
    },
    "toprak": {
        "name": "Toprak",
        "title": "Süper Kaşif",
        "avatar": "football_hero",
        "tasks": [
            ("Öğrenme Görevleri", "40 dakika Türkçe kitap Okudu", 10),
            ("Öğrenme Görevleri", "Okuduğu kitaptan 5 satırlık özet çıkarttı", 10),
            ("Öğrenme Görevleri", "20 Paragraf sorusu çözdü", 10),
            ("Öğrenme Görevleri", "Duolingo da Almanca çalıştı", 10),
            ("Öğrenme Görevleri", "Almanca 10 yeni kelime yazdı.", 10),
            ("Öğrenme Görevleri", "20 dakika İngilizce kitap okudu", 10),
            ("Öğrenme Görevleri", "İngilizce podcast veya TED-Ed izledi", 10),
            ("Öğrenme Görevleri", "Almanya / Amerika üniversitelerini araştırdı (hergün 1 üniversite hakkında bilgi edindi ve öğrendiklerini not aldı)", 10),
            ("Öğrenme Görevleri", "Bir bilim insanı hakkında araştırma yaptı", 10),
            ("Öğrenme Görevleri", "20 matematik sorusu çözdü", 10),
            ("Akıl Oyunları", "Pythonda en az 30 dakika kod yazdı", 10),
            ("Akıl Oyunları", "GitHub hesabı açıp çalışmalarını yükledi", 10),
            ("Akıl Oyunları", "Basit bir web sitesi yapmayı öğren (HTML/ CSS)", 10),
            ("Akıl Oyunları", "Her gün 2 satranç maçı yaptı", 10),
            ("Akıl Oyunları", "5 tane Sudoku bulmaca çözdü", 10),
            ("Ev Kahramanı", "Yatağını topladı", 5),
            ("Ev Kahramanı", "Odasını topladı", 5),
            ("Ev Kahramanı", "Kirli sepetindeki çamaşırları makine önündeki sepete attı", 5),
            ("Ev Kahramanı", "Anneye ev işlerinde yardım etti (bulaşık makinesi boşaltma/ çamaşır asma-toplama/ ortak alanları toplama / buzdolabı temizleme / kiler temizleme)", 15),
            ("Ev Kahramanı", "Kardeşiyle kaliteli zaman geçirdi", 15),
            ("Ev Kahramanı", "Kardeşine satranç/ ülke dersi verdi", 10),
            ("Ev Kahramanı", "Haftada 3 farklı yemek yapmayı öğrenme", 15),
            ("Ev Kahramanı", "Sofrayı kurma ve kaldırmada yardımcı olma", 10),
            ("Ev Kahramanı", "Çamaşır/ bulaşık makinesi çalıştırma", 10),
            ("Ev Kahramanı", "Blendır kullanarak smothie yaptı/ çay demledi / kahve yaptı", 10),
            ("Sağlıklı Yaşam", "Sabah dişlerini fırçaladı", 5),
            ("Sağlıklı Yaşam", "Akşam dişlerini fırçaladı", 5),
            ("Sağlıklı Yaşam", "Sağlıklı bir ara öğün hazırladı", 5),
            ("Sağlıklı Yaşam", "Günde 7.000 adım attı", 20),
            ("Sağlıklı Yaşam", "Günlük 2,5 lt. su hedefini tamamladı", 10),
            ("Sağlıklı Yaşam", "Kahvaltısını hazırladı", 5),
            ("Sağlıklı Yaşam", "Dambıllarla kuvvet egzersizi yaptı. Hergün 15 dakika", 15),
            ("Sağlıklı Yaşam", "Gece 00.00 den önce yattı", 15),
            ("Sağlıklı Yaşam", "Havuzda 25 mt 15 tur (yani 30 kere git-gel) yüzdü", 15),
            ("Sağlıklı Yaşam", "Sabah 9:00 da uyanıp gruba GÜNAYDIN yazdı ", 15),
            ("Sağlıklı Yaşam", "Gazlı içecek- ıce tea- şekerli içecek tüketmedi", 10),
            ("Sağlıklı Yaşam", "Abur cubur yemedi", 10),
            ("İyi Kalpli Çocuk", "Bir iyilik yaptı veya nazik bir davranış sergiledi", 15),
            ("İyi Kalpli Çocuk", "Bir çiçek yetiştirdi", 10),
            ("İyi Kalpli Çocuk", "Bir büyüğünü aradı veya ziyaret etti, sohbet etti.", 15),
            ("İyi Kalpli Çocuk", "Evde kimse söylemeden bir işi üstlendi", 15),
            ("İyi Kalpli Çocuk", "Birine yeni birşey öğretti.", 15),
            ("Ekstra Puan Avcısı", "Haftada 1 kitap bitirdi.", 25),
            ("Ekstra Puan Avcısı", "Haftada 50.000 adım attı", 25),
            ("Ekstra Puan Avcısı", "Tatlısız, şekersiz, atıştırmalık olmadan 1 hafta bitirdi", 25),
            ("Ekstra Puan Avcısı", "Ailece kutu oyunu, masa oyunu organize etti", 25),
            ("Ekstra Puan Avcısı", "1 gün telefonsuz zaman geçirdi", 25),
        ],
        "rewards": [
            (1600, "1 öğün dışarıdan yemek yeme"),
            (2000, "1 öğün dışarıdan yemek yeme + 200 TL"),
            (2500, "1 öğün dışarıdan yemek yeme + 400 TL"),
            (3000, "2 öğün dışarıdan yemek yeme + 500 TL"),
        ],
    },
}

OLD_TO_CANONICAL = {
    "uzay": {
        "20 dakika Türkçe kitap okudu": "20 dakika Türkçe kitap Okudu",
        "Duolingo'da İngilizce çalıştı": "Duolingo da ingilizce çalıştı",
        "1 satranç maçı yaptı": "Hergün 1 satranç maçı yaptı",
        "En az 30 dakika spor yaptı": "En az 30 dakika spor veya hareket yaptı",
        "Bir iyilik veya nazik davranış yaptı": "Bir iyilik yaptı veya nazik bir davranış sergiledi",
    },
    "toprak": {
        "40 dakika Türkçe kitap okudu": "40 dakika Türkçe kitap Okudu",
        "Okuduğu kitaptan 5 satırlık özet çıkardı": "Okuduğu kitaptan 5 satırlık özet çıkarttı",
        "20 paragraf sorusu çözdü": "20 Paragraf sorusu çözdü",
        "Duolingo'da Almanca çalıştı": "Duolingo da Almanca çalıştı",
        "Python'da en az 30 dakika kod yazdı": "Pythonda en az 30 dakika kod yazdı",
        "2 satranç maçı yaptı": "Her gün 2 satranç maçı yaptı",
        "Günlük 2,5 litre su içti": "Günlük 2,5 lt. su hedefini tamamladı",
        "15 dakika kuvvet egzersizi yaptı": "Dambıllarla kuvvet egzersizi yaptı. Hergün 15 dakika",
        "Bir iyilik veya nazik davranış yaptı": "Bir iyilik yaptı veya nazik bir davranış sergiledi",
    },
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def copy_template(conn, child_id, template_key):
    template = SEED_DATA.get(template_key)
    if not template:
        return
    for order, (category, description, points) in enumerate(template["tasks"]):
        conn.execute(
            "INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)",
            (child_id, category, description, points, order),
        )
    for order, (required_points, description) in enumerate(template["rewards"]):
        conn.execute(
            "INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)",
            (child_id, required_points, description, order),
        )


def sync_seed_child(conn, child_key, child):
    row = conn.execute("SELECT * FROM children WHERE child_key=?", (child_key,)).fetchone()
    if not row:
        cur = conn.execute(
            "INSERT INTO children(child_key,name,title,password_hash,avatar_key) VALUES(?,?,?,?,?)",
            (child_key, child["name"], child["title"], generate_password_hash(f"{child['name']}123!"), child["avatar"]),
        )
        copy_template(conn, cur.lastrowid, child_key)
        return

    child_id = row["id"]
    if not row["avatar_key"]:
        conn.execute("UPDATE children SET avatar_key=? WHERE id=?", (child["avatar"], child_id))

    for old, new in OLD_TO_CANONICAL.get(child_key, {}).items():
        old_row = conn.execute(
            "SELECT id FROM tasks WHERE child_id=? AND description=?", (child_id, old)
        ).fetchone()
        new_row = conn.execute(
            "SELECT id FROM tasks WHERE child_id=? AND description=?", (child_id, new)
        ).fetchone()
        if old_row and not new_row:
            conn.execute("UPDATE tasks SET description=? WHERE id=?", (new, old_row["id"]))

    existing = {r["description"] for r in conn.execute("SELECT description FROM tasks WHERE child_id=?", (child_id,))}
    next_order = conn.execute("SELECT COALESCE(MAX(sort_order),-1)+1 FROM tasks WHERE child_id=?", (child_id,)).fetchone()[0]
    for category, description, points in child["tasks"]:
        if description not in existing:
            conn.execute(
                "INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)",
                (child_id, category, description, points, next_order),
            )
            next_order += 1


def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'Süper Kaşif',
                password_hash TEXT,
                avatar_key TEXT NOT NULL DEFAULT 'scientist'
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                points INTEGER NOT NULL CHECK(points >= 0),
                sort_order INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                required_points INTEGER NOT NULL,
                description TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                completion_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(task_id, completion_date),
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reward_grants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                reward_id INTEGER,
                description TEXT NOT NULL DEFAULT '',
                grant_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE,
                FOREIGN KEY(reward_id) REFERENCES rewards(id) ON DELETE SET NULL
            );
            """
        )
        child_cols = {r[1] for r in conn.execute("PRAGMA table_info(children)")}
        if "password_hash" not in child_cols:
            conn.execute("ALTER TABLE children ADD COLUMN password_hash TEXT")
        if "avatar_key" not in child_cols:
            conn.execute("ALTER TABLE children ADD COLUMN avatar_key TEXT NOT NULL DEFAULT 'scientist'")
        completion_cols = {r[1] for r in conn.execute("PRAGMA table_info(completions)")}
        if "note" not in completion_cols:
            conn.execute("ALTER TABLE completions ADD COLUMN note TEXT NOT NULL DEFAULT ''")

        if not conn.execute("SELECT 1 FROM admins WHERE username='admin'").fetchone():
            conn.execute(
                "INSERT INTO admins(username,password_hash) VALUES(?,?)",
                ("admin", generate_password_hash("FamilyHero2026!")),
            )

        for key, child in SEED_DATA.items():
            sync_seed_child(conn, key, child)

        for key, pw in {"uzay": "Uzay123!", "toprak": "Toprak123!"}.items():
            row = conn.execute("SELECT password_hash FROM children WHERE child_key=?", (key,)).fetchone()
            if row and not row["password_hash"]:
                conn.execute("UPDATE children SET password_hash=? WHERE child_key=?", (generate_password_hash(pw), key))

GOAL_SEEDS = [
    ("Kitap Kurdu", "7 gün üst üste kitap okursa", 7, 200),
    ("Satranç Ustası", "25 satranç maçı oynarsa", 25, 200),
    ("Kodlama Kahramanı", "15 kodlama görevi yaparsa", 15, 200),
    ("İngilizce Şampiyonu", "30 gün Duolingo çalışırsa", 30, 200),
    ("Ülkeler Şampiyonu", "15 ülkenin başkentini öğrenip haritasını çizerse", 15, 400),
    ("İyilik Elçisi", "20 iyilik görevi tamamlarsa", 20, 500),
    ("Yüzme Yıldızı", "15 yüzme antrenmanı yaparsa", 15, 1000),
    ("Sağlık Elçisi", "20 gün abur cubur ve ice tea olmadan geçirirse", 20, 5000),
    ("Yazın Süper Kaşifi", "Tüm rozetleri tamamlarsa", 1, 7500),
    ("Aylık Görev Şampiyonu", "1 ay boyunca haftalık tüm görevleri yaparsa", 1, 10000),
]


def ensure_configurable_schema(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            criteria TEXT NOT NULL DEFAULT '',
            target_value INTEGER NOT NULL DEFAULT 1,
            bonus_points INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(child_id) REFERENCES children(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS goal_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL UNIQUE,
            current_value INTEGER NOT NULL DEFAULT 0,
            completed_date TEXT,
            note TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(goal_id) REFERENCES goals(id) ON DELETE CASCADE
        );
        """
    )
    for child in conn.execute("SELECT id FROM children ORDER BY id").fetchall():
        exists = conn.execute("SELECT 1 FROM goals WHERE child_id=? LIMIT 1", (child["id"],)).fetchone()
        if not exists:
            for order, (title, criteria, target, points) in enumerate(GOAL_SEEDS):
                cur = conn.execute(
                    "INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)",
                    (child["id"], title, criteria, target, points, order),
                )
                conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)", (cur.lastrowid,))


_original_init_db = init_db

def repair_seed_task_labels(conn):
    """Eski sürümlerde kategori adı görev açıklamasına yazılmış kayıtları güvenle onarır."""
    known_categories = {
        "Öğrenme Görevleri", "Akıl Oyunları", "Ev Kahramanı",
        "Sağlıklı Yaşam", "İyi Kalpli Çocuk", "Ekstra Puan Avcısı"
    }
    for child_key, template in SEED_DATA.items():
        child = conn.execute("SELECT id FROM children WHERE child_key=?", (child_key,)).fetchone()
        if not child:
            continue
        child_id = child["id"]
        by_category = {}
        for category, description, points in template["tasks"]:
            by_category.setdefault(category, []).append((description, points))
        for category, expected in by_category.items():
            rows = conn.execute(
                "SELECT id,description FROM tasks WHERE child_id=? AND category=? ORDER BY sort_order,id",
                (child_id, category),
            ).fetchall()
            for row, (description, points) in zip(rows, expected):
                current = (row["description"] or "").strip()
                if not current or current in known_categories:
                    conn.execute(
                        "UPDATE tasks SET description=?,points=? WHERE id=?",
                        (description, points, row["id"]),
                    )


def init_db():
    _original_init_db()
    with get_db() as conn:
        ensure_configurable_schema(conn)
        repair_seed_task_labels(conn)
