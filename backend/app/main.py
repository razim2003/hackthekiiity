from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv

_backend_dir = Path(__file__).resolve().parents[1]
_repo_root = _backend_dir.parent

for _env_path in (_backend_dir / ".env", _repo_root / ".env", _repo_root / ".env.example"):
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)

app = FastAPI(title="Pet Rescue & Rehoming System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Import routes
from app.routes.cats import router as cats_router

app.include_router(cats_router, prefix="/api/cats", tags=["cats"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
