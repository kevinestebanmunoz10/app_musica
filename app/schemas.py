from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SongBase(BaseModel):
    title: str
    artist: str
    source: str
    external_id: str
    duration_ms: Optional[int] = None
    thumbnail_url: Optional[str] = None


class SongCreate(SongBase):
    pass


class SongOut(SongBase):
    id: int
    local_file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistCreate(BaseModel):
    name: str


class PlaylistOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    songs: list[SongOut] = []

    class Config:
        from_attributes = True
