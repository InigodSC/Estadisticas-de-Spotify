import fastapi
import datetime as dt
import uvicorn
from fastapi import Request, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests, base64, urllib.parse

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
SCOPE = "user-top-read user-read-recently-played user-read-private"
URL_BASE = "https://api.spotify.com/v1"

access_token = None

#Que el usuario haga login 
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
    return HTMLResponse("<h2>Autenticación completada correctamente. Ya puedes usar la API.</h2>")


#Devuelve el token de acceso
@app.get("/token")
def get_token():
    if not access_token:
        raise HTTPException(status_code=401, detail="No estás autenticado todavía")
    return {"access_token": access_token}

#Comprueba si esta autenticado
def auth_headers():
    if not access_token:
        raise HTTPException(status_code=401, detail="No estás autenticado todavía")
    return {"Authorization": f"Bearer {access_token}"}


#Devuelve el nombre de usuario
@app.get("/usr_name")
def getUsrName():
    headers = auth_headers()
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la informacion del perfil del usuario")

    data = response.json()
    return {
        "nombre": data.get("display_name"),
    }

#Devuelve la foto de perfil del usuario
@app.get("/usr_pic")
def getUsrPic():
    headers = auth_headers()
    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la informacion del perfil del usuario")

    data = response.json()
    
    images = data.get("images")
    
    if images and len(images) > 0 and images[0].get("url"):
        return RedirectResponse(url=images[0]["url"])
    else:
        return RedirectResponse(url="https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png")

#Devuelve los top artistas escuchados del usuario, se puede establecer el limite de artistas a mostrar y el tiempo que quieras recoger los datos
@app.get("/top_artists")
def get_top_artists(
    time_range: str = Query("medium_term", enum=["short_term", "medium_term", "long_term"]),
    limit: int = Query(..., gt=0, le=50, description="Número de artistas a mostrar (entre 1 y 50)")
):
    headers = auth_headers()
    url = f"{URL_BASE}/me/top/artists?time_range={time_range}&limit={limit}" 
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()
    return [
        {"nombre": artist["name"], "generos": artist["genres"], "imagen": artist["images"][0]["url"] if artist.get("images") else "https://via.placeholder.com/150"}
        for artist in data.get("items", [])
    ]

#Devuelve las top canciones escuchadss del usuario, se puede establecer el limite de canciones a mostrar y el tiempo que quieras recoger los datos
@app.get("/top_tracks")
def get_top_tracks(
    time_range: str = Query("medium_term", enum=["short_term", "medium_term", "long_term"]),
    limit: int = Query(10, ge=1, le=50)
):
    headers = auth_headers()
    url = f"{URL_BASE}/me/top/tracks?time_range={time_range}&limit={limit}"
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.json())

    data = res.json()
    return [
        {
            "titulo": track["name"],
            "artistas": [artist["name"] for artist in track["artists"]],
            "album": track["album"]["name"],
            "imagen": track["album"]["images"][0]["url"] if track["album"]["images"] else None
        }
        for track in data.get("items", [])
    ]

#Devuelve las canciones recientemente reproducidas, se puede establecer el límite de canciones que se pueden mostrar
@app.get("/recent_tracks")
def get_recent_tracks(limit: int = Query(10, ge=1, le=50)):
    headers = auth_headers()
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

def main():
   uvicorn.run(app, host="localhost", port=8888)


if __name__ == "__main__":
    main()
