import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Resolve env files relative to this file so startup works from any working directory.
_backend_dir = Path(__file__).resolve().parents[2]
_repo_root = _backend_dir.parent

for _env_path in (_backend_dir / ".env", _repo_root / ".env", _repo_root / ".env.example"):
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)

supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
        "Create backend/.env or .env at the repo root (you can copy from .env.example)."
    )

supabase: Client = create_client(supabase_url, supabase_key)
