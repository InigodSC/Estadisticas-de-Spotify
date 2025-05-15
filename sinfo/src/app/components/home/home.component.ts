import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MenuComponent } from '../menu/menu.component';
import { OpcionesUsuarioComponent } from '../opciones-usuario/opciones-usuario.component';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, MenuComponent, OpcionesUsuarioComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit{
  private spotifyService = inject(SpotifyService);
  private router = inject(Router);

  mostrarMenu = false;
  mostrarOpciones = false;

  nombre: string = '';
  foto: string = '';
  cancionesRecientes:any[] = []

  despligueMenu (): void {
    this.mostrarMenu = !this.mostrarMenu;
  }

  alternarOpciones(): void {
    this.mostrarOpciones = !this.mostrarOpciones;
  }
  ngOnInit(): void {
    this.spotifyService.getToken().subscribe({
      next: () => {
        console.log('Sesión activa, continuando...');
        this.cargarPerfilYDatos(); // 👈 tu función para nombre, foto, canciones...
      },
      error: () => {
        console.warn('No hay token, redirigiendo a login...');
        this.router.navigate(['/login']);
      }
    });
  }
  cargarPerfilYDatos(): void {
    this.spotifyService.getUserPic().subscribe({
      next: (res) => this.foto = res.url,
      error: () => this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png'
    });

    this.spotifyService.getUserName().subscribe({
      next: (res) => this.nombre = res.nombre,
      error: () => this.nombre = 'Usuario'
    });

    this.spotifyService.getRecentTracks().subscribe({
      next: (res) => this.cancionesRecientes = res,
      error: () => this.cancionesRecientes = []
    });
  }
}
