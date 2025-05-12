import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-canciones',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './canciones.component.html',
  styleUrls: ['./canciones.component.css']
})
export class CancionesComponent implements OnInit {
  private spotifyService = inject(SpotifyService);

  topTracks: any[] = [];
  ngOnInit(): void {
    this.spotifyService.getTopTracks().subscribe({
      next: (res) => {
        console.log('Canciones recibidas:', res);  // 👈 debug en consola
        this.topTracks = res;
      },
      error: (err) => {
        console.error('Error al obtener canciones:', err);
        this.topTracks = [];
      }
    });
  }
}
