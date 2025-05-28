import { Component, OnInit, inject } from "@angular/core";
import { Router, RouterModule } from "@angular/router";
import { SpotifyService } from "../../services/spotify.service";
import { CommonModule, isPlatformBrowser } from "@angular/common";
import { PLATFORM_ID } from "@angular/core";
import { MenuComponent } from "../menu/menu.component";
import { OpcionesUsuarioComponent } from "../opciones-usuario/opciones-usuario.component";

@Component({
  selector: "app-home",
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MenuComponent,
    OpcionesUsuarioComponent,
  ],
  templateUrl: "./home.component.html",
  styleUrls: ["./home.component.css"],
})
export class HomeComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  mostrarMenu = false;
  mostrarOpciones = false;
  cancionesPersonalizadas: any[] = [];

  nombre: string = "Invitado";
  foto: string = "";
  cancionesRecientes: any[] = [];
  cancionesRecomendadas: any[] = [];
  artistasRecomendados: any[] = [];
  haySesion = false;

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem("access_token");
    if (token) {
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
      console.log("🧪 Token usado en smartRecommendations:", token);
      this.spotifyService.getCustomRecommendations(token).subscribe({
        next: (res) => {
          this.cancionesPersonalizadas = res;
          console.log("🎯 Recomendaciones personalizadas recibidas:", res);
        },
        error: (err) => {
          if (err.status === 204) {
            console.warn("⚠️ No se encontraron recomendaciones personalizadas");
          } else {
            console.error(
              "❌ Error al obtener recomendaciones personalizadas:",
              err
            );
          }
          this.cancionesPersonalizadas = [];
        },
      });
      this.spotifyService.getCustomArtistRecommendations(token).subscribe({
        next: (res) => {
          this.artistasRecomendados = res;
          console.log("🎤 Artistas personalizados recomendados:", res);
        },
        error: (err) => {
          if (err.status === 204) {
            console.warn("⚠️ No se encontraron artistas personalizados");
          } else {
            console.error("❌ Error al obtener artistas personalizados:", err);
          }
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
}
