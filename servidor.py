import fastapi
import datetime as dt
import uvicorn
from fastapi import Request, HTTPException, Query, Header
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests, base64, urllib.parse
import webbrowser


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "reproducido_en": item["played_at"]
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

@app.get("/recommend_tracks_smart")
def recommend_tracks_smart(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    headers = {"Authorization": f"Bearer {token}"}
    URL_BASE = "https://api.spotify.com/v1"

    # Paso 1: Obtener géneros válidos desde Spotify
    genre_res = requests.get(f"{URL_BASE}/recommendations/available-genre-seeds", headers=headers)
    if genre_res.status_code != 200:
        print("❌ Error al obtener géneros disponibles")
        raise HTTPException(status_code=genre_res.status_code, detail="No se pudieron obtener los géneros disponibles")

    available_genres = [g.lower() for g in genre_res.json().get("genres", [])]
    print("✅ Géneros disponibles (Spotify):", available_genres)

    # Paso 2: Obtener top tracks del usuario
    top_tracks_res = requests.get(f"{URL_BASE}/me/top/tracks?limit=20", headers=headers)
    if top_tracks_res.status_code != 200:
        print("❌ Error al obtener top tracks:", top_tracks_res.status_code)
        raise HTTPException(status_code=top_tracks_res.status_code, detail="No se pudieron obtener las canciones top del usuario")

    found_genres = set()

    for track in top_tracks_res.json().get("items", []):
        for artist in track.get("artists", []):
            artist_id = artist.get("id")
            if artist_id:
                artist_res = requests.get(f"{URL_BASE}/artists/{artist_id}", headers=headers)
                if artist_res.status_code == 200:
                    artist_data = artist_res.json()
                    for g in artist_data.get("genres", []):
                        g_lower = g.lower()
                        if g_lower in available_genres:
                            found_genres.add(g_lower)
                            if len(found_genres) >= 5:
                                break
        if len(found_genres) >= 5:
            break

    print("🎯 Géneros encontrados en tus canciones:", found_genres)

    if not found_genres:
        raise HTTPException(status_code=204, detail="No hay géneros válidos encontrados en tus canciones top")

    # Paso 3: Solicitar recomendaciones basadas en los géneros encontrados
    rec_params = {
        "seed_genres": ",".join(list(found_genres)[:5]),
        "limit": 15
    }
    print("📤 Solicitando recomendaciones con géneros:", rec_params["seed_genres"])

    rec_res = requests.get(f"{URL_BASE}/recommendations", headers=headers, params=rec_params)

    if rec_res.status_code != 200:
        print("❌ Error al obtener recomendaciones:", rec_res.status_code)
        print("🧾 Respuesta completa:", rec_res.text)
        raise HTTPException(status_code=rec_res.status_code, detail="Error al obtener recomendaciones")

    data = rec_res.json()

    recomendaciones = [
        {
            "nombre": track["name"],
            "artistas": [a["name"] for a in track["artists"]],
            "imagen": track["album"]["images"][0]["url"] if track["album"].get("images") else None,
            "id": track["id"]
        }
        for track in data.get("tracks", [])
    ]

    print(f"✅ {len(recomendaciones)} canciones recomendadas encontradas.")
    return recomendaciones


#############MAIN#############

def main():
   uvicorn.run(app, host="localhost", port=8888)

if __name__ == "__main__":
    main()
