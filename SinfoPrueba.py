import requests
import base64
import urllib.parse
import webbrowser
import http.server
import threading
import tkinter as tk
from tkinter import scrolledtext

client_id = '10975615f3b34ac09a9c8c9a1d64642a'
client_secret = 'c2cfab340b9a4a82a436f1ac90d1fafa'
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-top-read user-read-recently-played'

auth_code = None

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

def start_server():
    server = http.server.HTTPServer(('localhost', 8888), AuthHandler)
    server.handle_request()

threading.Thread(target=start_server, daemon=True).start()

# Abrimos navegador para autorización de cliente
params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope,
}
url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
webbrowser.open(url)

print("Esperando autenticación...")
while auth_code is None:
    pass

# Obtener token
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
access_token = response.json()['access_token']

headers = {"Authorization": f"Bearer {access_token}"}

# Obtener los datos mandando las peticiones al servidor
def obtener_datos():
    texto = ""

    texto += "Tus 10 canciones más escuchadas (largo plazo):\n"
    url = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10"
    res = requests.get(url, headers=headers).json()
    for i, track in enumerate(res.get("items", []), start=1):
        artists = ", ".join([a["name"] for a in track["artists"]])
        texto += f"{i}. {track['name']} - {artists}\n"

    texto += "\nTus 10 artistas más escuchados:\n"
    url = "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10"
    res = requests.get(url, headers=headers).json()
    for i, artist in enumerate(res.get("items", []), start=1):
        texto += f"{i}. {artist['name']}\n"

    texto += "\nTus 10 canciones reproducidas recientemente:\n"
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=10"
    res = requests.get(url, headers=headers).json()
    for i, item in enumerate(res.get("items", []), start=1):
        track = item["track"]
        artists = ", ".join([a["name"] for a in track["artists"]])
        texto += f"{i}. {track['name']} - {artists}\n"

    return texto

# Mostrar en una ventana con Tkinter
def mostrar_en_ventana(texto):
    root = tk.Tk()
    root.title("Spotify - Estadísticas")
    root.geometry("600x600")
    root.configure(bg="#121212")  

    font_style = ("Helvetica", 12)
    
    texto_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=font_style, bg="#121212", fg="white", insertbackground="white")
    texto_area.insert(tk.END, texto)
    texto_area.pack(expand=True, fill='both', padx=20, pady=20)
    texto_area.configure(state='disabled')

    separator = tk.Frame(root, height=2, bg="white")
    separator.pack(fill=tk.X, padx=20)

    close_button = tk.Button(root, text="Cerrar", bg="#1DB954", fg="white", font=("Helvetica", 12), command=root.quit)
    close_button.pack(pady=20)

    root.mainloop()

# Ejecuta y muestra los datos sobre la ventana Tkinter
datos = obtener_datos()
mostrar_en_ventana(datos)
