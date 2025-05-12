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
  filteredArtists: any[] = [];
  searchTerm: string = '';

  ngOnInit(): void {
    this.spotifyService.getTopArtists().subscribe({
      next: (res) => {
        console.log('Artistas recibidos:', res); // 👈 verificación en consola
        this.topArtists = res;
        this.filteredArtists = res;
      },
      error: (err) => {
        console.error('Error al obtener artistas:', err);
        this.topArtists = [];
        this.filteredArtists = [];
      }
    });
  }

  onSearch(): void {
    const term = this.searchTerm.toLowerCase();
    this.filteredArtists = this.topArtists.filter(artist =>
      artist.name.toLowerCase().includes(term)
    );
  }
}
