import { Component, OnInit, inject } from '@angular/core';
import { SpotifyService } from '../../services/spotify.service';
import { Router } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-canciones',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './canciones.component.html',
  styleUrls: ['./canciones.component.css']
})
export class CancionesComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  topCanciones: any[] = [];
  cancionesFiltradas: any[] = [];

  nombreFiltro: string = '';
  generoFiltro: string = '';
  generosDisponibles: string[] = [];

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getTopTracks(token, 20).subscribe({
      next: (res) => {
        this.topCanciones = res;
        this.cancionesFiltradas = res;

        // Extraer géneros si están disponibles
        const generos = new Set<string>();
        res.forEach((song: { generos: string[]; }) => {
          if (song.generos) {
            song.generos.forEach((g: string) => generos.add(g));
          }
        });
        this.generosDisponibles = Array.from(generos);
      },
      error: () => {
        this.topCanciones = [];
        this.cancionesFiltradas = [];
      }
    });
  }

  filtrarCanciones(): void {
    const nombre = this.nombreFiltro.toLowerCase();
    const genero = this.generoFiltro.toLowerCase();

    this.cancionesFiltradas = this.topCanciones.filter(song => {
      const coincideNombre = song.titulo.toLowerCase().includes(nombre);
      const coincideGenero = !genero || (song.generos && song.generos.some((g: string) => g.toLowerCase().includes(genero)));
      return coincideNombre && coincideGenero;
    });
  }
}