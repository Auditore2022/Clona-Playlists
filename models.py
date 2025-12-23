from dataclasses import dataclass
from typing import Optional

@dataclass
class Track:
    """Rerpresenta una cacnión sin depender de alguna plataforma específica"""
    artist: str
    title: str
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    isrc: Optional[str] = None

    def __str__(self) -> str:
        """Devuelve una representación legible del Track (Artista - Título)"""
        return f"{self.artist} - {self.title}"