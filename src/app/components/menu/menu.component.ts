import { Component, EventEmitter, inject, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent {
  private spotifyService = inject(SpotifyService);

  nombre:string='';
  foto:string='';

  @Output() cerrarMenu = new EventEmitter<void>();

  constructor(private router: Router) {}

  goToArtists(): void {
    this.router.navigate(['/artistas']);
    this.cerrarMenu.emit();
  }

  goToSongs(): void {
    this.router.navigate(['/canciones']);
    this.cerrarMenu.emit();
  }

  close(): void {
    this.cerrarMenu.emit();
  }
}
