# Clonador de Playlist 0.1.0(CLI)

Script en python para clonar una lista de canciones (artista - título) de un archivo ".txt" a una playlist de Spotify

## Requisitos

- Python 3.10+
- Cuenta de Spotify
- App creada en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

## Instalación
- pip install -r requirements.txt
- crear un archivo ".env" con los siguientes datos:
    - SPOTIFY_CLIENT_ID=TU_CLIENT_ID
    - SPOTIFY_CLIENT_SECRET=TU_CLIENT_SECRET
    - SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
    - SPOTIFY_USERNAME=tu_usuario
- crear un archivo "songs.txt" con las canciones que quiere añadir a la lista en el siguiente formato:
    Artista - Título
Por ejemplo:
    - Luis Miguel - Hasta Que Me Olvides
    - BURNOUT SYNDROMES - FLY HIGH!!

## Uso

- asegurate de haber ingresado previamente los valores necesarios en el archivo ".env" y la lista de canciones en "songs.txt"
- ejecutar comando "python clone_cli.py"
- se abrirá el navegador para iniciar sesión en tu cuenta de spotify
- después de iniciar sesión, el programa leerá el archvio "songs.txt" y buscará las canciones en Spotify
- después se te pedirá que ingreses un nombre para la lista de reproducción (por defecto se pondrá "Creada con clonador de Playlist")
- El programa creará automáticamente la Playlist con el nombre que elegiste, te mostrará la ID de la playlist, y comenzará a ingresar las canciones que haya encontrado en la plataforma
- Al finalizar, te dará un resumen con
    1. las canciones que encontró en total en el archivo "songs.txt"
    2. el total de canciones encontradas en Spotify
    3. el total de canciones NO encontradas en Spotify
    4. la lista de canciones que NO encontró en Spotify
  
  ejemplo:
    === Resumen ===
    Total en archivo: 696
    Encontradas en Spotify: 695
    No encontradas: 1

    Canciones no encontradas:
    - Eros Ramazzotti - Así (feat. Il Volo)

    Listo. Revisa tu cuenta de Spotify para ver la nueva playlist.

## Versiones

- v0.1.0 - Primera versión CLI usable: lectura desde "songs.txt", creación de playlist en Spotify y matchin básico mejorado.
