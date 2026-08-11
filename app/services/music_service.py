import os
import shutil
from pathlib import Path
import yt_dlp

DOWNLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Render monta los "Secret Files" en /etc/secrets/<nombre> como SOLO LECTURA,
# pero yt-dlp necesita poder reescribir el archivo de cookies tras usarlo.
# Por eso lo copiamos a una carpeta escribible antes de usarlo.
_SECRET_COOKIES_PATH = os.getenv("COOKIES_FILE", "/etc/secrets/cookies.txt")
COOKIES_FILE = str(DOWNLOADS_DIR.parent / "cookies_writable.txt")

if os.path.exists(_SECRET_COOKIES_PATH):
    shutil.copyfile(_SECRET_COOKIES_PATH, COOKIES_FILE)
elif os.path.exists(_SECRET_COOKIES_PATH.lstrip("/")):
    shutil.copyfile(_SECRET_COOKIES_PATH.lstrip("/"), COOKIES_FILE)

_HAS_COOKIES = os.path.exists(COOKIES_FILE)

# YouTube bloquea distinto según qué "cliente" (app/sitio) simula yt-dlp.
# En vez de fijar uno solo, probamos varios en orden hasta que alguno
# funcione: esto compensa que el bloqueo cambia con el tiempo y según IP.
CLIENT_ATTEMPTS = [["tv"], ["ios"], ["android"], ["web", "android"]]


def _base_opts() -> dict:
    opts = {"quiet": True, "no_warnings": True}
    if _HAS_COOKIES:
        opts["cookiefile"] = COOKIES_FILE
    return opts


def _extract_with_fallback(url_or_query: str, extra_opts: dict, download: bool = False):
    """Intenta extraer info probando distintos clientes de YouTube en orden,
    hasta que uno funcione. Lanza la última excepción si todos fallan."""
    last_error = None
    for clients in CLIENT_ATTEMPTS:
        ydl_opts = {
            **_base_opts(),
            **extra_opts,
            "extractor_args": {"youtube": {"player_client": clients}},
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url_or_query, download=download)
        except Exception as e:
            last_error = e
            continue
    raise last_error


def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """Busca canciones en YouTube y devuelve metadata (sin descargar)."""
    search_query = f"ytsearch{limit}:{query}"
    result = _extract_with_fallback(
        search_query,
        {"extract_flat": True, "skip_download": True},
        download=False,
    )
    entries = [e for e in (result.get("entries") or []) if e]

    return [
        {
            "external_id": entry.get("id"),
            "title": entry.get("title"),
            "artist": entry.get("uploader") or entry.get("channel"),
            "duration_ms": (entry.get("duration") or 0) * 1000,
            "thumbnail_url": entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else None,
        }
        for entry in entries
    ]


def get_stream_url(video_id: str) -> str:
    """Obtiene una URL de audio directa para streaming (no descarga a disco)."""
    info = _extract_with_fallback(
        f"https://www.youtube.com/watch?v={video_id}",
        {"format": "bestaudio/best", "noplaylist": True},
        download=False,
    )
    return info["url"]


def download_track(video_id: str) -> str:
    """Descarga el audio en formato Opus (liviano) y devuelve la ruta local."""
    output_template = str(DOWNLOADS_DIR / f"{video_id}.%(ext)s")
    _extract_with_fallback(
        f"https://www.youtube.com/watch?v={video_id}",
        {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "opus",
                    "preferredquality": "128",
                }
            ],
        },
        download=True,
    )
    return str(DOWNLOADS_DIR / f"{video_id}.opus")