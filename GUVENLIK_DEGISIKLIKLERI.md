# Güvenlik Düzeltmeleri — 25 Temmuz 2026

Bu sürümde önceki incelemede tespit edilen kritik güvenlik açıkları giderildi.

## 1. Sabit / tahmin edilebilir şifreler kaldırıldı
- `database.py` içindeki sabit admin şifresi (`FamilyHero2026!`) ve çocuk
  şifreleri (`Uzay123!`, `Toprak123!`) kaldırıldı.
- Artık şifreler ortam değişkenlerinden okunuyor:
  - `FAMILYHERO_ADMIN_PASSWORD`
  - `FAMILYHERO_CHILD_UZAY_PASSWORD`
  - `FAMILYHERO_CHILD_TOPRAK_PASSWORD`
- Bu değişkenler tanımlı değilse uygulama ilk kurulumda rastgele, güçlü bir
  şifre üretir ve bunu **deploy log'una** yazar. Kurulumdan sonra bu şifreyi
  not edip kalıcı bir env değişkeniyle değiştirin.

## 2. SECRET_KEY için tehlikeli sabit fallback kaldırıldı
- Eskiden `FAMILYHERO_SECRET_KEY` tanımlı değilse uygulama herkesçe bilinen
  sabit bir anahtarla (`familyhero-local-key`) çalışıyordu; bu, oturum
  çerezlerinin ve şifre sıfırlama linklerinin sahteleştirilebilmesi anlamına
  geliyordu.
- Artık env değişkeni yoksa her başlangıçta rastgele, tahmin edilemez bir
  anahtar üretiliyor (ve log'a uyarı yazılıyor). **Production'da bu env
  değişkenini mutlaka sabit bir değerle tanımlayın**, aksi halde her
  yeniden başlamada tüm oturumlar/linkler geçersiz olur.

## 3. CSRF koruması eklendi
- `Flask-WTF` (`CSRFProtect`) kuruldu; tüm state değiştiren POST
  endpoint'leri artık geçerli bir CSRF token gerektiriyor.
- 27 formun tamamına otomatik olarak gizli `csrf_token` alanı eklendi.
- Token olmadan yapılan POST istekleri `400 Bad Request` ile reddediliyor
  (test edildi).

## 4. Brute-force / rate limit koruması eklendi
- `Flask-Limiter` kuruldu.
- `/` (çocuk girişi), `/admin/login` ve `/forgot-password` endpoint'lerine
  dakikada sınırlı deneme hakkı getirildi (10/dk, 10/dk, 5/dk).
- Not: Varsayılan olarak bellek-içi (in-memory) depolama kullanılıyor; tek
  instance için yeterli. Railway'de birden fazla instance/worker
  çalıştırırsanız `Flask-Limiter`'a Redis gibi paylaşılan bir depolama
  bağlamanız gerekir.

## 5. Session çerezi sertleştirildi
- `SESSION_COOKIE_HTTPONLY=True`
- `SESSION_COOKIE_SAMESITE="Lax"`
- `SESSION_COOKIE_SECURE=True` (yalnızca HTTPS üzerinden gönderilir;
  yerelde HTTP ile test ediyorsanız `FAMILYHERO_INSECURE_COOKIES=true`
  env değişkeniyle geçici olarak kapatabilirsiniz)

## 6. Minimum şifre uzunlukları artırıldı
- Çocuk hesabı oluştururken minimum şifre uzunluğu 4 → **8** karaktere
  çıkarıldı.
- Şifre sıfırlamada minimum uzunluk 6 → **8** karaktere çıkarıldı
  (şablon ve sunucu tarafı doğrulaması güncellendi).

## 7. Küçük temizlik
- Hiç kullanılmayan boş `static/admin_v08.css` dosyası silindi.

---

## Railway'de yapmanız gerekenler
`RAILWAY_KURULUM.txt` dosyasındaki "2.1. GÜVENLİK (ZORUNLU)" bölümünü
okuyup şu değişkenleri Variables kısmına ekleyin:

```
FAMILYHERO_SECRET_KEY=<uzun rastgele bir anahtar>
FAMILYHERO_ADMIN_PASSWORD=<güçlü bir admin şifresi>
FAMILYHERO_CHILD_UZAY_PASSWORD=<Uzay için şifre>
FAMILYHERO_CHILD_TOPRAK_PASSWORD=<Toprak için şifre>
```

## Bilinçli olarak kapsam dışı bırakılanlar
Önceki incelemede bahsedilen kod organizasyonu / okunabilirlik önerileri
(app.py'nin blueprint'lere bölünmesi, şablonların minify edilmeden
tutulması, seed verilerinin koddan config'e taşınması vb.) bu düzenlemeye
dahil edilmedi; bunlar işlevi bozma riski taşıyan daha büyük çaplı
yeniden yapılandırmalar olduğu için ayrı bir çalışma olarak ele alınmalı.
