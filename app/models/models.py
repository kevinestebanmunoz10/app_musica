from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base

# Tabla intermedia playlist <-> canciones (relación muchos a muchos)
playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True),
)


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    artist = Column(String, index=True, nullable=False)
    source = Column(String, nullable=False)  # "spotify" | "youtube"
    external_id = Column(String, nullable=False)  # id en la plataforma origen
    duration_ms = Column(Integer, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    local_file_path = Column(String, nullable=True)  # si se descargó localmente
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    playlists = relationship("Playlist", secondary=playlist_songs, back_populates="songs")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    songs = relationship("Song", secondary=playlist_songs, back_populates="playlists")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
