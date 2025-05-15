import { Component, inject, OnInit } from '@angular/core';
import { SpotifyService } from '../../services/spotify.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-perfil',
  imports: [CommonModule],
  templateUrl: './perfil.component.html',
  styleUrl: './perfil.component.css'
})
export class PerfilComponent implements OnInit {
  private spotifyService = inject(SpotifyService);

  nombre: string = '';
  foto: string = '';

  ngOnInit(): void {
    this.spotifyService.getUserName().subscribe({
    next: (res) => {
      console.log('Nombre:', res.nombre);
      this.nombre = res.nombre;
    },
    error: () => {
      this.nombre = 'Desconocido';
    }
  });
    this.spotifyService.getUserPic().subscribe({
      next: (res) => {
        console.log('Imagen de perfil:', res.url);
        this.foto = res.url;
      },
      error: () => {
        this.foto = 'https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png';
      }
    });

  }

}
