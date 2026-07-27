# 4.32.3-beta — Görev/Ödül/Hedef Panelinde Kategori Seçimi ve Tek Buton

- Sol kategori listesinden bir öğeye tıklamak artık sağda **yalnızca o kategoriyi** açık gösteriyor (önceden tıklanan kategori açılıyor ama diğerleri de açık kalabiliyordu). Seçili kategori sol listede vurgulanıyor.
- "Tümünü daralt" / "Tümünü aç" iki ayrı buton yerine **tek bir buton** oldu: en az bir grup açıksa buton "Tümünü daralt" yazıyor ve tıklanınca hepsini kapatıp kendini "Tümünü aç" olarak güncelliyor; hepsi kapalıyken de tersi oluyor.
- Bu tek buton artık yalnızca Görevler'de değil, **Ödüller** ve **Hedefler** bölümlerinde de var (önceden bu ikisinde hiç toplu aç/kapat kontrolü yoktu).

# 4.32.2-beta — Yönetici Girişi ve Tasarım Tutarlılığı Düzeltmeleri

## Kod düzeltmeleri
- **Ölü uç nokta düzeltildi:** `/admin/login` artık gerçek bir giriş ekranı sunuyor. Önceden bu route sadece `login?mode=adult` adresine yönlendiriyordu; bu yüzden `templates/admin_login.html` hiçbir zaman render edilmiyordu (kod tabanında hiçbir `render_template("admin_login.html")` çağrısı yoktu) ve kartı güncelleyen kimse fark etmiyordu.
- **Yönetici girişi artık tek adımda çalışıyor:** Kullanıcı adı platform genelinde zaten benzersiz olduğu için (`users.username UNIQUE`), yöneticiler/aile sahipleri/süper adminler önce aileyi arayıp sonra kendini listeden seçmek zorunda kalmadan doğrudan kullanıcı adı + şifre ile giriş yapabiliyor. Aile/çocuk girişi (`/` , step'li arama akışı) olduğu gibi korundu.
- Yeni giriş ucu için de `10/dakika` rate limit ve başarısız/başarılı girişler için audit log eklendi (`auth.admin_login.failed`, `auth.login.success`).

## Tasarım düzeltmeleri
- `static/style.css` içinde, hiçbir class/media query ile sınırlanmamış tamamlanmamış bir "FamilyHero 2.2 — Compact Corporate UI" taslağı; `body`, `.auth-card`, `.auth-shell`, `.flash`, `.sidebar`, `.admin-layout`, buton/input gibi temel seçicileri asıl temadan **sonra** yeniden tanımlayıp CSS cascade'inde sessizce kazanıyordu. Sonuç: tüm site (özellikle giriş ve yönetici/süper admin giriş ekranları) tasarlanandan daha küçük fontlu, düz köşeli (4px yerine 18-22px radius) ve donuk gölgeli görünüyordu. Bu çakışan blok kaldırıldı; yalnızca hâlâ kullanılan birkaç CSS değişkeni (`--fh-border` vb.) korundu.
- `templates/admin_login.html` sıfırdan, sitenin geri kalanıyla aynı `auth-shell`/`auth-card` tasarım diline uygun şekilde yeniden yazıldı; hata mesajları artık `base.html`'deki ortak `flash` mekanizmasıyla gösteriliyor.

# 4.32.0-beta — Aile ve Üye Seçimli Giriş

- Giriş akışı aile arama → üye seçme → şifre olarak yenilendi.
- Aynı görünen kullanıcı adı farklı ailelerde kullanılabilir hale getirildi.
- Yeni ailelere ana ailenin görev, ödül ve hedef varsayılanları kopyalanır.
- Yeni çocuk eklenince aile varsayılanları otomatik uygulanır.
- Süper admin aile listesine sunucu taraflı arama, otomatik filtreleme ve 50 sonuç sınırı eklendi.
- Çocuk kullanıcı anahtarı benzersizliği platform geneli yerine aile bazına taşındı.

# 4.31.1-beta — Aile Oluşturma Düzeltmesi

- PostgreSQL üzerinde aile oluştururken oluşan `membership_roles ... RETURNING id` hatası düzeltildi.
- Aile yöneticisi ve çocuk rol atamaları güvenli bir yardımcı fonksiyonda toplandı.
- Rol bulunamadığında işlem transaction ile geri alınır; yarım aile kaydı bırakılmaz.

# 4.31.0-beta — Super Admin Aile Yönetimi

- Süper admin menüsüne **Aile Yönetimi** ekranı eklendi.
- Aileler tek ekrandan listelenebilir ve yeni test ailesi oluşturulabilir.
- Süper admin, seçtiği ailenin yönetim çalışma alanına geçebilir.
- Aile kodu, kullanıcı adı ve e-posta çakışmaları alan bazında gösterilir.
- Aile adı girildiğinde aile kodu ve benzersiz yönetici kullanıcı adı önerilir.
- Platform admin yetkilendirmesi aile değiştirme senaryosu için düzeltildi.

# Changelog

## 4.20.0-sprint2a

- Production için fail-closed SECRET_KEY yapılandırması
- Tahmin edilebilir seed çocuk şifrelerinin kaldırılması
- RBAC uyumluluk köprüsü, permission service ve route kontrolleri
- Kritik yönetim işlemleri için audit log desteği
- `.gitignore`, `.env.example` ve güvenlik dokümantasyonu
- Güvenlik kodunun servis modüllerine ayrılması
