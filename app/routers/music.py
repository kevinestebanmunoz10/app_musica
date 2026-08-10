from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import httpx

from app.services import music_service
from app.database import get_db
from app.models.models import Song

router = APIRouter(prefix="/music", tags=["music"])


@router.post("/library/add")
def add_to_library(video_id: str, title: str, artist: str, duration_ms: int = None,
                    thumbnail_url: str = None, db: Session = Depends(get_db)):
    """Guarda una canción encontrada en la búsqueda a la biblioteca, sin descargarla."""
    existing = db.query(Song).filter(Song.source == "youtube", Song.external_id == video_id).first()
    if existing:
        return existing

    song = Song(
        title=title,
        artist=artist,
        source="youtube",
        external_id=video_id,
        duration_ms=duration_ms,
        thumbnail_url=thumbnail_url,
    )
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.get("/library/downloaded")
def list_downloaded(db: Session = Depends(get_db)):
    """Lista solo las canciones que ya están descargadas localmente."""
    return db.query(Song).filter(Song.local_file_path.isnot(None)).all()


@router.get("/search")
def search(q: str, limit: int = 10):
    if not q.strip():
        raise HTTPException(status_code=400, detail="La búsqueda no puede estar vacía")
    try:
        return music_service.search_tracks(q, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error buscando en YouTube: {e}")


@router.get("/stream/{video_id}")
async def stream(video_id: str, request: Request):
    """Actúa como puente: el backend pide el audio a YouTube (misma IP que
    obtuvo la URL firmada) y se lo reenvía al navegador/celular, en vez de
    redirigir directamente (YouTube rechaza la URL si la pide otra IP)."""
    try:
        url = music_service.get_stream_url(video_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error obteniendo el stream: {e}")

    range_header = request.headers.get("range")
    headers = {"User-Agent": "Mozilla/5.0"}
    if range_header:
        headers["Range"] = range_header

    client = httpx.AsyncClient(timeout=30.0)
    try:
        upstream = await client.send(
            client.build_request("GET", url, headers=headers), stream=True
        )
    except Exception as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Error conectando con YouTube: {e}")

    async def body_iterator():
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    response_headers = {}
    for key in ("content-length", "content-range", "accept-ranges", "content-type"):
        if key in upstream.headers:
            response_headers[key] = upstream.headers[key]
    response_headers.setdefault("accept-ranges", "bytes")
    response_headers.setdefault("content-type", "audio/webm")

    return StreamingResponse(
        body_iterator(),
        status_code=upstream.status_code,
        headers=response_headers,
    )


@router.post("/download/{video_id}")
def download(video_id: str, title: str = "", artist: str = "", db: Session = Depends(get_db)):
    """Descarga el audio a disco y lo registra en la biblioteca (tabla songs)."""
    try:
        path = music_service.download_track(video_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error descargando: {e}")

    song = db.query(Song).filter(Song.source == "youtube", Song.external_id == video_id).first()
    if song:
        song.local_file_path = path
    else:
        song = Song(
            title=title or video_id,
            artist=artist or "Desconocido",
            source="youtube",
            external_id=video_id,
            local_file_path=path,
        )
        db.add(song)
    db.commit()
    db.refresh(song)
    return {"video_id": video_id, "file_path": path, "song_id": song.id}


@router.get("/file/{video_id}")
def get_file(video_id: str):
    """Sirve el archivo de audio ya descargado."""
    path = music_service.DOWNLOADS_DIR / f"{video_id}.opus"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no descargado todavía")
    return FileResponse(path, media_type="audio/opus", filename=f"{video_id}.opus")
