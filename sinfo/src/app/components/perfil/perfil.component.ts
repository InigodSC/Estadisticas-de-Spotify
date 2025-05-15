import { Component, OnInit, inject } from '@angular/core';
import { SpotifyService } from '../../services/spotify.service';
import { Router } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css']
})
export class PerfilComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  nombre: string = '';
  foto: string = '';

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getUserName(token).subscribe({
      next: (res) => this.nombre = res.nombre,
      error: () => this.nombre = 'Desconocido'
    });

    this.spotifyService.getUserPic(token).subscribe({
      next: (res) => this.foto = res.url,
      error: () => this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'
    });
  }

  cerrarSesion(): void {
    localStorage.removeItem('access_token');
    this.router.navigate(['/login']);
  }
}
