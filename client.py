import requests
import base64
import urllib.parse
import webbrowser
import http.server
import threading

# CONFIGURA TU APP DE SPOTIFY
client_id = '10975615f3b34ac09a9c8c9a1d64642a'
client_secret = 'c2cfab340b9a4a82a436f1ac90d1fafa'
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-read-private'

auth_code = None



def solicitar_token():

    global user_headers

    # 1. Servidor para capturar el auth code
    class AuthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            global auth_code
            if "/callback" in self.path:
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                auth_code = params.get('code', [None])[0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write("<h1>Autenticado correctamente. Puedes cerrar esta ventana.</h1>".encode('utf-8'))

    def start_server():
        server = http.server.HTTPServer(('localhost', 8888), AuthHandler)
        server.handle_request()

    # 2. Lanzamos servidor en segundo plano
    threading.Thread(target=start_server, daemon=True).start()

    # 3. Abrimos navegador para autorizar
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    webbrowser.open(auth_url)

    print("Esperando autenticación...")
    while auth_code is None:
        pass

    # 4. Intercambiamos el código por un token
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
    token_response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)

    if token_response.status_code != 200:
        print("Error al obtener token:", token_response.text)
        exit()

    access_token = token_response.json()['access_token']

    # 5. Hacemos petición para obtener el nombre del usuario
    user_headers = {
        'Authorization': f'Bearer {access_token}'
    }

user_info = requests.get("https://api.spotify.com/v1/me", headers=user_headers).json()

print("Nombre de usuario:", user_info.get("display_name", "No disponible"))
