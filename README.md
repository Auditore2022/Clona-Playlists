# Clonador de Playlist 0.2.0(CLI)

Script en python para clonar una lista de canciones a una playlist de Spotify, ya sea desde un archivo de texto, o desde un servicio de música alterno (Deezer -disponible- o Apple Music -pendiente-)

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
- si usarás la opción de archivo de texto, deberás crear un archivo "songs.txt" con las canciones que quiere añadir a la lista en el siguiente formato:
    Artista - Título
Por ejemplo:
    - Luis Miguel - Hasta Que Me Olvides
    - BURNOUT SYNDROMES - FLY HIGH!!

## Uso

- asegurate de haber ingresado previamente los valores necesarios en el archivo ".env" y en su caso, la lista de canciones en "songs.txt"
- ejecutar comando "python clone_cli.py"
- se abrirá el navegador para iniciar sesión en tu cuenta de spotify
- después de iniciar sesión, el programa te pedirá elegir tres opciones:
    1) leer desde un archivo de texto "songs.txt" (uso típico)
        - al usar la opción 1, el programa leerá el archvio "songs.txt" y buscará las canciones en Spotify
    2) leer desde una lista de Apple Music
        - NO DISPONIBLE POR EL MOMENTO
    3) leer desde un enlace a una lista de reproducción de Deezer
        - al usar la opción 3, el programa solicitará que ingreses la URL de una lista de reproducción de Deezer, la cual leerá y buscará las canciones en Spotify.
- después se te pedirá que ingreses un nombre para la lista de reproducción (por defecto se pondrá "Creada con clonador de Playlist")
- El programa creará automáticamente la Playlist con el nombre que elegiste, te mostrará la ID de la playlist, y comenzará a ingresar las canciones que haya encontrado en la plataforma
- Al finalizar, te dará un resumen con
    1. las canciones que encontró en total en el archivo "songs.txt"
    2. el total de canciones encontradas en Spotify
    3. el total de canciones NO encontradas en Spotify
    4. la lista de canciones que NO encontró en Spotify
  
  ejemplo:
  - 
    === Resumen ===
   
    Total en archivo: 696
    Encontradas en Spotify: 695
    No encontradas: 1

    Canciones no encontradas:
    - Eros Ramazzotti - Así (feat. Il Volo)

    Listo. Revisa tu cuenta de Spotify para ver la nueva playlist.

## Versiones

### v0.2.0
- Integración completa con Deezer (Búsqueda + Playlist)
- Clonación Deezer → Spotify funcional
- CLI con soporte para 3 fuentes: archivo txt, Apple Music (simulado), Deezer

### v0.1.2
- Se reorganizó la arquitectura para futura implementación de Apple Music
- Se añadió comentarios sobre las credenciales a obtener desde Apple developer

### v0.1.1
- Se implementó el objeto 'Track' como modelo de búsqueda sin importar la plataforma.
- Integración básica con Spotify web API funcional.
- Se reorganizó la lógica de Spotify, separandola en su propio archivo (services/spotify_service.py).
- Se añadió esqueleto para 'services/apple_service.py', solo funciona en modo simulado.
- Se añadió soporte para seleccionar fuente (archivo o Apple Music simulado).
- **En desarrollo** Integración real con la API de Apple Music

### v0.1.0
- Primera versión CLI usable: lectura desde "songs.txt", creación de playlist en Spotify y matchin básico mejorado.