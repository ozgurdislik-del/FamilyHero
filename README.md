# FamilyHero

FamilyHero, aile içi görev, puan, hedef, ödül ve oylama uygulamasıdır.

## Yerel/Production yapılandırması

1. `.env.example` dosyasındaki değişkenleri kendi ortamınızda tanımlayın.
2. PostgreSQL `DATABASE_URL` sağlayın.
3. Production için `FAMILYHERO_ENV=production` ve güçlü bir `FAMILYHERO_SECRET_KEY` zorunludur.
4. Bağımlılıkları kurun: `pip install -r requirements.txt`
5. Uygulamayı başlatın: `python app.py`

Railway başlangıç komutu `Procfile` içindedir:

```text
web: gunicorn app:app
```

Güvenlik ayrıntıları için `docs/SECURITY.md`, teslim kapsamı için `SPRINT2A_REPORT.md` dosyasını okuyun.
