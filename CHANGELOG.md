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
