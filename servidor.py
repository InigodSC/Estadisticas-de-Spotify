import asyncio
import fastapi
import datetime as dt
import uvicorn
from fastapi import Request, HTTPException, Query, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests, base64, urllib.parse
import webbrowser
from collections import Counter
import httpx  # ✅ Asegúrate de tener esto arriba en tus imports


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"]
)

GENRES_VALIDOS = {
    "pop", "rock", "hip-hop", "edm", "electronic", "latin", "indie", "reggaeton", "trap",
    "jazz", "blues", "metal", "dance", "folk", "classical", "soul", "funk", "punk", "house"
}
GENERO_FAMILIAS = {
    "pop": ["pop", "dance pop", "indie pop", "pop rap", "latin pop", "teen pop"],
    "rock": ["rock", "alternative rock", "indie rock", "hard rock", "soft rock", "punk rock"],
    "hip-hop": ["hip hop", "rap", "trap", "trap latino", "hip-hop", "gangster rap"],
    "reggaeton": ["reggaeton", "latin hip hop"],
    "electronic": ["edm", "electro", "electronic", "house", "deep house", "techno", "trance"],
    "metal": ["metal", "heavy metal", "death metal", "metalcore"],
    "rnb": ["r&b", "r-n-b", "soul", "neo soul"],
    "latin": ["latin", "latino", "salsa", "bachata", "merengue"],
    "jpop": ["j-pop", "japanese pop", "j-idol", "anime"],
    "kpop": ["k-pop", "korean pop"],
}


CLIENT_ID = "10975615f3b34ac09a9c8c9a1d64642a"
CLIENT_SECRET = "c2cfab340b9a4a82a436f1ac90d1fafa"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-top-read user-read-recently-played user-read-private user-read-email"
URL_BASE = "https://api.spotify.com/v1"

access_token = None


#############GETS PARA EL LOGIN#############

#Login para el cliente
@app.get("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

#Recibe el codigo de autorización
from fastapi.responses import RedirectResponse

@app.get("/callback")
def callback(request: Request):
    global access_token
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="No se recibió el código de autorización")

    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="Error obteniendo el token")

    access_token = res.json()["access_token"]

    #Redirige a Angular y le pasa el token por query
    return RedirectResponse(f"http://localhost:4200/callback?access_token={access_token}")

#Devuelve el token de acceso del ultimo cliente logeado
@app.get("/token")
def get_token():
    return {"access_token": access_token}


#############GETS DE PERFIL USUARIO#############


#Devuelve el nombre de usuario
@app.get("/usr_name/{acs_tkn}")
def getUsrName(acs_tkn):

    headers = {"Authorization": f"Bearer {acs_tkn}"}
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la informacion del perfil del usuario")

    data = response.json()
    return {
        "nombre": data.get("display_name"),
    }

#Devuelve la foto de perfil del usuario
@app.get("/usr_pic/{acs_tkn}")
def getUsrPic(acs_tkn):

    headers = {"Authorization": f"Bearer {acs_tkn}"}
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la información del perfil del usuario")

    data = response.json()
    images = data.get("images")

    if images and len(images) > 0 and images[0].get("url"):
        return {"url": images[0]["url"]}
    else:
        return {"url": "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"}

#Devuelve el email del usuario
@app.get("/usr_email/{acs_tkn}")
def getUsrEmail(acs_tkn):

    headers = {"Authorization": f"Bearer {acs_tkn}"}
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la informacion del perfil del usuario")

    data = response.json()
    return {
        "email": data.get("email"),
    }

