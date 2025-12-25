import os
from typing import List, Tuple
from models import Track
from services.apple_service import get_tracks_from_apple_playlist
from services.deezer_service import get_tracks_from_deezer_playlist
from services.youtube_music_service import get_tracks_from_youtube_music_playlist
from services.spotify_service import (
    load_env,
    init_spotify,
    search_track,
    create_playlist,
    add_tracks_in_batches
)

def read_songs_file(path: str) -> List[Tuple[str, str]]:
    """
    Lee un archivo de texto con el siguiente formato:
    Artista - Título

    y devuelve una lista de objetos de clase Track
    """
    songs: List[Track] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            #separar por " - "
            parts=line.split(" - ", maxsplit=1)
            if len(parts) != 2:
                print(f"[ADVERTENCIA] Línea inválida, se ignorará: {line}")
                continue
            artist, title = parts[0].strip(), parts[1].strip()
            track = Track(artist=artist, title=title)
            songs.append(track)
    return songs

def get_tracks_from_source(source_type: str) -> List[Track]:
    """
    Obtiene canciones desde cualquier fuente.
    source_type puede ser: 
        "1" (archivo), 
        "2" (apple), 
        "3" (deezer), 
        "4" (youtube)
    """
    if source_type == "1":
        #fuente: archivo
        songs_file = "songs.txt"
        if not os.path.exists(songs_file):
            print(f"Error: no se encontró el archivo {songs_file}.")
            return []
        
        songs = read_songs_file(songs_file)
        if not songs:
            print("No se encontraron canciones válidas en el archivo.")
            return []
        
        print(f"→ Se leyeron {len(songs)} canciones desde {songs_file}")
        return songs
    
    elif source_type == "2":
        #fuente: apple music (solo simulado)
        fake_url = "https://music.apple.com/mx/playlist/demo"
        songs = get_tracks_from_apple_playlist(fake_url)
        if not songs:
            print("No se obtuvieron canciones desde Apple Music (solo simulado)")
            return []
        print(f"→ Se obtuvieron {len(songs)} canciones desde Apple Music (solo simulado)")
        return songs
    
    elif source_type == "3":
        #fuente: deezer
        deezer_url = input("Pega la URL de la playlist de Deezer: ").strip()
        if not deezer_url:
            print("URL vacía.")
            return []
        print("\n→ Obteniendo canciones desde Deezer...")
        songs = get_tracks_from_deezer_playlist(deezer_url)
        if not songs:
            print("No se obtuvieron canciones desde Deezer.")
            return []
        print(f"→ Se obtuvieron {len(songs)} canciones desde Deezer")
        return songs
    
    elif source_type == "4":
        #fuente: youtube music
        yt_url = input("Pega la URL o ID de la playlist de Youtube Music: ").strip()
        if not yt_url:
            print("URL vacía.")
            return[]
        print("\n→ Obteniendo canciones desde Youtube Music...")
        songs = get_tracks_from_youtube_music_playlist(yt_url)
        if not songs:
            print("No se obtuvieron canciones desde Youtube Music.")
            return []
        print(f"→ Se obtuvieron {len(songs)} canciones desde Youtube Music")
        return songs
    else:
        print("Opción de fuente inválida.")
        return []

def main():
    print("=== Playlist cloner (versión CLI) ===\n")

    #1. Cargar configuración
    client_id, client_secret, redirect_uri, username = load_env()

    #2. Inicializar cliente Spotify
    print("→ Iniciando autenticación con Spotify...")
    sp = init_spotify(client_id, client_secret, redirect_uri)
    me = sp.current_user()
    print(f"Autenticado como {me['display_name']} ({me['id']})\n")

    #3. Seleccionar fuente de canciones
    print("=== SELECCIONA FUENTE DE CANCIONES ===")
    print("1) Archivo \"songs.txt\"")
    print("2) Apple Music (solo simulado)")
    print("3) Deezer (URL pública)")
    print("4) Youtube Music (URL o ID)")
    source_choice = input("\nOpción [1/2/3/4]: ").strip() or "1"

    #4. Obtener canciones desde la fuente elegida
    songs = get_tracks_from_source(source_choice)
    if not songs:
        print("No se obtuvieron canciones. Abortando")
        return
    

    #5. Preguntar nombre de la playlist destino
    playlist_name = input("\nNombre de la nueva playlist en Spotify: ").strip() or "Mi playlist clonada"
    
    #6. Buscar cada canción en Spotify
    found_track_ids: List[str] = []
    not_found: List[Track] = []
    
    print("\n=== Buscando canciones en Spotify ===")
    for idx, song in enumerate(songs, start=1):
        print(f"[{idx}/{len(songs)}] Buscando: {song} ...", end=" ", flush=True)
        track = search_track(sp, song.artist, song.title, song.duration_ms)
        if track:
            track_id = track["id"]
            found_track_ids.append(track_id)
            track_name = track["name"]
            track_artist = track["artists"][0]["name"]
            print(f"→ {track_artist} - {track_name}")
        else:
            not_found.append(song)
            print("No encontrada")
    
    #7. Crear playlist y agregar canciones encontradas
    if not found_track_ids:
        print("\n No se encontró ninguna canción en Spotify. No se creará playlist.")
        return
    
    print(f"\n→ creando playlist '{playlist_name}'...")
    playlist_id = create_playlist(sp, username, playlist_name)
    print(f"Playlist creada (ID: {playlist_id})")
    print("→ Agregando canciones a la playlist...")
    add_tracks_in_batches(sp, playlist_id, found_track_ids)

    #8. Resumen
    print("\n=== Resumen ===")
    print(f"Total obtenidos: {len(songs)}")
    print(f"Encontradas en Spotify: {len(found_track_ids)}")
    print(f"No encontradas: {len(not_found)}")

    if not_found:
        print("\nCanciones no encontradas: ")
        for track in not_found:
            print(f" - {track}")
    print("\n Listo. Revisa tu cuenta de Spotify para ver la nueva playlist")


if __name__== "__main__":
    main()
