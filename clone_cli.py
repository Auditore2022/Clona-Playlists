import os
from typing import List, Tuple
from models import Track
from services.apple_service import get_tracks_from_apple_playlist
from services.deezer_service import get_tracks_from_deezer_playlist
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

def main():
    print("=== Playlist Cloner (versión CLI) ===")
    print("Selecciona la fuente de canciones: ")
    print(" 1) Archivo 'songs.txt'")
    print(" 2) Apple Music (simulado)")
    print(" 3) Deezer (URL pública)")
    choice = input ("Opción [1/2/3]: ").strip() or "1"

    #1. Cargar configuración
    client_id, client_secret, redirect_uri, username = load_env()

    #2. Inicializar cliente de Spotify (esto abrirá el navegador la primera vez)
    print("→ Iniciando autenticación con Spotify...")
    sp = init_spotify(client_id, client_secret, redirect_uri)
    me = sp.current_user()
    print(f"Autenticado como: {me['display_name']} ({me['id']})")

    #3. Obtener canciones según la fuente elegida
    if choice== "1":
        songs_file = "songs.txt"
        if not os.path.exists(songs_file):
            print(f"No se encontró el archivo {songs_file}. Créalo y agrega tus canciones en formato 'Artista - Título' por línea")
            return
        
        songs = read_songs_file(songs_file)
        if not songs:
            print("No se encontraron canciones válidas en el archivo.")
            return
        
        print(f"Se leyeron {len(songs)} canciones desde {songs_file}")
    
    elif choice == "2":
        #TODO: en el futuro se leerá una URL real de Apple Music
        fake_url = "https://music.apple.com/mx/playlist/demo"
        songs = get_tracks_from_apple_playlist(fake_url)
        if not songs:
            print("No se obtuvieron canciones desde Apple Music (simulado).")
            return
        
        print(f"Se obtuvieron {len(songs)} canciones desde Apple Music (simulado).")
    
    elif choice == "3":
        deezer_url = input("Pega la URL de la playlist de Deezer: ").strip()
        if not deezer_url:
            print("Error: URL vacía. Intenta de nuevo")
            return
        
        print("\n→ Obteniendo canciondes desde Deezer...")
        songs = get_tracks_from_deezer_playlist(deezer_url)
        if not songs:
            print("No se obtuvieron canciones desde Deezer. Verifica la URL.")
            return
        
        print(f"→ Se obtuvieron {len(songs)} canciones desde Deezer")

    else:
        print("Opción inválida. Usa 1, 2 o 3.")
        return

    #4. preguntar nombre de la playlist destino
    playlist_name = input("Nombre de la nueva playlist en Spotify: ").strip() or "Mi playlist clonada"

    #5. Buscar canciones en spotify
    found_track_ids: List[str] = []
    not_found: List[Tuple[str, str]] = []

    print("\n=== Buscando canciones en Spotify ===")
    for idx, song in enumerate(songs, start=1):
        print(f"[{idx}/{len(songs)}]Buscando: {song} ...", end=" ", flush=True)
        track = search_track(sp, song.artist, song.title)
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
