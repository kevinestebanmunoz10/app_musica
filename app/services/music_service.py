import os
from pathlib import Path
import yt_dlp

DOWNLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Render monta los "Secret Files" en /etc/secrets/<nombre>. Localmente, podés
# poner tu cookies.txt junto al proyecto y apuntar la variable de entorno
# COOKIES_FILE a esa ruta. Este archivo NUNCA debe subirse a GitHub.
COOKIES_FILE = os.getenv("COOKIES_FILE", "/etc/secrets/cookies.txt")

# Simula la app de Android de YouTube en vez del sitio web. Esto evita el
# bloqueo "Sign in to confirm you're not a bot" que YouTube aplica a
# peticiones que vienen desde IPs de servidores en la nube (Render, AWS, etc).
YOUTUBE_CLIENT_ARGS = {
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
        }
    }
}

if os.path.exists(COOKIES_FILE):
    YOUTUBE_CLIENT_ARGS["cookiefile"] = COOKIES_FILE


def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """Busca canciones en YouTube y devuelve metadata (sin descargar)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        **YOUTUBE_CLIENT_ARGS,
    }
    search_query = f"ytsearch{limit}:{query}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(search_query, download=False)
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
    ydl_opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "noplaylist": True,
        **YOUTUBE_CLIENT_ARGS,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return info["url"]


def download_track(video_id: str) -> str:
    """Descarga el audio en formato Opus (liviano) y devuelve la ruta local."""
    output_template = str(DOWNLOADS_DIR / f"{video_id}.%(ext)s")
    ydl_opts = {
        "quiet": True,
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
        **YOUTUBE_CLIENT_ARGS,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)

    return str(DOWNLOADS_DIR / f"{video_id}.opus")