#Devuelve el numero de seguidores del usuario
@app.get("/usr_followers/{acs_tkn}")
def getUsrFollowers(acs_tkn: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la información del perfil del usuario")

    data = response.json()
    return {
        "followers": data.get("followers", {}).get("total", 0)
    }

#Devuelve el pais del usuario
@app.get("/usr_country/{acs_tkn}")
def getUsrFollowers(acs_tkn: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la información del perfil del usuario")

    data = response.json()
    return {
        "country": data.get("country"),
    }

#############GETS CANCIONES Y ARTISTAS#############

#Devuelve los top artistas escuchados del usuario, se puede establecer el limite de artistas a mostrar y el tiempo que quieras recoger los datos
@app.get("/top_artists/{acs_tkn}")
def get_top_artists(
    acs_tkn,
    time_range: str = Query("long_term", enum=["short_term", "medium_term", "long_term"]),
    limit: int = Query(..., gt=0, le=50, description="Número de artistas a mostrar (entre 1 y 50)")
):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    url = f"{URL_BASE}/me/top/artists?time_range={time_range}&limit={limit}" 
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()
    return [
    {
        "nombre": artist["name"],
        "generos": artist["genres"],
        "imagen": artist["images"][0]["url"] if artist.get("images") else "https://via.placeholder.com/150",
        "id": artist["id"]  # ✅ Aquí lo añadimos
    }
    for artist in data.get("items", [])
]


#Devuelve las top canciones escuchadss del usuario, se puede establecer el limite de canciones a mostrar y el tiempo que quieras recoger los datos
@app.get("/top_tracks/{acs_tkn}")
def get_top_tracks(
    acs_tkn,
    time_range: str = Query("long_term", enum=["short_term", "medium_term", "long_term"]),
    limit: int = Query(10, ge=1, le=50),
):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    url = f"{URL_BASE}/me/top/tracks?time_range={time_range}&limit={limit}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()
    tracks = []

    for track in data.get("items", []):
        generos = set()

        # Obtener los géneros de cada artista del track
        for artist in track["artists"]:
            artist_id = artist["id"]
            artist_url = f"{URL_BASE}/artists/{artist_id}"
            artist_res = requests.get(artist_url, headers=headers)
            if artist_res.status_code == 200:
                artist_data = artist_res.json()
                for genero in artist_data.get("genres", []):
                    generos.add(genero)

        tracks.append({
            "titulo": track["name"],
            "artistas": [artist["name"] for artist in track["artists"]],
            "album": track["album"]["name"],
            "imagen": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "id": track["id"],
            "generos": list(generos)  # ✅ Añadido para el filtro en Angular
        })

    return tracks


#Devuelve las canciones recientemente reproducidas, se puede establecer el límite de canciones que se pueden mostrar
@app.get("/recent_tracks/{acs_tkn}")
def get_recent_tracks(acs_tkn, limit: int = Query(10, ge=1, le=50)):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    url = f"{URL_BASE}/me/player/recently-played?limit={limit}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()
    tracks = []

    for item in data.get("items", []):
        track = item["track"]
        tracks.append({
            "titulo": track["name"],
            "artistas": [artist["name"] for artist in track["artists"]],
            "album": track["album"]["name"],
            "imagen": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "reproducido_en": item["played_at"],
            "id": track["id"]
        })

    return tracks

#############GETS RECOMENDACIONES#############

#Devuelve 10 canciones recomendadas en base a una cancion
@app.get("/recommend_tracks/{acs_tkn}/{track_id}")
def recommend_tracks(acs_tkn: str, track_id: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    params = {
        "seed_tracks": track_id,
        "limit": 10
    }

    res = requests.get(f"{URL_BASE}/recommendations", headers=headers, params=params)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="No se pudieron obtener recomendaciones")

    data = res.json()
    return [
        {
            "nombre": track["name"],
            "artistas": [artist["name"] for artist in track["artists"]],
            "id": track["id"],
            "imagen": track["album"]["images"][0]["url"] if track["album"].get("images") else None
        }
        for track in data.get("tracks", [])
    ]
#Devuelve 10 artistas basados en un artista
@app.get("/recommend_artists/{acs_tkn}/{artist_id}")
def recommend_artists(acs_tkn: str, artist_id: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    params = {
        "seed_artists": artist_id,
        "limit": 20  # Se devuelven 20 canciones para filtrar artistas únicos
    }

    res = requests.get(f"{URL_BASE}/recommendations", headers=headers, params=params)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="No se pudieron obtener recomendaciones")

    data = res.json()
    seen = set()
    unique_artists = []

    for track in data.get("tracks", []):
        for artist in track["artists"]:
            if artist["id"] not in seen:
                seen.add(artist["id"])
                unique_artists.append({
                    "nombre": artist["name"],
                    "id": artist["id"],
                    "uri": artist["uri"]
                })
            if len(unique_artists) == 10:
                break
        if len(unique_artists) == 10:
            break

    return unique_artists

def map_to_familia(genero):
    for familia, keywords in GENERO_FAMILIAS.items():
        if genero.lower() in keywords:
            return familia
    return None  # Si no encaja, se ignora

@app.get("/recommend_artists_custom")
def recommend_artists_custom(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener artistas top del usuario
    res_artists = requests.get(f"{URL_BASE}/me/top/artists?limit=15", headers=headers)
    if res_artists.status_code != 200:
        raise HTTPException(status_code=res_artists.status_code, detail="No se pudieron obtener los artistas top")

    top_artists_data = res_artists.json().get("items", [])
    top_artist_ids = {a["id"] for a in top_artists_data}

    # Contar familias de géneros
    contador_familias = Counter()
    for artist in top_artists_data:
        for g in artist.get("genres", []):
            familia = map_to_familia(g)
            if familia:
                contador_familias[familia] += 1

    if not contador_familias:
        raise HTTPException(status_code=204, detail="No se encontraron familias de géneros válidas")

    # Escoger las 3 familias más comunes
    familias_preferidas = [f for f, _ in contador_familias.most_common(3)]

    recomendaciones = []
    vistos = set()

    for familia in familias_preferidas:
        for genero in GENERO_FAMILIAS[familia]:
            search_url = f"https://api.spotify.com/v1/search"
            params = {
                "q": f"genre:{genero}",
                "type": "artist",
                "limit": 15
            }
            res = requests.get(search_url, headers=headers, params=params)
            if res.status_code != 200:
                continue

            for artist in res.json().get("artists", {}).get("items", []):
                if artist["id"] in top_artist_ids or artist["id"] in vistos:
                    continue
                vistos.add(artist["id"])
                recomendaciones.append({
                    "nombre": artist["name"],
                    "id": artist["id"],
                    "imagen": artist["images"][0]["url"] if artist.get("images") else None,
                    "generos": artist.get("genres", [])
                })
                if len(recomendaciones) >= 10:
                    break
            if len(recomendaciones) >= 10:
                break
        if len(recomendaciones) >= 10:
            break

    if not recomendaciones:
        raise HTTPException(status_code=204, detail="No se encontraron artistas nuevos")

    return recomendaciones

@app.get("/recommend_custom")
def recommend_custom(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    headers = {"Authorization": f"Bearer {token}"}

    # 🔁 Paso 1: obtener top tracks de los 3 periodos
    all_tracks = []
    seen_ids = set()
    for time_range in ["short_term", "medium_term", "long_term"]:
        res = requests.get(
            f"{URL_BASE}/me/top/tracks?limit=50&time_range={time_range}", headers=headers
        )
        if res.status_code == 200:
            items = res.json().get("items", [])
            for track in items:
                if track["id"] not in seen_ids:
                    all_tracks.append(track)
                    seen_ids.add(track["id"])

    if not all_tracks:
        return {
            "mensaje": "No se encontraron canciones top en ningún periodo.",
            "recomendaciones": [],
        }

    # 🧠 Paso 2: detectar géneros de artistas (optimizando peticiones en lotes)
    artist_ids = {
        artist["id"]
        for track in all_tracks
        for artist in track.get("artists", [])
    }

    def obtener_generos_por_familia(artist_ids, headers):
        contador_familias = Counter()
        artist_ids = list(artist_ids)

        for i in range(0, len(artist_ids), 50):
            ids_lote = artist_ids[i:i+50]
            res = requests.get(
                f"{URL_BASE}/artists",
                headers=headers,
                params={"ids": ",".join(ids_lote)}
            )
            if res.status_code != 200:
                continue

            for artist_data in res.json().get("artists", []):
                for g in artist_data.get("genres", []):
                    familia = map_to_familia(g)
                    if familia:
                        contador_familias[familia] += 1

        return contador_familias

    contador_familias = obtener_generos_por_familia(artist_ids, headers)

    if not contador_familias:
        return {
            "mensaje": "No se encontraron géneros útiles en los artistas analizados.",
            "recomendaciones": [],
        }

    familias_preferidas = [f for f, _ in contador_familias.most_common(3)]

    # 🔍 Paso 3: buscar canciones por esos géneros
    recomendaciones = []
    vistos = set()

    for familia in familias_preferidas:
        for genero in GENERO_FAMILIAS.get(familia, []):
            params = {"q": f"genre:{genero}", "type": "track", "limit": 15}
            res = requests.get(f"{URL_BASE}/search", headers=headers, params=params)
            if res.status_code != 200:
                continue
            for track in res.json().get("tracks", {}).get("items", []):
                if track["id"] in vistos:
                    continue
                vistos.add(track["id"])
                recomendaciones.append(
                    {
                        "titulo": track["name"],
                        "artistas": [a["name"] for a in track["artists"]],
                        "imagen": (
                            track["album"]["images"][0]["url"]
                            if track["album"].get("images")
                            else None
                        ),
                        "id": track["id"],
                    }
                )
                if len(recomendaciones) >= 10:
                    break
            if len(recomendaciones) >= 10:
                break
        if len(recomendaciones) >= 10:
            break

    return {
        "mensaje": f"Se encontraron {len(recomendaciones)} canciones nuevas",
        "recomendaciones": recomendaciones,
    }


@app.get("/artist_info/{acs_tkn}/{artist_id}")
def get_artist_info(acs_tkn: str, artist_id: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    url = f"{URL_BASE}/artists/{artist_id}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="No se pudo obtener información del artista")

    data = res.json()
    return {
        "nombre": data.get("name"),
        "imagen": data["images"][0]["url"] if data.get("images") else None,
        "generos": data.get("genres", []),
        "seguidores": data.get("followers", {}).get("total"),
        "popularidad": data.get("popularity"),
        "spotify_url": data.get("external_urls", {}).get("spotify")
    }

@app.get("/track_info/{acs_tkn}/{track_id}")
def get_track_info(acs_tkn: str, track_id: str):
    headers = {"Authorization": f"Bearer {acs_tkn}"}
    url = f"{URL_BASE}/tracks/{track_id}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="No se pudo obtener información de la canción")

    data = res.json()
    return {
        "name": data.get("name"),
        "images": data["album"]["images"],
        "album": {
            "name": data["album"]["name"],
        },
        "artists": data.get("artists"),
        "duration_ms": data.get("duration_ms"),
        "popularity": data.get("popularity"),
        "external_urls": data.get("external_urls"),
        "preview_url": data.get("preview_url")
    }

def calcular_wrap_stats(time_range: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}

    top_res = requests.get(
        f"{URL_BASE}/me/top/tracks?limit=50&time_range={time_range}", headers=headers
    )
    recent_res = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=50", headers=headers
    )

    if top_res.status_code != 200 or recent_res.status_code != 200:
        raise HTTPException(status_code=400, detail="No se pudieron obtener canciones")

    top_tracks = top_res.json().get("items", [])
    recent_items = recent_res.json().get("items", [])
    recent_tracks = [item["track"] for item in recent_items if "track" in item]

    all_tracks = top_tracks + recent_tracks
    total_duracion_ms = sum(track.get("duration_ms", 0) for track in all_tracks)

    artist_ids = {
        artist["id"] for track in all_tracks for artist in track.get("artists", [])
    }

    generos_contador = Counter()
    for artist_id in artist_ids:
        res = requests.get(f"{URL_BASE}/artists/{artist_id}", headers=headers)
        if res.status_code == 200:
            for genero in res.json().get("genres", []):
                generos_contador[genero.lower()] += 1

    total_generos = sum(generos_contador.values()) or 1
    generos = [
        {"nombre": g, "porcentaje": round((c / total_generos) * 100)}
        for g, c in generos_contador.most_common(10)
    ]

    return {
        "tiempo_escuchado_min": round(total_duracion_ms / 60000),
        "generos": generos,
    }


@app.get("/wrap_stats_long")
def get_wrap_stats_long(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return calcular_wrap_stats("long_term", token)


@app.get("/wrap_stats_medium")
def get_wrap_stats_medium(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return calcular_wrap_stats("medium_term", token)


@app.get("/wrap_stats_short")
def get_wrap_stats_short(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return calcular_wrap_stats("short_term", token)

#############MAIN#############

def main():
   uvicorn.run(app, host="localhost", port=8888)

if __name__ == "__main__":
    main()