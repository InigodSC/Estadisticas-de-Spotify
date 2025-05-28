import { Component, OnInit, inject } from '@angular/core';
import { SpotifyService } from '../../services/spotify.service';
import { Router } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-artistas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './artistas.component.html',
  styleUrls: ['./artistas.component.css']
})
export class ArtistasComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  topArtists: any[] = [];
  filtrados: any[] = [];
  paginados: any[] = [];
  nombre: string = '';
  generoFiltro: string = '';
  generosDisponibles: string[] = [];

  paginaActual: number = 1;
  artistasPorPagina: number = 10;
  totalPaginas: number = 1;

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getTopArtists(token, 50).subscribe({
      next: (res) => {
        this.topArtists = res;
        this.filtrados = res;
        this.actualizarPaginacion();

        const generos = new Set<string>();
        res.forEach((artist: any) => {
          if (artist.generos) {
            artist.generos.forEach((g: string) => generos.add(g));
          }
        });
        this.generosDisponibles = Array.from(generos);
      },
      error: () => {
        this.topArtists = [];
        this.filtrados = [];
        this.paginados = [];
      }
    });
  }

  onSearch(): void {
    const term = this.nombre.toLowerCase();
    const genero = this.generoFiltro.toLowerCase();

    this.filtrados = this.topArtists.filter(artist =>
      artist.nombre.toLowerCase().includes(term) &&
      (!genero || artist.generos?.some((g: string) => g.toLowerCase().includes(genero)))
    );
    this.paginaActual = 1;
    this.actualizarPaginacion();
  }

  actualizarPaginacion(): void {
    this.totalPaginas = Math.ceil(this.filtrados.length / this.artistasPorPagina);
    const inicio = (this.paginaActual - 1) * this.artistasPorPagina;
    const fin = inicio + this.artistasPorPagina;
    this.paginados = this.filtrados.slice(inicio, fin);
  }

  cambiarPagina(nuevaPagina: number): void {
    if (nuevaPagina < 1 || nuevaPagina > this.totalPaginas) return;
    this.paginaActual = nuevaPagina;
    this.actualizarPaginacion();
  }

  volver(): void {
    this.router.navigate(['/']);
  }
}
