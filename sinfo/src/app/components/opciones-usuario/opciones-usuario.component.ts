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

  @Output() closeOptions = new EventEmitter<void>();

  constructor(private router: Router) {}

  goToProfile(): void {
    this.router.navigate(['/perfil']);
    this.closeOptions.emit();
  }

  logout(): void {
    window.location.href = 'http://localhost:8000/login'; // tu backend para reautenticación
  }
}
