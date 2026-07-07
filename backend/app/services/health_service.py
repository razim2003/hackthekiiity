from app.config import get_settings
from app.database.connection import supabase


def check_supabase_status() -> dict:
    settings = get_settings()
    checks = {
        "database": {"ok": False},
        "contact_columns": {"ok": False},
        "storage": {"ok": False, "bucket": settings.supabase_storage_bucket},
    }

    try:
        supabase.table("cats").select("id").limit(1).execute()
        checks["database"]["ok"] = True
    except Exception as exc:
        checks["database"]["error"] = str(exc)

    try:
        supabase.table("cats").select("owner_name,contact_phone,contact_email").limit(1).execute()
        checks["contact_columns"]["ok"] = True
    except Exception as exc:
        checks["contact_columns"]["error"] = (
            "Run database/add_contact_fields.sql in Supabase SQL Editor. "
            f"Details: {exc}"
        )

    try:
        supabase.storage.get_bucket(settings.supabase_storage_bucket)
        checks["storage"]["ok"] = True
    except Exception as exc:
        checks["storage"]["error"] = str(exc)

    return {
        "status": "healthy" if all(check["ok"] for check in checks.values()) else "degraded",
        "checks": checks,
    }
