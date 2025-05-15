import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-opciones-usuario',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './opciones-usuario.component.html',
  styleUrls: ['./opciones-usuario.component.css']
})
export class OpcionesUsuarioComponent {

  @Output() cerrarOpciones = new EventEmitter<void>();

  constructor(private router: Router) {}

  irAlPerfil(): void {
    this.router.navigate(['/perfil']);
    this.cerrarOpciones.emit();
  }

  cerrarSesion(): void {
  localStorage.removeItem('access_token');
  this.router.navigate(['/login']);
}
}
