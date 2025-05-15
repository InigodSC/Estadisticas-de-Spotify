import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { SpotifyService } from '../../services/spotify.service';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';
import { MenuComponent } from '../menu/menu.component';
import { OpcionesUsuarioComponent } from '../opciones-usuario/opciones-usuario.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, MenuComponent, OpcionesUsuarioComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  mostrarMenu = false;
  mostrarOpciones = false;

  nombre: string = '';
  foto: string = '';
  cancionesRecientes: any[] = [];

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.spotifyService.getUserName(token).subscribe({
      next: (res) => this.nombre = res.nombre,
      error: () => this.router.navigate(['/login'])
    });

    this.spotifyService.getUserPic(token).subscribe({
      next: (res) => this.foto = res.url,
      error: () => this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'
    });

    this.spotifyService.getRecentTracks(token,10).subscribe({
      next: (res) => this.cancionesRecientes = res,
      error: () => this.cancionesRecientes = []
    });
  }

  despligueMenu(): void {
    this.mostrarMenu = !this.mostrarMenu;
  }

  alternarOpciones(): void {
    this.mostrarOpciones = !this.mostrarOpciones;
  }
}
