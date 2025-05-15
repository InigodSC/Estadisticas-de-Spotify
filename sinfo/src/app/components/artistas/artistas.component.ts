import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-artistas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './artistas.component.html',
  styleUrls: ['./artistas.component.css']
})
export class ArtistasComponent implements OnInit {
  private spotifyService = inject(SpotifyService);

  topArtists: any[] = [];
  filtrados: any[] = [];
  nombre: string = '';

  ngOnInit(): void {
    this.spotifyService.getTopArtists().subscribe({
      next: (res) => {
        console.log('Artistas recibidos:', res);
        this.topArtists = res;
        this.filtrados = res;
      },
      error: (err) => {
        console.error('Error al obtener artistas:', err);
        this.topArtists = [];
        this.filtrados = [];
      }
    });
  }

  onSearch(): void {
    const term = this.nombre.toLowerCase();
    this.filtrados = this.topArtists.filter(artist =>
      artist.nombre.toLowerCase().includes(term)
    );
  }
}
