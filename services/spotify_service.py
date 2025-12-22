import os
from typing import List, Tuple
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def load_env():
    """cargar variables de entorno desde .env"""
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    username = os.getenv("SPOTIFY_USERNAME")

    if not all([client_id, client_secret, redirect_uri, username]):
        raise RuntimeError("Faltan variables en .env(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, USERNAME)")
    
    return client_id, client_secret, redirect_uri, username

def init_spotify(client_id: str, client_secret: str, redirect_uri: str) -> spotipy.Spotify:
    """inicializa el cliente spotify con OAuth"""
    scope = "playlist-modify-public playlist-modify-private"

    auth_manager = SpotifyOAuth(
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = redirect_uri,
        scope = scope
    )

    sp = spotipy.Spotify(auth_manager = auth_manager)
    return sp

def search_track(sp: spotipy.Spotify, artist: str, title: str):
    """
    Busca un track en Spotify usando dos métodos:
    1. Búsqueda estricta con qualifiers (track: / artist:)
    2. Búsqueda flexible sin qualifiers
    """

    #1. Búsqueda estricta
    query_strict = f"track:{title} artist:{artist}"
    result = sp.search(q=query_strict, type="track", limit=1)
    items = result.get("tracks", {}).get("items", [])
    if items:
        return items[0]
    
    #2. Búsqueda flexible (hasta 3 resultados)
    query_flexible = f"{title} {artist}"
    result = sp.search(q=query_flexible, type="track", limit=3)
    items = result.get("tracks", {}).get("items", [])
    if not items:
        return None
    
    #por ahora, devolvemos el primero de los resultados
    return items[0]

def create_playlist(sp: spotipy.Spotify, username: str, name: str, description: str = "") -> str:
    """Crea un playlist y devuelve su ID"""
    playlist = sp.user_playlist_create(
        user = username,
        name = name,
        public = False,
        description = description or "Creada con Clonador de Playlist"
    )
    return playlist["id"]

def add_tracks_in_batches(sp: spotipy.Spotify, playlist_id: str, track_ids: List[str]):
    """Agrega tracks en lotes de máximo 100 (limitación de la API)."""
    BATCH_SIZE = 100
    for i in range(0, len(track_ids), BATCH_SIZE):
        batch = track_ids[i : i + BATCH_SIZE]
        sp.playlist_add_items(playlist_id, batch)
        print (f"→ Agregadas {len(batch)} canciones a la playlist (total parcial: {i + len(batch)})")
