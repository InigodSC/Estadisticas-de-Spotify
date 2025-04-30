import requests
import base64
import urllib.parse
import webbrowser
import http.server
import threading
import json

client_id = '10975615f3b34ac09a9c8c9a1d64642a'
client_secret = 'c2cfab340b9a4a82a436f1ac90d1fafa'
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-top-read user-read-recently-played'

auth_code = None #Codigo de autorizacion al iniciar sesión con Spotify

#Clase para crear un servidor web básico
class AuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if "/callback" in self.path:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            auth_code = params.get('code', [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<h1>Autenticado correctamente. Puedes cerrar esta pestaña.</h1>".encode('utf-8'))


# Arranca el servidor local
def start_server():
    server = http.server.HTTPServer(('localhost', 8888), AuthHandler)
    server.handle_request()

# Construye la URL y abrimos navegador para que el usuario inicie sesión
params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope,
}
url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
threading.Thread(target=start_server, daemon=True).start()
webbrowser.open(url)

# Espera a que el usuario inicie sesión
print("Esperando autenticación...")
while auth_code is None:
    pass

# Intercambiar auth_code por token de acceso
auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri
}
response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
tokens = response.json()
access_token = tokens['access_token']

# Preparar headers para peticiones
headers = {"Authorization": f"Bearer {access_token}"}

# Obtener y mostrar datos
def mostrar_datos():
    print("\nTus 10 canciones más escuchadas (largo plazo):\n")
    url = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10"
    res = requests.get(url, headers=headers).json()
    for i, track in enumerate(res.get("items", []), start=1):
        artists = ", ".join([a["name"] for a in track["artists"]])
        print(f"{i}. {track['name']} - {artists}")

    print("\nTus 10 artistas más escuchados (largo plazo):\n")
    url = "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10"
    res = requests.get(url, headers=headers).json()
    for i, artist in enumerate(res.get("items", []), start=1):
        print(f"{i}. {artist['name']}")

    print("\nTus 10 canciones reproducidas recientemente:\n")
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=10"
    res = requests.get(url, headers=headers).json()
    for i, item in enumerate(res.get("items", []), start=1):
        track = item["track"]
        artists = ", ".join([a["name"] for a in track["artists"]])
        print(f"{i}. {track['name']} - {artists}")

mostrar_datos()
