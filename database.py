import os
import logging
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

logger = logging.getLogger("familyhero")


def _seed_password(env_var, fallback_label):
    """İlk hesap oluşturulurken gerekli şifreyi yalnızca ortamdan alır."""
    value = os.environ.get(env_var, "").strip()
    if value:
        if len(value) < 10:
            raise RuntimeError(f"{env_var} en az 10 karakter olmalıdır.")
        return value
    raise RuntimeError(
        f"{fallback_label} oluşturulamadı: {env_var} tanımlı değil. "
        "Şifreler kaynak kodda veya deploy loglarında üretilemez."
    )

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


class HybridRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class DbResult:
    def __init__(self, cursor, lastrowid=None):
        self.cursor = cursor
        self.lastrowid = lastrowid

    def _wrap(self, row):
        if row is None:
            return None
        if isinstance(row, dict):
            return HybridRow(row)
        if self.cursor.description:
            return HybridRow({d.name: v for d, v in zip(self.cursor.description, row)})
        return row

    def fetchone(self):
        return self._wrap(self.cursor.fetchone())

    def fetchall(self):
        return [self._wrap(r) for r in self.cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())


class DbConnection:
    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _sql(query):
        return query.replace('?', '%s')

    def execute(self, query, params=()):
        query = self._sql(query)
        cur = self.conn.cursor()
        lastrowid = None
        q_upper = query.lstrip().upper()
        wants_id = q_upper.startswith('INSERT INTO') and 'RETURNING ' not in q_upper and 'ON CONFLICT' not in q_upper
        if wants_id:
            query = query.rstrip().rstrip(';') + ' RETURNING id'
        cur.execute(query, params)
        if wants_id:
            row = cur.fetchone()
            lastrowid = row[0] if row else None
        return DbResult(cur, lastrowid)

    def executescript(self, script):
        for statement in [s.strip() for s in script.split(';') if s.strip()]:
            self.execute(statement)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


def get_db():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL tanımlı değil. Railway Variables bölümünden Postgres.DATABASE_URL referansını ekleyin.')
    if database_url.startswith('postgres://'):
        database_url = 'postgresql://' + database_url[len('postgres://'):]
    import psycopg
    return DbConnection(psycopg.connect(database_url))


def copy_template(conn, child_id, template_key):
    template = SEED_DATA.get(template_key)
    if not template:
        return
    for order, (category, description, points) in enumerate(template['tasks']):
        conn.execute('INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)',
                     (child_id, category, description, points, order))
    for order, (required_points, description) in enumerate(template['rewards']):
        conn.execute('INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)',
                     (child_id, required_points, description, order))


def sync_seed_child(conn, child_key, child):
    row = conn.execute("SELECT c.* FROM children c JOIN families f ON f.id=c.family_id WHERE c.child_key=? AND f.slug='default-family'", (child_key,)).fetchone()
    if not row:
        cur = conn.execute("INSERT INTO children(family_id,child_key,name,title,password_hash,avatar_key) VALUES((SELECT id FROM families WHERE slug='default-family'),?,?,?,?,?)",
                           (child_key, child['name'], child['title'], generate_password_hash(_seed_password(f"FAMILYHERO_CHILD_{child_key.upper()}_PASSWORD", f"'{child_key}' çocuk hesabı")), child['avatar']))
        copy_template(conn, cur.lastrowid, child_key)
        return
    child_id = row['id']
    if not row['avatar_key']:
        conn.execute('UPDATE children SET avatar_key=? WHERE id=?', (child['avatar'], child_id))
    for old, new_name in OLD_TO_CANONICAL.get(child_key, {}).items():
        old_row = conn.execute('SELECT id FROM tasks WHERE child_id=? AND description=?', (child_id, old)).fetchone()
        new_row = conn.execute('SELECT id FROM tasks WHERE child_id=? AND description=?', (child_id, new_name)).fetchone()
        if old_row and not new_row:
            conn.execute('UPDATE tasks SET description=? WHERE id=?', (new_name, old_row['id']))
    existing = {r['description'] for r in conn.execute('SELECT description FROM tasks WHERE child_id=?', (child_id,))}
    next_order = conn.execute('SELECT COALESCE(MAX(sort_order),-1)+1 AS next_order FROM tasks WHERE child_id=?', (child_id,)).fetchone()[0]
    for category, description, points in child['tasks']:
        if description not in existing:
            conn.execute('INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)',
                         (child_id, category, description, points, next_order))
            next_order += 1


