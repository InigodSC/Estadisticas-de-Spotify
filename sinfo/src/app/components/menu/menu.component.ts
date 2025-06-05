import { Component, EventEmitter, inject, Input, OnInit, Output, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private platformId = inject(PLATFORM_ID);

  nombre: string = '';
  foto: string = '';

  @Input() oculto = false;
  @Output() cerrarMenu = new EventEmitter<void>();

  constructor(private router: Router) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getUserPic(token).subscribe({
      next: res => this.foto = res.url,
      error: () => this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'
    });

    this.spotifyService.getUserName(token).subscribe({
      next: res => this.nombre = res.nombre,
      error: () => this.nombre = 'desconocido'
    });
  }

  goToArtists(): void {
    this.router.navigate(['/artistas']);
    this.cerrarMenu.emit();
  }

  goToSongs(): void {
    this.router.navigate(['/canciones']);
    this.cerrarMenu.emit();
  }

  goToWrap(): void {
    this.router.navigate(['/wrap']);
    this.cerrarMenu.emit();
  }

  close(): void {
    this.cerrarMenu.emit();
  }

  irAlPerfil(): void {
    this.router.navigate(['/perfil']);
  }
}
