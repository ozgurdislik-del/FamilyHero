# FamilyHero Security Baseline

## Zorunlu production değişkenleri

- `FAMILYHERO_ENV=production`
- `FAMILYHERO_SECRET_KEY`
- `DATABASE_URL`
- İlk kurulumda hesap yoksa ilgili seed şifre değişkenleri

Production ortamı `FAMILYHERO_SECRET_KEY` olmadan başlamaz.

## Uygulanan kontroller

- Flask-WTF genel CSRF koruması
- Login ve şifre sıfırlama uçlarında rate limit
- `HttpOnly`, `SameSite=Lax`, production için `Secure` session çerezi
- RBAC tabloları ve `permission_required` route koruması
- Kritik yönetim işlemleri için audit kayıtları
- Kaynak kodda sabit seed şifresi bulunmaması
- `.env`, veritabanı ve log dosyalarının Git dışında tutulması

## Veri paylaşımı

Gerçek çocuk verisi içeren PostgreSQL dump veya SQLite dosyası kod inceleme paketine eklenmemelidir. Test ve demo paketleri sentetik veri kullanmalıdır.

## Secret rotation

`FAMILYHERO_SECRET_KEY` değiştirilirse mevcut session'lar ve eski şifre sıfırlama token'ları geçersiz olur. Planlı bakım dışında değiştirilmemelidir.
