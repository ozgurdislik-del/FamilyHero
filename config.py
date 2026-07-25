import os


class BaseConfig:
    ENVIRONMENT = os.environ.get("FAMILYHERO_ENV", "development").strip().lower()
    IS_PRODUCTION = ENVIRONMENT in {"production", "prod"} or bool(os.environ.get("RAILWAY_ENVIRONMENT"))

    SECRET_KEY = os.environ.get("FAMILYHERO_SECRET_KEY", "").strip()
    if IS_PRODUCTION and not SECRET_KEY:
        raise RuntimeError(
            "FAMILYHERO_SECRET_KEY zorunludur. Production ortamı güvenli anahtar olmadan başlatılamaz."
        )
    if not SECRET_KEY:
        # Yalnızca yerel geliştirme içindir. Production yukarıda fail-closed davranır.
        SECRET_KEY = "development-only-change-me"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION and os.environ.get(
        "FAMILYHERO_INSECURE_COOKIES", ""
    ).lower() != "true"
    PERMANENT_SESSION_LIFETIME_SECONDS = int(
        os.environ.get("FAMILYHERO_SESSION_LIFETIME_SECONDS", "43200")
    )
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024


class Config(BaseConfig):
    pass
