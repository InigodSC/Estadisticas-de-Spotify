import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
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

  showMenu = false;
  showUserOptions = false;

  nombre: string = '';
  foto: string = '';

  despligueMenu (): void {
    this.showMenu = !this.showMenu;
  }

  toggleUserOptions(): void {
    this.showUserOptions = !this.showUserOptions;
  }
  ngOnInit(): void {
    this.spotifyService.getUserPic().subscribe({
      next: (res) => {
        console.log('Imagen de perfil:', res.url);
        this.foto = res.url;
      },
      error: () => {
        this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png';
      }
    });
    this.spotifyService.getUserName().subscribe({
      next:(res)=>{
        console.log('Nombre de usuario: ',res.nombre);
        this.nombre = res.nombre;
      },
      error:()=>{
        this.nombre='Usuario';
      }
    })

  }
}
