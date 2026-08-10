from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Song
from app.schemas import SongCreate, SongOut

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/", response_model=list[SongOut])
def list_songs(db: Session = Depends(get_db)):
    return db.query(Song).all()


@router.post("/", response_model=SongOut)
def add_song(song: SongCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Song)
        .filter(Song.source == song.source, Song.external_id == song.external_id)
        .first()
    )
    if existing:
        return existing

    db_song = Song(**song.model_dump())
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


@router.delete("/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    db.delete(song)
    db.commit()
    return {"ok": True}
