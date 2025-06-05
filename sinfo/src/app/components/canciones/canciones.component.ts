import { Component, OnInit, inject } from "@angular/core";
import { SpotifyService } from "../../services/spotify.service";
import { Router } from "@angular/router";
import { CommonModule, isPlatformBrowser } from "@angular/common";
import { PLATFORM_ID } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { HttpClient } from "@angular/common/http";
import { InfoModalComponent } from "../info-modal/info-modal.component";

@Component({
  selector: "app-canciones",
  standalone: true,
  imports: [CommonModule, FormsModule, InfoModalComponent],
  templateUrl: "./canciones.component.html",
  styleUrls: ["./canciones.component.css"],
})
export class CancionesComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  private http = inject(HttpClient);
  private token = localStorage.getItem("access_token");

  selectedItem: any = null;
  selectedType: "song" = "song";
  showModal = false;

  topCanciones: any[] = [];
  cancionesFiltradas: any[] = [];
  paginadas: any[] = [];
  periodo: string = "long_term";

  nombreFiltro: string = "";
  generoFiltro: string = "";
  generosDisponibles: string[] = [];

  paginaActual: number = 1;
  cancionesPorPagina: number = 10;
  totalPaginas: number = 1;

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
      this.router.navigate(["/login"]);
      return;
    }
    this.actualizarCanciones();
  }

  filtrarCanciones(): void {
    const nombre = this.nombreFiltro.toLowerCase();
    const genero = this.generoFiltro.toLowerCase();

    this.cancionesFiltradas = this.topCanciones.filter((song) => {
      const coincideNombre = song.titulo.toLowerCase().includes(nombre);
      const coincideGenero =
        !genero ||
        (song.generos &&
          song.generos.some((g: string) => g.toLowerCase().includes(genero)));
      return coincideNombre && coincideGenero;
    });

    this.paginaActual = 1;
    this.actualizarPaginacion();
  }

  actualizarCanciones(): void {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    this.spotifyService.getTopTracksRange(token, 50, this.periodo).subscribe({
      next: (res) => {
        this.topCanciones = res;

        // ✅ Regenerar los géneros
        const generos = new Set<string>();
        res.forEach((song: any) => {
          if (song.generos) {
            song.generos.forEach((g: string) => generos.add(g));
          }
        });
        this.generosDisponibles = Array.from(generos).sort();

        this.filtrarCanciones(); // Aplica el filtro y la paginación
      },
      error: () => {
        this.topCanciones = [];
        this.cancionesFiltradas = [];
        this.paginadas = [];
        this.generosDisponibles = [];
      },
    });
  }

  actualizarPaginacion(): void {
    this.totalPaginas = Math.ceil(
      this.cancionesFiltradas.length / this.cancionesPorPagina
    );
    const inicio = (this.paginaActual - 1) * this.cancionesPorPagina;
    const fin = inicio + this.cancionesPorPagina;
    this.paginadas = this.cancionesFiltradas.slice(inicio, fin);
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina < 1 || nuevaPagina > this.totalPaginas) return;
    this.paginaActual = nuevaPagina;
    this.actualizarPaginacion();
  }

  volver(): void {
    this.router.navigate(["/home"]);
  }

  openSongModal(song: any) {
    if (!this.token || !song.id) return;

    this.spotifyService.getTrackInfo(this.token, song.id).subscribe({
      next: (res) => {
        this.selectedItem = res;
        this.selectedType = "song";
        this.showModal = true;
      },
      error: (err) => console.error("Error al obtener info de canción:", err),
    });
  }
}
