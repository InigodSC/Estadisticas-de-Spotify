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
  nombre: string = '';

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getTopArtists(token, 20).subscribe({
      next: (res) => {
        this.topArtists = res;
        this.filtrados = res;
      },
      error: () => {
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
