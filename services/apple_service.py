from typing import List, Optional
from models import Track

class AppleMusicClient:
    """
    Cliente de Apple Music

    Por ahora solo es un cascarón sin integración real con la API (no tengo dinero xD)
    Más adelante:
        - Se usará credenciales de Apple Developer (TEAM_ID, KEY_ID, PRIVATE_KEY).
        - se implementará autenticación con MusicKit.
    """

    def __init__(
            self,
            team_id: Optional[str] = None,
            key_id: Optional[str] = None,
            private_key_path: Optional[str] = None,
    ):
        self.team_id = team_id
        self.key_id = key_id
        self.private_key_path = private_key_path
    

    def search_tracks(self, query: str, limit: int = 5) -> List[Track]:
        """
        Busca canciones en Apple Music.
        Ahora mismo devuelve datos simulados.
        TODO
        cuando haya credenciales, se usará API real.
        """
        print(f"→ (AppleMusicClient.simulado) Buscando en Apple Music: '{query}'")
        artist = ""
        title = query

        if " - " in query:
            parts = query.split(" - ", maxsplit=1)
            artist, title = parts[0].strip(), parts[1].strip()
        
        if not artist:
            artist = "Artista Desconocido"
        
        demo_track = Track(artist=artist, title=title)
        return [demo_track]
    
    
    def get_tracks_from_playlist(self, playlist_url: str) -> List[Track]:
        """
        Obtiene canciones desde una playlist de Apple Music.
        Ahora mismo devuelve una lista fija simulada.
        """
        print(f"→ (AppleMusicClient.simulado) Obteniendo canciones de Apple Music desde: {playlist_url}")

        demo_tracks = [
            Track(artist="Kyary Pamyu Pamyu", title="Ponponpon"),
            Track(artist="Kyary Pamyu Pamyu", title="Ninja Re Bang Bang"),
            Track(artist="Kyary Pamyu Pamyu", title="チェリーボンボン"),
            Track(artist="Kyary Pamyu Pamyu", title="Harajuku Iyahoi"),
            Track(artist="Kyary Pamyu Pamyu", title="Kimino Mikata"),
        ]

        print(f"→ (AppleMusicClient.simulado) Se obtuvieron {len(demo_tracks)} canciones (simuladas)")
        return demo_tracks
    

def get_tracks_from_apple_playlist(playlist_url: str) -> List[Track]:
    """
    Llamado al AppleMusicClient
    TODO
    Usar API real en un futuro
    """
    client = AppleMusicClient()
    return client.get_tracks_from_playlist(playlist_url)