GOAL_SEEDS = [
    ('Kitap Kurdu', '7 gün üst üste kitap okursa', 7, 200),
    ('Satranç Ustası', '25 satranç maçı oynarsa', 25, 200),
    ('Kodlama Kahramanı', '15 kodlama görevi yaparsa', 15, 200),
    ('İngilizce Şampiyonu', '30 gün Duolingo çalışırsa', 30, 200),
    ('Ülkeler Şampiyonu', '15 ülkenin başkentini öğrenip haritasını çizerse', 15, 400),
    ('İyilik Elçisi', '20 iyilik görevi tamamlarsa', 20, 500),
    ('Yüzme Yıldızı', '15 yüzme antrenmanı yaparsa', 15, 1000),
    ('Sağlık Elçisi', '20 gün abur cubur ve ice tea olmadan geçirirse', 20, 5000),
    ('Yazın Süper Kaşifi', 'Tüm rozetleri tamamlarsa', 1, 7500),
    ('Aylık Görev Şampiyonu', '1 ay boyunca haftalık tüm görevleri yaparsa', 1, 10000),
]



def make_internal_username(family_slug, login_name):
    """Aynı görünen kullanıcı adını farklı ailelerde güvenle kullanmak için iç kimlik üretir."""
    return f"{family_slug}::{login_name}".lower()


def seed_family_templates_from_live_family(conn, family_id):
    """Bir ailenin mevcut çocuk ayarlarından tekrar kullanılabilir varsayılan şablonlar üretir."""
    task_rows = conn.execute(
        """SELECT t.category,t.description,t.points,t.sort_order
             FROM tasks t JOIN children c ON c.id=t.child_id
            WHERE c.family_id=? AND t.active=1
            ORDER BY c.id,t.sort_order,t.id""",
        (family_id,),
    ).fetchall()
    reward_rows = conn.execute(
        """SELECT r.required_points,r.description,r.sort_order
             FROM rewards r JOIN children c ON c.id=r.child_id
            WHERE c.family_id=?
            ORDER BY c.id,r.sort_order,r.id""",
        (family_id,),
    ).fetchall()
    goal_rows = conn.execute(
        """SELECT g.title,g.criteria,g.target_value,g.bonus_points,g.sort_order
             FROM goals g JOIN children c ON c.id=g.child_id
            WHERE c.family_id=? AND g.active=1
            ORDER BY c.id,g.sort_order,g.id""",
        (family_id,),
    ).fetchall()

    seen = set()
    order = 0
    for row in task_rows:
        key = (row['category'], row['description'], row['points'])
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            """INSERT INTO family_task_templates(family_id,category,description,points,sort_order)
               VALUES(?,?,?,?,?) ON CONFLICT DO NOTHING""",
            (family_id, row['category'], row['description'], row['points'], order),
        )
        order += 1

    seen = set()
    order = 0
    for row in reward_rows:
        key = (row['required_points'], row['description'])
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            """INSERT INTO family_reward_templates(family_id,required_points,description,sort_order)
               VALUES(?,?,?,?) ON CONFLICT DO NOTHING""",
            (family_id, row['required_points'], row['description'], order),
        )
        order += 1

    seen = set()
    order = 0
    for row in goal_rows:
        key = (row['title'], row['criteria'], row['target_value'], row['bonus_points'])
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            """INSERT INTO family_goal_templates(family_id,title,criteria,target_value,bonus_points,sort_order)
               VALUES(?,?,?,?,?,?) ON CONFLICT DO NOTHING""",
            (family_id, row['title'], row['criteria'], row['target_value'], row['bonus_points'], order),
        )
        order += 1


