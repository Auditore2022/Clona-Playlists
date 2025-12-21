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

def read_songs_file(path: str) -> List[Tuple[str, str]]:
    """
    lee un archivo de texto con formato:
    Artista - Tìtulo
    
    Devuelve una lista de tuplas (artista, tìtulo)
    
    """
    songs:List[Tuple[str, str]] = []

    with open(path, "r", encoding = "utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            #separar por " - "
            parts = line.split(" - ", maxsplit=1)
            if len(parts) != 2:
                print(f"[ADVERTENCIA] Línea inválida (se ignorará): {line}")
                continue
            artist, title = parts[0].strip(), parts[1].strip()
            songs.append((artist, title))

    return songs
    
def search_track(sp: spotipy.Spotify, artist: str, title: str):
    """busca un track en spotify usando artista + títutlo"""
    query = f"track:{title} artist:{artist}"
    result = sp.search(q=query, type="track", limit=1)
    items = result.get("tracks", {}).get("items", [])

    if not items:
        return None
    return items[0] #primer resultado

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

def main():
    print("=== Playlist Cloner (versión CLI) ===")

    #1. Cargar configuración
    client_id, client_secret, redirect_uri, username = load_env()

    #2. Inicializar cliente de Spotify (esto abrirá el navegador la primera vez)
    print("→ Iniciando autenticación con Spotify...")
    sp = init_spotify(client_id, client_secret, redirect_uri)
    me = sp.current_user()
    print(f"Autenticado como: {me['display_name']} ({me['id']})")

    #3. leer archivo de canciones
    songs_file = "songs.txt"
    if not os.path.exists(songs_file):
        print(f"No se encontró el archivo {songs_file}. Créalo y agrega 'Artista - Título' por línea.")
        return
    songs = read_songs_file(songs_file)
    if not songs:
        print("No se encontraron cancionas válidad en el archivo")
        return
    
    print(f"→ Se leyeron {len(songs)} canciones desde {songs_file}")

    #4. preguntar nombre de la playlist destino
    playlist_name = input("Nombre de la nueva playlist en Spotify: ").strip() or "Mi playlist clonada"

    #5. Buscar canciones en spotify
    found_track_ids: List[str] = []
    not_found: List[Tuple[str, str]] = []

    print("\n=== Buscando canciones en Spotify ===")
    for idx, (artist, title) in enumerate(songs, start=1):
        print(f"[{idx}/{len(songs)}] Buscando: {artist} - {title}...", end=" ", flush=True)
        track = search_track(sp, artist, title)
        if track:
            track_id = track["id"]
            found_track_ids.append(track_id)
            track_name = track["name"]
            track_artist = track["artists"][0]["name"]
            print(f"→ {track_artist} - {track_name}")
        else:
            not_found.append((artist, title))
            print("No encontrada")
    
    #6. Crear playlist y agregar canciones encontrada
    if not found_track_ids:
        print("\n No se encontró ninguna canción en Spotify. No se creará playlist")
        return
    
    print(f"\n→ Creando playlist '{playlist_name}'...")
    playlist_id = create_playlist(sp, username, playlist_name)
    print(f"Playlist creada (ID: {playlist_id})")

    print("→ Agregando canciones a la playlist...")
    add_tracks_in_batches(sp, playlist_id, found_track_ids)

    #7. Resumen
    print("\n=== Resumen ===")
    print(f"Total en archivo: {len(songs)}")
    print(f"Encontradas en Spotify: {len(found_track_ids)}")
    print(f"No encontradas: {len(not_found)}")

    if not_found:
        print("\nCanciones no encontradas:")
        for artist, title in not_found:
            print(f" - {artist} - {title}")

    print("\nListo. Revisa tu cuenta de Spotify para ver la nueva playlist.")

if __name__== "__main__":
    main()
