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

def search_track(sp: spotipy.Spotify, artist: str, title: str, duration_ms: int = None):
    """
    Busca un track en Spotify usando tres estrategias:
    1) Búsqueda estricta con qualifiers (track: / artist:)
    2) Búsqueda flexible sin qualifiers
    3) Fuzzy matching si las anteriores fallan
    
    Filtra por duración si está disponible.
    """
    from fuzzywuzzy import fuzz
    
    # 1) Búsqueda estricta
    query_strict = f"track:{title} artist:{artist}"
    result = sp.search(q=query_strict, type="track", limit=5)
    items = result.get("tracks", {}).get("items", [])
    
    if items:
        # Validar duración si está disponible
        if duration_ms:
            for item in items:
                duration_diff = abs(item.get("duration_ms", 0) - duration_ms)
                # Si la duración está dentro de ±5 segundos, es probablemente correcta
                if duration_diff < 5000:
                    return item
        # Si no hay duración o no coincide exactamente, devolver el primero
        return items[0]

    # 2) Búsqueda flexible (sin qualifiers), hasta 5 resultados
    query_flexible = f"{title} {artist}"
    result = sp.search(q=query_flexible, type="track", limit=5)
    items = result.get("tracks", {}).get("items", [])
    
    if items:
        # Validar duración si está disponible
        if duration_ms:
            for item in items:
                duration_diff = abs(item.get("duration_ms", 0) - duration_ms)
                if duration_diff < 5000:
                    return item
        return items[0]

    # 3) Fuzzy matching: Si nada funcionó, intentar con fuzzy
    # Buscar solo por título (menos restrictivo)
    query_title_only = title
    result = sp.search(q=query_title_only, type="track", limit=10)
    items = result.get("tracks", {}).get("items", [])
    
    if items:
        # Calcular similitud fuzzy entre el artista buscado y los resultados
        best_match = None
        best_score = 0
        
        for item in items:
            # Extraer artistas del resultado
            item_artist = item["artists"][0]["name"] if item.get("artists") else ""
            
            # Calcular similitud
            artist_similarity = fuzz.token_set_ratio(artist.lower(), item_artist.lower())
            title_similarity = fuzz.token_set_ratio(title.lower(), item.get("name", "").lower())
            
            # Score combinado (60% artista, 40% título)
            combined_score = (artist_similarity * 0.6) + (title_similarity * 0.4)
            
            # Validar duración
            if duration_ms:
                duration_diff = abs(item.get("duration_ms", 0) - duration_ms)
                if duration_diff > 5000:
                    combined_score *= 0.7  # Penalizar si la duración no coincide
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = item
        
        # Solo devolver si el score es razonable (>60)
        if best_match and best_score > 60:
            return best_match

    return None

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