def clone_family_templates(conn, source_family_id, target_family_id):
    """Kaynak ailenin varsayılan görev, ödül ve hedeflerini yeni aileye kopyalar."""
    seed_family_templates_from_live_family(conn, source_family_id)
    conn.execute(
        """INSERT INTO family_task_templates(family_id,category,description,points,sort_order,active)
           SELECT ?,category,description,points,sort_order,active
             FROM family_task_templates WHERE family_id=?
           ON CONFLICT DO NOTHING""",
        (target_family_id, source_family_id),
    )
    conn.execute(
        """INSERT INTO family_reward_templates(family_id,required_points,description,sort_order,active)
           SELECT ?,required_points,description,sort_order,active
             FROM family_reward_templates WHERE family_id=?
           ON CONFLICT DO NOTHING""",
        (target_family_id, source_family_id),
    )
    conn.execute(
        """INSERT INTO family_goal_templates(family_id,title,criteria,target_value,bonus_points,sort_order,active)
           SELECT ?,title,criteria,target_value,bonus_points,sort_order,active
             FROM family_goal_templates WHERE family_id=?
           ON CONFLICT DO NOTHING""",
        (target_family_id, source_family_id),
    )


def copy_family_defaults_to_child(conn, family_id, child_id):
    """Aile varsayılanlarını yeni çocuğun düzenlenebilir kişisel kayıtlarına kopyalar."""
    counts = {'tasks': 0, 'rewards': 0, 'goals': 0}
    for row in conn.execute(
        """SELECT category,description,points,sort_order
             FROM family_task_templates
            WHERE family_id=? AND active=1 ORDER BY sort_order,id""",
        (family_id,),
    ).fetchall():
        conn.execute(
            "INSERT INTO tasks(child_id,category,description,points,sort_order) VALUES(?,?,?,?,?)",
            (child_id, row['category'], row['description'], row['points'], row['sort_order']),
        )
        counts['tasks'] += 1

    for row in conn.execute(
        """SELECT required_points,description,sort_order
             FROM family_reward_templates
            WHERE family_id=? AND active=1 ORDER BY sort_order,id""",
        (family_id,),
    ).fetchall():
        conn.execute(
            "INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)",
            (child_id, row['required_points'], row['description'], row['sort_order']),
        )
        counts['rewards'] += 1

    for row in conn.execute(
        """SELECT title,criteria,target_value,bonus_points,sort_order
             FROM family_goal_templates
            WHERE family_id=? AND active=1 ORDER BY sort_order,id""",
        (family_id,),
    ).fetchall():
        goal = conn.execute(
            """INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order)
               VALUES(?,?,?,?,?,?)""",
            (child_id, row['title'], row['criteria'], row['target_value'], row['bonus_points'], row['sort_order']),
        )
        conn.execute("INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)", (goal.lastrowid,))
        counts['goals'] += 1
    return counts



