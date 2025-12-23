from typing import List
from models import Track

def get_tracks_from_apple_playlist(playlist_url: str) -> List[Track]:
    """
    Simula obtener canciones desde una playlist de Apple Music

    TODO
    -se Usará MusicKit / Apple Music API para leer una playlist real.
    -Convertir la respuesta en objetos Track.
    """
    print(f"(simulado) Obteniendo canciones de Apple Music desde: {playlist_url}")

    #lista de ejemplo (para prototipado)
    demo_tracks = [
        Track(artist="José José", title="Lágrimas (Sinfónico)"),
        Track(artist="José José", title="¿Y Quién Puede Ser? (Sinfónico)"),
        Track(artist="José José", title="El Triste (Sinfónico)"),
        Track(artist="José José", title="Payaso (Sinfónico)"),
        Track(artist="José José", title="No Me Digas Que Te Vas (Sinfónico)"),
        Track(artist="José José", title="Preso (Sinfónico)")
    ]
    
    print(f"(Simulado) Se obtuvieron {len(demo_tracks)} canciones desde Apple Music")
    return demo_tracks