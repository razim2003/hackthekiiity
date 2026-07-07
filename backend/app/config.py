from functools import lru_cache
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


_backend_dir = Path(__file__).resolve().parents[1]
_repo_root = _backend_dir.parent

for _env_path in (_backend_dir / ".env", _repo_root / ".env", _repo_root / ".env.example"):
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_storage_bucket: str = "pet-pics"
    enable_ai_matching: bool = True
    allowed_cat_statuses: Tuple[str, ...] = ("lost", "found", "stray", "adoptable")

    model_config = SettingsConfigDict(env_file=None, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
