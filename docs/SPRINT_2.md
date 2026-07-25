# Sprint 2 — Foundation

## Amaç

FamilyHero'yu tek aileli çalışan uygulamadan çok aileli, yetki kontrollü ve izlenebilir ürün mimarisine taşımak; aynı zamanda kritik mobil UX sorunlarını çözmek.

## Bu teslimde tamamlananlar

- [x] Günün Bilgisi alanı hero butonundan ayrıldı.
- [x] Mobil hero butonunun tıklanabilirliği güvence altına alındı.
- [x] Oylama seçenekleri büyük, renkli kart düzenine geçirildi.
- [x] Yönetici oylama ekranına hızlı ikon paleti eklendi.
- [x] Multi-family geçiş tabloları eklendi.
- [x] RBAC temel tabloları ve başlangıç izin kataloğu eklendi.
- [x] Audit log ve feedback temel tabloları eklendi.
- [x] Ürün ve mimari dokümantasyon yapısı oluşturuldu.

## Sonraki adımlar

- Yeni kullanıcı kimliğini mevcut çocuk/admin oturumlarına bağlayan geçiş servisi.
- `current_user.can(permission)` yetki servisi ve decorator'lar.
- Aile seçici ve aile yönetim ekranları.
- Feedback Center ekranları.
- Audit kayıtlarının kritik işlemlere bağlanması.
- Çoklu seçimli anketin veri modeli ve kullanıcı akışı.
