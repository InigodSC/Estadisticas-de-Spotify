import fastapi
import datetime as dt
import uvicorn
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
import requests

app = fastapi.FastAPI()

URL_BASE = "https://api.spotify.com/v1"

@app.get("/usr_name")
def getUsrName(token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{URL_BASE}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="No se ha podido obtener la informacion del perfil del usuario")

    data = response.json()
    return {
        "nombre": data.get("display_name")
    }
    

@app.get("/top_artistas_corto_ini")
def getTopArtistasIni(token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{URL_BASE}/me/top/artists?time_range=short_term&limit=5", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()
    artistas = [artist["name"] for artist in data.get("items", [])]

    return {"top_artistas_corto": artistas}


@app.get("/top_artistas_ini_corto")
def getTopCancionesIniCorto(token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{URL_BASE}/me/top/tracks?time_range=short_term&limit=5", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()
    canciones = [{"titulo": track["name"]} for track in data.get("items", [])]

    return {"top_canciones_corto": canciones}


@app.get("/top_artistas_ini_largo")
def getTopCancionesIniLargo(token: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{URL_BASE}/me/top/tracks?time_range=long_term&limit=5", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    data = response.json()
    canciones = [{"titulo": track["name"]} for track in data.get("items", [])]

    return {"top_canciones_largo": canciones}

def main():
   uvicorn.run(app, host="localhost", port=1224)




if __name__ == "__main__":
    main()