from typing import List, Optional
import requests
from models import Track

class DeezerClient:
    """
    Cliente de Deezer.
    Usa la API pública de Deezer para funcionar
    """

    BASE_URL = "https://api.deezer.com"

    def __init__(self):
        self.session = requests.Session()
    
    def search_tracks(self, query: str, limit: int = 5) -> List[Track]:
        """
        Busca canciones en Deezer por query (artista o título).
        """
        print(f"(DeezerClient) Buscando en Deezer: '{query}'")

        endpoint = f"{self.BASE_URL}/search/track"
        params= {
            "q": query,
            "limit": limit
        }

        try:
            response = self.session.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            tracks = [ ]
            for item in data.get("data", []):
                track = Track(
                    artist = item["artist"]["name"],
                    title=item["title"],
                    album=item.get("album", {}).get("title", ""),
                    duration_ms=item.get("duration", 0) * 1000, #convierte segundos a ms
                )
                tracks.append(track)
            
            print(f"→ Se encontraron {len(tracks)} canciones en Deezer")
            return tracks
        except requests.RequestException as e:
            print(f"Error buscando en Deezer: {e}")
            return []
    

    def get_tracks_from_playlist(self, playlist_url: str) -> List[Track]:
        """
        Obtiene canciones desde una playlist de Deezer.
        Espera una url tipo:
        https://www.deezer.com/playlist/1234567890
        """
        print(f"(DeezerClient) Obteniendo canciones de Deezer desde: {playlist_url}")

        #extrae ID de la playlist desde la URL
        playlist_id = self._extract_playlist_id(playlist_url)

        if not playlist_id:
            print("No se pudo extraer el ID de la playlist de la URL")
            return[]
        
        endpoint = f"{self.BASE_URL}/playlist/{playlist_id}/tracks"
        params = {"limit": 100} #máximo por request

        try:
            response = self.session.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            tracks = []
            for item in data.get("data", []):
                track = Track(
                    artist=item["artist"]["name"],
                    title=item["title"],
                    album=item.get("album", {}).get("title", ""),
                    duration_ms=item.get("duration", 0) * 1000 #convierte segundos a ms
                )
                tracks.append(track)
            print(f"→ Se obtuvieron {len(tracks)} canciones desde Deezer")
            return tracks
        except requests.RequestException as e:
            print(f"Error obteniendo playlist de Deezer: {e}")
            return []
    
    def _extract_playlist_id(self, url: str) -> Optional[str]:
        """
        extrae el ID de una url de Deezer.
        Se esperan formatos como:
            - https://www.deezer.com/playlist/1234567890
            - https://deezer.com/playlist/1234567890
        """
        if "playlist/" not in url:
            return None
        
        try:
            #se extrae el número despues de "playlist/"
            parts = url.split("playlist/")
            if len(parts) > 1:
                playlist_id = parts[1].split("?")[0].split("#")[0].strip()
                return playlist_id if playlist_id.isdigit() else None
        except Exception:
            pass
        return None
    
def get_tracks_from_deezer_playlist(playlist_url: str) -> List[Track]:
     """
     Función de alto nivel usada por el CLI.
     Envuelve al DeezerClient.
     """
     client = DeezerClient()
     return client.get_tracks_from_playlist(playlist_url)