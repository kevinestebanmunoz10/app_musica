from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import songs, music
from app.config import get_settings

settings = get_settings()

# Crea las tablas si no existen (para SQLite esto es suficiente al inicio)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# Permite que la app móvil/web (Capacitor) llame al backend sin bloqueos CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: restringe a tu dominio/app real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router)
app.include_router(music.router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health")
def health():
    return {"status": "healthy"}
