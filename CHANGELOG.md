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
