from typing import List, Optional
from models import Track

try:
    from ytmusicapi import YTMusic
except ImportError:
    print("ytmusicapi no instalado, instala con pip install ytmusicapi")
    YTMusic = None


class YoutubeMusicClient:
    """
    Cliente de Youtube Music.
    Usa ytmusicapi para acceder a Youtube Music.

    IMPORTANTE: solo es modo LECTURA (buscar y obtener playlists).
    La creación de playlists requiere configuración adicional que se añadirá en el futuro.
    """

    def __init__(self):
        """inicializa el cliente sin autenticar (solo lectura)"""
        if YTMusic is None:
            raise RuntimeError("ytmusicapi no está instalado")
        
        #Inicializar sin archivo de auth (solo lectura de playlists públicas por el momento)
        self.yt = YTMusic()
    
    def search_tracks(self, query: str, limit: int=5) -> List[Track]:
        """
        Busca canciones en Youtube Music por query (artista o título).
        """
        print(f"(YoutubeMusicClient) Buscando en Youtube Music: '{query}'")

        try:
            #search_songs devolverá resultados de canciones
            results = self.yt.search(query, filter="songs", limit=limit)

            tracks = []
            for item in results:
                #Extraer info del resultado
                artist_name = ""
                if "artists" in item and len(item["artists"]) > 0:
                    artist_name = item["artists"][0]["name"]
                
                title = item.get("title", "")

                if title: #solo se agrega si tiene título
                    track = Track(
                        artist = artist_name or "Artista Desconocido",
                        title = title,
                        album = item.get("album", {}).get("name", "")
                    )
                    tracks.append(track)
            print(f"→ Se encontraron {len(tracks)} canciones en Youtube Music")
            return tracks
        except Exception as e:
            print(f" Error buscando en Youtube Music: {e}")
            return []
    

    def get_tracks_from_playlist(self, playlist_url: str) -> List[Track]:
        """
        Obtiene canciones desde una playlist de Youtube Music.

        Espera una URL tipo:
        https://music.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf

        o un ID de playlist:
        PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
        """
        print(f"(YoutubeMusicClient) Obteniendo canciones de Youtube Music desde {playlist_url}")

        # Extraer ID de la playlist
        playlist_id = self._extract_playlist_id(playlist_url)

        if not playlist_id:
            print("❌ Error: No se pudo extraer el ID de la playlist")
            return []
        
        try:
            # Obtener playlist y canciones
            playlist_contents = self.yt.get_playlist(playlist_id)
            
            # Validar que se obtuvo la playlist
            if playlist_contents is None:
                print("❌ Error: No se pudo obtener la playlist (puede ser privada o no existe)")
                return []
            
            # Validar que tiene canciones
            if "tracks" not in playlist_contents or playlist_contents["tracks"] is None:
                print("❌ Error: La playlist no tiene canciones o no se pudieron cargar")
                return []

            tracks = []
            for item in playlist_contents.get("tracks", []):
                # Validar que item no sea None
                if item is None:
                    continue
                
                artist_name = ""
                if "artists" in item and item["artists"] and len(item["artists"]) > 0:
                    artist_name = item["artists"][0].get("name", "")

                title = item.get("title", "")

                if title:
                    track = Track(
                        artist=artist_name or "Artista Desconocido",
                        title=title,
                        album=item.get("album", {}).get("name", "") if item.get("album") else ""
                    )
                    tracks.append(track)
            
            print(f"→ Se obtuvieron {len(tracks)} canciones desde Youtube Music")
            return tracks
            
        except Exception as e:
            print(f"❌ Error obteniendo playlist de Youtube Music: {e}")
            print("   Tip: Asegúrate de que la URL es correcta y la playlist es pública")
            return []
    
    def _extract_playlist_id(self, url_or_id: str) -> Optional[str]:
        """
        Extrae el ID de una URL o devuelve el ID si es directo.
        Formatos esperados:
        - https://music.youtube.com/playlist?list=PLxxx
        - https://music.youtube.com/playlist?list=OLAKxxx
        - https://music.youtube.com/playlist?list=RDCLAKxxx
        - PLxxx (ID directo)
        - OLAKxxx (ID directo)
        - RDCLAKxxx (ID directo)
        """

        #si ya es un ID directo (empieza con PL, OLAK, RDCLAK, etc)
        if any(url_or_id.startswith(prefix) for prefix in ["PL", "OLAK", "RDCLAK", "RD"]):
            return url_or_id.split("&")[0].strip() #quita los parámetros extra
        
        #si es una URL
        if "list=" in url_or_id:
            try:
                parts = url_or_id.split("list=")
                playlist_id = parts[1].split("&")[0].split("#")[0].strip()
                #aceptar cualquier ID que esté después de "list="
                return playlist_id if playlist_id else None
            except Exception:
                pass
        return None

def get_tracks_from_youtube_music_playlist(playlist_url: str) -> List[Track]:
    """
    Función de alto nivel usada por el CLI.
    envuelve al YoutubeMusicClient.
    """
    client = YoutubeMusicClient()
    return client.get_tracks_from_playlist(playlist_url)