def import_bundled_sqlite_if_empty(conn):
    """İlk PostgreSQL kurulumunda repodaki mevcut familyhero.db verilerini bir kez taşır."""
    if conn.execute('SELECT 1 FROM children LIMIT 1').fetchone():
        return
    sqlite_path = BASE_DIR / 'familyhero.db'
    if not sqlite_path.exists():
        return
    import sqlite3
    source = sqlite3.connect(sqlite_path)
    source.row_factory = sqlite3.Row
    try:
        child_map, task_map, reward_map, goal_map = {}, {}, {}, {}
        for row in source.execute('SELECT * FROM children ORDER BY id'):
            cur = conn.execute(
                'INSERT INTO children(child_key,name,email,title,password_hash,avatar_key) VALUES(?,?,?,?,?,?)',
                (row['child_key'], row['name'], row['email'] if 'email' in row.keys() else None,
                 row['title'], row['password_hash'], row['avatar_key'])
            )
            child_map[row['id']] = cur.lastrowid
        for row in source.execute('SELECT * FROM tasks ORDER BY id'):
            cur = conn.execute(
                'INSERT INTO tasks(child_id,category,description,points,sort_order,active) VALUES(?,?,?,?,?,?)',
                (child_map[row['child_id']], row['category'], row['description'], row['points'], row['sort_order'], row['active'])
            )
            task_map[row['id']] = cur.lastrowid
        for row in source.execute('SELECT * FROM rewards ORDER BY id'):
            cur = conn.execute(
                'INSERT INTO rewards(child_id,required_points,description,sort_order) VALUES(?,?,?,?)',
                (child_map[row['child_id']], row['required_points'], row['description'], row['sort_order'])
            )
            reward_map[row['id']] = cur.lastrowid
        for row in source.execute('SELECT * FROM completions ORDER BY id'):
            conn.execute(
                'INSERT INTO completions(task_id,completion_date,note,created_at,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(task_id,completion_date) DO NOTHING',
                (task_map[row['task_id']], row['completion_date'], row['note'] if 'note' in row.keys() else '',
                 row['created_at'] if 'created_at' in row.keys() else datetime.now().isoformat(),
                 row['updated_at'] if 'updated_at' in row.keys() else (row['created_at'] if 'created_at' in row.keys() else datetime.now().isoformat()))
            )
        try:
            for row in source.execute('SELECT * FROM goals ORDER BY id'):
                cur = conn.execute(
                    'INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order,active) VALUES(?,?,?,?,?,?,?)',
                    (child_map[row['child_id']], row['title'], row['criteria'], row['target_value'], row['bonus_points'], row['sort_order'], row['active'])
                )
                goal_map[row['id']] = cur.lastrowid
            for row in source.execute('SELECT * FROM goal_progress ORDER BY id'):
                conn.execute(
                    'INSERT INTO goal_progress(goal_id,current_value,completed_date,note,updated_at) VALUES(?,?,?,?,?)',
                    (goal_map[row['goal_id']], row['current_value'], row['completed_date'], row['note'], row['updated_at'])
                )
        except sqlite3.OperationalError:
            pass
        try:
            for row in source.execute('SELECT * FROM reward_grants ORDER BY id'):
                conn.execute(
                    'INSERT INTO reward_grants(child_id,reward_id,description,grant_date,note,created_at) VALUES(?,?,?,?,?,?)',
                    (child_map[row['child_id']], reward_map.get(row['reward_id']), row['description'], row['grant_date'], row['note'], row['created_at'])
                )
        except sqlite3.OperationalError:
            pass
    finally:
        source.close()

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS children (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT,
            child_key TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            title TEXT NOT NULL DEFAULT 'Süper Kaşif',
            password_hash TEXT,
            avatar_key TEXT NOT NULL DEFAULT 'scientist',
            birth_date DATE,
            favorite_team TEXT NOT NULL DEFAULT '',
            school TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id BIGSERIAL PRIMARY KEY,
            child_id BIGINT NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            points INTEGER NOT NULL CHECK(points >= 0),
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS rewards (
            id BIGSERIAL PRIMARY KEY,
            child_id BIGINT NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            required_points INTEGER NOT NULL,
            description TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS completions (
            id BIGSERIAL PRIMARY KEY,
            task_id BIGINT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            completion_date DATE NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(task_id, completion_date)
        );
        CREATE TABLE IF NOT EXISTS admins (
            id BIGSERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reward_grants (
            id BIGSERIAL PRIMARY KEY,
            child_id BIGINT NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            reward_id BIGINT REFERENCES rewards(id) ON DELETE SET NULL,
            description TEXT NOT NULL DEFAULT '',
            grant_date DATE NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goals (
            id BIGSERIAL PRIMARY KEY,
            child_id BIGINT NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            criteria TEXT NOT NULL DEFAULT '',
            target_value INTEGER NOT NULL DEFAULT 1,
            bonus_points INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS goal_progress (
            id BIGSERIAL PRIMARY KEY,
            goal_id BIGINT NOT NULL UNIQUE REFERENCES goals(id) ON DELETE CASCADE,
            current_value INTEGER NOT NULL DEFAULT 0,
            completed_date DATE,
            note TEXT NOT NULL DEFAULT '',
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS family_polls (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            poll_date DATE NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS family_poll_options (
            id BIGSERIAL PRIMARY KEY,
            poll_id BIGINT NOT NULL REFERENCES family_polls(id) ON DELETE CASCADE,
            option_text TEXT NOT NULL,
            emoji TEXT NOT NULL DEFAULT '•',
            sort_order INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS family_poll_votes (
            id BIGSERIAL PRIMARY KEY,
            poll_id BIGINT NOT NULL REFERENCES family_polls(id) ON DELETE CASCADE,
            option_id BIGINT NOT NULL REFERENCES family_poll_options(id) ON DELETE CASCADE,
            child_id BIGINT NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(poll_id, child_id)
        );

        /* Sprint 2 foundation: organization-aware identity and authorization.
           Existing children/admins remain operational during the transition. */
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT,
            user_type TEXT NOT NULL DEFAULT 'member',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            must_change_password INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS families (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'active',
            created_by_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS family_memberships (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            member_kind TEXT NOT NULL DEFAULT 'adult',
            child_id BIGINT REFERENCES children(id) ON DELETE SET NULL,
            login_name TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(family_id,user_id),
            UNIQUE(family_id,child_id)
        );
        CREATE TABLE IF NOT EXISTS family_task_templates (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            points INTEGER NOT NULL CHECK(points >= 0),
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(family_id,category,description,points)
        );
        CREATE TABLE IF NOT EXISTS family_reward_templates (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
            required_points INTEGER NOT NULL,
            description TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(family_id,required_points,description)
        );
        CREATE TABLE IF NOT EXISTS family_goal_templates (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            criteria TEXT NOT NULL DEFAULT '',
            target_value INTEGER NOT NULL DEFAULT 1,
            bonus_points INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(family_id,title,criteria,target_value,bonus_points)
        );
        CREATE TABLE IF NOT EXISTS roles (
            id BIGSERIAL PRIMARY KEY,
            role_key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            scope TEXT NOT NULL DEFAULT 'family',
            system_role INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS permissions (
            id BIGSERIAL PRIMARY KEY,
            permission_key TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
            PRIMARY KEY(role_id,permission_id)
        );
        CREATE TABLE IF NOT EXISTS membership_roles (
            membership_id BIGINT NOT NULL REFERENCES family_memberships(id) ON DELETE CASCADE,
            role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            PRIMARY KEY(membership_id,role_id)
        );
        CREATE TABLE IF NOT EXISTS audit_logs (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT REFERENCES families(id) ON DELETE SET NULL,
            actor_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            action_key TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT,
            before_data TEXT,
            after_data TEXT,
            request_ip TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedback_items (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT REFERENCES families(id) ON DELETE SET NULL,
            created_by_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            category TEXT NOT NULL DEFAULT 'general',
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'received',
            priority TEXT NOT NULL DEFAULT 'normal',
            app_version TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS feedback_comments (
            id BIGSERIAL PRIMARY KEY,
            feedback_id BIGINT NOT NULL REFERENCES feedback_items(id) ON DELETE CASCADE,
            author_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            comment_text TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS activity_page_views (
            id BIGSERIAL PRIMARY KEY,
            family_id BIGINT REFERENCES families(id) ON DELETE SET NULL,
            user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
            child_id BIGINT REFERENCES children(id) ON DELETE SET NULL,
            actor_type TEXT NOT NULL,
            username TEXT,
            endpoint TEXT,
            path TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.execute('CREATE INDEX IF NOT EXISTS idx_activity_page_views_lookup ON activity_page_views(family_id, user_id, child_id, created_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_activity_page_views_created_at ON activity_page_views(created_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_audit_logs_action_created ON audit_logs(action_key, created_at)')
        conn.execute('ALTER TABLE children ADD COLUMN IF NOT EXISTS family_id BIGINT')
        conn.execute('ALTER TABLE family_polls ADD COLUMN IF NOT EXISTS family_id BIGINT')
        conn.execute('ALTER TABLE children ADD COLUMN IF NOT EXISTS email TEXT')
        conn.execute('ALTER TABLE children ADD COLUMN IF NOT EXISTS birth_date DATE')
        conn.execute("ALTER TABLE children ADD COLUMN IF NOT EXISTS favorite_team TEXT NOT NULL DEFAULT ''")
        conn.execute("ALTER TABLE children ADD COLUMN IF NOT EXISTS school TEXT NOT NULL DEFAULT ''")
        conn.execute('ALTER TABLE children ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP')
        conn.execute('ALTER TABLE children ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP')
        conn.execute('ALTER TABLE completions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP')
        conn.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password INTEGER NOT NULL DEFAULT 0')
        conn.execute('ALTER TABLE family_memberships ADD COLUMN IF NOT EXISTS login_name TEXT')
        conn.execute('UPDATE family_memberships fm SET login_name=u.username FROM users u WHERE fm.user_id=u.id AND (fm.login_name IS NULL OR fm.login_name=\'\')')
        conn.execute('UPDATE family_memberships fm SET login_name=c.child_key FROM children c WHERE fm.child_id=c.id')
        conn.execute("UPDATE family_memberships SET login_name='member-' || id WHERE login_name IS NULL OR login_name=''")
        conn.execute('''WITH ranked AS (
                            SELECT id,ROW_NUMBER() OVER(PARTITION BY family_id,LOWER(login_name) ORDER BY id) AS rn
                              FROM family_memberships
                       )
                       UPDATE family_memberships fm
                          SET login_name=fm.login_name || '-' || ranked.rn
                         FROM ranked
                        WHERE fm.id=ranked.id AND ranked.rn>1''')
        conn.execute('ALTER TABLE family_memberships ALTER COLUMN login_name SET NOT NULL')
        conn.execute('ALTER TABLE children DROP CONSTRAINT IF EXISTS children_child_key_key')
        conn.execute('DROP INDEX IF EXISTS children_child_key_key')
        conn.execute('DROP INDEX IF EXISTS children_family_child_key_unique')
        conn.execute('DROP INDEX IF EXISTS family_memberships_family_login_unique')

        # v4.33: Login names are globally unique. Keep the oldest/default-family
        # name and rename later duplicates deterministically before adding indexes.
        conn.execute('''WITH ranked AS (
                            SELECT fm.id,
                                   ROW_NUMBER() OVER(
                                       PARTITION BY LOWER(fm.login_name)
                                       ORDER BY CASE WHEN f.slug='default-family' THEN 0 ELSE 1 END, fm.id
                                   ) AS rn,
                                   f.slug
                              FROM family_memberships fm
                              JOIN families f ON f.id=fm.family_id
                       )
                       UPDATE family_memberships fm
                          SET login_name=ranked.slug || '-' || fm.login_name || '-' || fm.id
                         FROM ranked
                        WHERE fm.id=ranked.id AND ranked.rn>1''')
        conn.execute('''UPDATE children c
                           SET child_key=fm.login_name
                          FROM family_memberships fm
                         WHERE fm.child_id=c.id AND LOWER(c.child_key)<>LOWER(fm.login_name)''')
        conn.execute('''UPDATE users u
                           SET username=fm.login_name
                          FROM family_memberships fm
                         WHERE fm.user_id=u.id AND LOWER(u.username)<>LOWER(fm.login_name)''')
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS family_memberships_login_global_unique ON family_memberships(LOWER(login_name))')
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS children_child_key_global_unique ON children(LOWER(child_key))')
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_global_unique ON users(LOWER(username))')
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS children_email_unique ON children (LOWER(email)) WHERE email IS NOT NULL')
        import_bundled_sqlite_if_empty(conn)
        admin_row = conn.execute("SELECT id,password_hash FROM admins WHERE username='admin'").fetchone()
        if not admin_row:
            admin_hash = generate_password_hash(
                _seed_password("FAMILYHERO_ADMIN_PASSWORD", "admin kullanıcısı")
            )
            cur = conn.execute(
                'INSERT INTO admins(username,password_hash) VALUES(?,?)',
                ('admin', admin_hash),
            )
            admin_row = {'id': cur.lastrowid, 'password_hash': admin_hash}

        family = conn.execute(
            "INSERT INTO families(name,slug) VALUES(?,?) ON CONFLICT(slug) DO UPDATE SET name=excluded.name RETURNING id",
            ('FamilyHero Ailesi','default-family'),
        ).fetchone()
        family_id = family['id']
        conn.execute('UPDATE children SET family_id=? WHERE family_id IS NULL', (family_id,))
        conn.execute('UPDATE family_polls SET family_id=? WHERE family_id IS NULL', (family_id,))
        conn.execute('CREATE INDEX IF NOT EXISTS children_family_idx ON children(family_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS polls_family_idx ON family_polls(family_id)')

        roles = [
            ('platform_admin','Platform Yöneticisi','platform',1),
            ('family_owner','Aile Sahibi','family',1),
            ('family_admin','Aile Yöneticisi','family',1),
            ('parent','Ebeveyn','family',1),
            ('child','Çocuk','family',1),
        ]
        for role_key, role_name, scope, system_role in roles:
            conn.execute(
                "INSERT INTO roles(role_key,name,scope,system_role) VALUES(?,?,?,?) ON CONFLICT(role_key) DO UPDATE SET name=excluded.name,scope=excluded.scope",
                (role_key,role_name,scope,system_role),
            )

        permission_rows = [
            ('family.view','Aile alanını görüntüleme'),
            ('family.update','Aile ayarlarını değiştirme'),
            ('member.view','Aile üyelerini görüntüleme'),
            ('member.manage','Aile üyelerini yönetme'),
            ('task.view','Görevleri görüntüleme'),
            ('task.create','Görev oluşturma'),
            ('task.update','Görev düzenleme'),
            ('task.delete','Görev silme'),
            ('task.complete','Görev tamamlama'),
            ('reward.view','Ödülleri görüntüleme'),
            ('reward.manage','Ödülleri yönetme'),
            ('goal.manage','Hedef ve rozetleri yönetme'),
            ('poll.create','Oylama oluşturma'),
            ('poll.manage','Oylamaları yönetme'),
            ('poll.vote','Oylamaya katılma'),
            ('report.view','Raporları görüntüleme'),
            ('statistics.view','İstatistikleri görüntüleme'),
            ('feedback.create','Geri bildirim oluşturma'),
            ('feedback.manage','Geri bildirimleri yönetme'),
            ('audit.view','Denetim kayıtlarını görüntüleme'),
        ]
        for permission_key, description in permission_rows:
            conn.execute(
                "INSERT INTO permissions(permission_key,description) VALUES(?,?) ON CONFLICT(permission_key) DO UPDATE SET description=excluded.description",
                (permission_key,description),
            )

        admin_user = conn.execute(
            """INSERT INTO users(username,display_name,password_hash,user_type)
               VALUES(?,?,?,?)
               ON CONFLICT(username) DO UPDATE SET
                   display_name=excluded.display_name,
                   password_hash=COALESCE(users.password_hash,excluded.password_hash),
                   user_type=excluded.user_type
               RETURNING id""",
            ('admin','FamilyHero Yöneticisi',admin_row['password_hash'],'platform_admin'),
        ).fetchone()
        admin_membership = conn.execute(
            """INSERT INTO family_memberships(family_id,user_id,member_kind,login_name,status)
               VALUES(?,?,?,?,?)
               ON CONFLICT(family_id,user_id) DO UPDATE SET login_name=excluded.login_name,status='active'
               RETURNING id""",
            (family_id,admin_user['id'],'adult','admin','active'),
        ).fetchone()
        conn.execute(
            "UPDATE families SET created_by_user_id=COALESCE(created_by_user_id,?) WHERE id=?",
            (admin_user['id'], family_id),
        )

        for role_key in ('platform_admin','family_owner'):
            conn.execute(
                """INSERT INTO membership_roles(membership_id,role_id)
                   SELECT ?,id FROM roles WHERE role_key=?
                   ON CONFLICT DO NOTHING""",
                (admin_membership['id'],role_key),
            )

        all_permissions = [p[0] for p in permission_rows]
        child_permissions = ['family.view','task.view','task.complete','reward.view','poll.vote','feedback.create']
        role_permission_map = {
            'platform_admin': all_permissions,
            'family_owner': all_permissions,
            'family_admin': [p for p in all_permissions if p != 'audit.view'],
            'parent': [p for p in all_permissions if p not in {'audit.view','family.update'}],
            'child': child_permissions,
        }
        for role_key, permission_keys in role_permission_map.items():
            for permission_key in permission_keys:
                conn.execute(
                    """INSERT INTO role_permissions(role_id,permission_id)
                       SELECT r.id,p.id FROM roles r,permissions p
                        WHERE r.role_key=? AND p.permission_key=?
                       ON CONFLICT DO NOTHING""",
                    (role_key,permission_key),
                )

        for key, child in SEED_DATA.items():
            sync_seed_child(conn, key, child)

        for child_row in conn.execute('SELECT id,family_id,child_key,name,password_hash,email FROM children ORDER BY id').fetchall():
            family_row = conn.execute('SELECT slug FROM families WHERE id=?', (child_row['family_id'],)).fetchone()
            if not family_row:
                continue
            membership = conn.execute(
                'SELECT id,user_id FROM family_memberships WHERE family_id=? AND child_id=?',
                (child_row['family_id'], child_row['id']),
            ).fetchone()
            if membership:
                user = {'id': membership['user_id']}
                conn.execute(
                    '''UPDATE users SET username=?,display_name=?,email=COALESCE(?,email),
                              password_hash=COALESCE(password_hash,?),user_type='member',updated_at=CURRENT_TIMESTAMP
                         WHERE id=?''',
                    (child_row['child_key'], child_row['name'], child_row.get('email'), child_row['password_hash'], user['id']),
                )
                conn.execute(
                    "UPDATE family_memberships SET login_name=?,status='active' WHERE id=?",
                    (child_row['child_key'], membership['id']),
                )
            else:
                internal_username = child_row['child_key']
                user = conn.execute(
                    '''INSERT INTO users(email,username,display_name,password_hash,user_type)
                       VALUES(?,?,?,?,?)
                       ON CONFLICT(username) DO UPDATE SET
                           display_name=excluded.display_name,
                           email=COALESCE(excluded.email,users.email),
                           password_hash=COALESCE(users.password_hash,excluded.password_hash),
                           user_type='member'
                       RETURNING id''',
                    (child_row.get('email'), internal_username, child_row['name'], child_row['password_hash'], 'member'),
                ).fetchone()
                membership = conn.execute(
                    '''INSERT INTO family_memberships(family_id,user_id,member_kind,child_id,login_name,status)
                       VALUES(?,?,?,?,?,?)
                       ON CONFLICT(family_id,user_id) DO UPDATE SET
                           child_id=excluded.child_id,login_name=excluded.login_name,status='active'
                       RETURNING id''',
                    (child_row['family_id'], user['id'], 'child', child_row['id'], child_row['child_key'], 'active'),
                ).fetchone()
            conn.execute(
                '''INSERT INTO membership_roles(membership_id,role_id)
                   SELECT ?,id FROM roles WHERE role_key='child'
                   ON CONFLICT DO NOTHING''',
                (membership['id'],),
            )
        for child in conn.execute('SELECT id FROM children ORDER BY id').fetchall():
            if not conn.execute('SELECT 1 FROM goals WHERE child_id=? LIMIT 1', (child['id'],)).fetchone():
                for order, (title, criteria, target, points) in enumerate(GOAL_SEEDS):
                    cur = conn.execute('INSERT INTO goals(child_id,title,criteria,target_value,bonus_points,sort_order) VALUES(?,?,?,?,?,?)',
                                       (child['id'], title, criteria, target, points, order))
                    conn.execute('INSERT INTO goal_progress(goal_id,current_value) VALUES(?,0)', (cur.lastrowid,))


        seed_family_templates_from_live_family(conn, family_id)
        for other_family in conn.execute('SELECT id FROM families WHERE id<>? ORDER BY id', (family_id,)).fetchall():
            clone_family_templates(conn, family_id, other_family['id'])
