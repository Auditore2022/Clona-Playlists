import os
from typing import List, Tuple
from models import Track
from services.apple_service import get_tracks_from_apple_playlist
from services.spotify_service import (
    load_env,
    init_spotify,
    search_track,
    create_playlist,
    add_tracks_in_batches
)
from services.deezer_service import (
    get_tracks_from_deezer_playlist,
    create_playlist_in_deezer,
    add_tracks_to_deezer_playlist
)
from services.youtube_music_service import (
    get_tracks_from_youtube_music_playlist,
    create_playlist_in_youtube_music,
    add_tracks_to_youtube_music_playlist
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

def create_playlist_in_destination(
        destination_type: str,
        playlist_name: str,
        tracks: List[Track],
        sp=None #cliente Spotify si es necesario
) -> dict:
    """
    Crea una playlist en el destino elegido y agrega las canciones
    destination_type puede ser: "1" (spotify), "2", (deezer), "3" (youtube)
    """

    if destination_type == "1":
        #Destino: Spotify
        if not sp:
            print("Cliente Spotify no inicializado")
            return {"status": "error", "message": "Spotify client not inicialized"}
        
        #obtener username
        me= sp.current_user()
        username = me["id"]

        print(f"\n→ Creando playlist '{playlist_name}' en Spotify...")
        playlist_id = create_playlist(sp, username, playlist_name)

        if not playlist_id:
            return {"status": "error", "message": "Failed to create Spotify playlist"}
        
        #buscar cada canción en Spotify
        found_track_ids = []
        not_found = []

        print("\n=== Buscando canciones en Spotify ===")
        for idx, song in enumerate(tracks, start=1):
            print(f"[{idx}/{len(tracks)}] Buscando: {song}...", end=" ", flush=True)
            track = search_track(sp, song.artist, song.title, song.duration_ms)
            if track:
                found_track_ids.append(track["id"])
                print(f"✅")
            else:
                not_found.append(song)
                print(f"❌")
        
        #agregar canciones
        if found_track_ids:
            print(f"→ Agregando {len(found_track_ids)} canciones a Spotify...")
            add_tracks_in_batches(sp, playlist_id, found_track_ids)
        
        return {
            "status": "success",
            "destination": "Spotify",
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "found": len(found_track_ids),
            "not_found": len(not_found),
            "not_found_list": not_found
        }
    
    elif destination_type == "2":
        # Destino: Deezer
        print(f"\n→ Creando playlist '{playlist_name}' en Deezer...")
        playlist_id = create_playlist_in_deezer(playlist_name)
        
        result = add_tracks_to_deezer_playlist(playlist_id, tracks)
        
        return {
            "status": "success",
            "destination": "Deezer",
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "found": result["added"],
            "not_found": result["failed"],
            "not_found_list": [],
        }
    
    elif destination_type == "3":
        # Destino: YouTube Music
        print(f"\n→ Creando playlist '{playlist_name}' en YouTube Music...")
        playlist_id = create_playlist_in_youtube_music(playlist_name)
        
        result = add_tracks_to_youtube_music_playlist(playlist_id, tracks)
        
        return {
            "status": "success",
            "destination": "YouTube Music",
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
            "found": result["added"],
            "not_found": result["failed"],
            "not_found_list": [],
        }
    
    else:
        return {"status": "error", "message": "Invalid destination type"}

def main():
    print("=== Playlist Cloner (v0.3.0 - Bidireccional) ===\n")

    # 1. Cargar configuración de Spotify
    client_id, client_secret, redirect_uri, username = load_env()

    # 2. Inicializar cliente Spotify (siempre necesario para búsqueda)
    print("→ Iniciando autenticación con Spotify...")
    sp = init_spotify(client_id, client_secret, redirect_uri)
    me = sp.current_user()
    print(f"✅ Autenticado en Spotify como: {me['display_name']}\n")

    # 3. Seleccionar ORIGEN de canciones
    print("=== SELECCIONA ORIGEN DE CANCIONES ===")
    print("  1) Archivo 'songs.txt'")
    print("  2) Apple Music (simulado)")
    print("  3) Deezer (URL pública)")
    print("  4) YouTube Music (URL o ID)")
    source_choice = input("\nOpción [1/2/3/4]: ").strip() or "1"

    # 4. Obtener canciones desde la fuente
    songs = get_tracks_from_source(source_choice)
    if not songs:
        print("❌ No se obtuvieron canciones. Abortando.")
        return

    # 5. Seleccionar DESTINO
    print("\n=== SELECCIONA DESTINO ===")
    print("  1) Spotify")
    print("  2) Deezer (simulado - requiere OAuth en v0.3.1)")
    print("  3) YouTube Music (simulado - requiere OAuth en v0.3.1)")
    destination_choice = input("\nOpción [1/2/3]: ").strip() or "1"

    # 6. Preguntar nombre de la playlist destino
    playlist_name = input("\nNombre de la nueva playlist: ").strip() or "Mi playlist clonada"

    # 7. Crear playlist en destino y agregar canciones
    print("\n" + "="*50)
    result = create_playlist_in_destination(
        destination_choice,
        playlist_name,
        songs,
        sp=sp
    )

    # 8. Mostrar resumen
    if result["status"] == "success":
        print("\n=== Resumen ===")
        print(f"Origen: {source_choice}")
        print(f"Destino: {result['destination']}")
        print(f"Total obtuvieron: {len(songs)}")
        print(f"Encontradas en destino: {result['found']}")
        print(f"No encontradas: {result['not_found']}")
        
        if result["not_found_list"]:
            print("\nCanciones no encontradas:")
            for track in result["not_found_list"][:10]:  # Mostrar máximo 10
                print(f"  - {track}")
            if len(result["not_found_list"]) > 10:
                print(f"  ... y {len(result['not_found_list']) - 10} más")
        
        print(f"\n🎉 Playlist '{playlist_name}' creada exitosamente en {result['destination']}!")
    else:
        print(f"\n❌ Error: {result.get('message', 'Desconocido')}")

if __name__ == "__main__":
    main()