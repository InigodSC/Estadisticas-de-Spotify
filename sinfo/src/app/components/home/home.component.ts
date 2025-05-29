import { Component, OnInit, inject } from "@angular/core";
import { Router, RouterModule } from "@angular/router";
import { SpotifyService } from "../../services/spotify.service";
import { CommonModule, isPlatformBrowser } from "@angular/common";
import { PLATFORM_ID } from "@angular/core";
import { MenuComponent } from "../menu/menu.component";
import { OpcionesUsuarioComponent } from "../opciones-usuario/opciones-usuario.component";
import { InfoModalComponent } from "../info-modal/info-modal.component";
import { HttpClient, HttpClientModule } from "@angular/common/http";

@Component({
  selector: "app-home",
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MenuComponent,
    OpcionesUsuarioComponent,
    InfoModalComponent,
  ],
  templateUrl: "./home.component.html",
  styleUrls: ["./home.component.css"],
})
export class HomeComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);
  private http = inject(HttpClient);

  selectedItem: any = null;
  selectedType: "song" | "artist" = "song";
  showModal = false;

  mostrarMenu = false;
  mostrarOpciones = false;
  cancionesPersonalizadas: any[] = [];

  nombre: string = "Invitado";
  foto: string = "";
  cancionesRecientes: any[] = [];
  cancionesRecomendadas: any[] = [];
  artistasRecomendados: any[] = [];
  haySesion = false;
  token: string = "";

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem("access_token");
    if (token) {
      this.token = token;
      this.haySesion = true;

      this.spotifyService.getUserName(token).subscribe({
        next: (res) => (this.nombre = res.nombre),
        error: () => (this.nombre = "Invitado"),
      });

      this.spotifyService.getUserPic(token).subscribe({
        next: (res) => (this.foto = res.url),
        error: () => (this.foto = ""),
      });

      this.spotifyService.getRecentTracks(token, 10).subscribe({
        next: (res) => (this.cancionesRecientes = res),
        error: () => (this.cancionesRecientes = []),
      });

      this.spotifyService.getCustomRecommendations(token).subscribe({
        next: (res) => {
          this.cancionesPersonalizadas = res;
        },
        error: (err) => {
          this.cancionesPersonalizadas = [];
        },
      });

      this.spotifyService.getCustomArtistRecommendations(token).subscribe({
        next: (res) => {
          this.artistasRecomendados = res;
        },
        error: (err) => {
          this.artistasRecomendados = [];
        },
      });
    } else {
      this.haySesion = false;
      this.nombre = "Invitado";
      this.foto = "";
    }
  }

  despligueMenu(): void {
    this.mostrarMenu = !this.mostrarMenu;
  }

  alternarOpciones(): void {
    if (this.haySesion) {
      this.mostrarOpciones = !this.mostrarOpciones;
    } else {
      this.irALogin();
    }
  }

  irALogin(): void {
    this.router.navigate(["/login"]);
  }

  openModal(item: any, type: "song" | "artist") {
    const token = this.token;

    if (type === "artist") {
      this.spotifyService.getArtistInfo(token, item.id).subscribe({
        next: (res) => {
          this.selectedItem = {
            name: res.nombre,
            images: res.imagen ? [{ url: res.imagen }] : [],
            genres: res.generos,
            followers: { total: res.seguidores },
            popularity: res.popularidad,
            external_urls: { spotify: res.spotify_url },
          };
          this.selectedType = "artist";
          this.showModal = true;
        },
        error: (err) =>
          console.error("Error al obtener información del artista:", err),
      });
    } else if (type === "song") {
      this.spotifyService.getTrackInfo(token, item.id).subscribe({
        next: (res) => {
          this.selectedItem = {
            name: res.name,
            images: res.images || [],
            album: { name: res.album?.name || "No disponible" },
            artists: res.artists?.map((a: any) => a.name),
            duration_ms: res.duration_ms,
            popularity: res.popularity,
            external_urls: { spotify: res.external_urls?.spotify },
            preview_url: res.preview_url
          };
          this.selectedType = "song";
          this.showModal = true;
        },
        error: (err) =>
          console.error("Error al obtener información de la canción:", err),
      });
    }
  }
}
